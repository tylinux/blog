# 利用逆向知识修复 『Jietu.app 』在 macOS Big Sur 下的崩溃问题

腾讯开发的截图工具：[Jietu](https://apps.apple.com/us/app/%E6%88%AA%E5%9B%BE-jietu-%E5%BF%AB%E9%80%9F%E6%A0%87%E6%B3%A8-%E4%BE%BF%E6%8D%B7%E5%88%86%E4%BA%AB%E7%9A%84%E6%88%AA%E5%B1%8F%E5%B7%A5%E5%85%B7/id1059334054?mt=12) 一直是我在 macOS 下最喜欢的截图工具，不过在升级到 macOS 11 Big Sur 之后就 GG 了，区域截图的时候会崩溃。这 App 上次更新是在 3 年前，指望腾讯修复希望不大，正好这俩天有空，尝试自己定位解决一下问题。
<!--more-->

## 定位崩溃原因

打开 `Console.app`，过滤 `Jietu` 进程，触发崩溃，日志如下:

```
2020-12-02 19:39:44.956 Jietu[15361:195786] *** Terminating app due to uncaught exception 'NSInvalidArgumentException', reason: 'NSConcreteAttributedString initWithString:: nil value'
*** First throw call stack:
(
0   CoreFoundation                      0x00007fff204936af __exceptionPreprocess + 242
1   libobjc.A.dylib                     0x00007fff201cb3c9 objc_exception_throw + 48
2   Foundation                          0x00007fff211aed5b -[NSRLEArray init] + 0
3   Foundation                          0x00007fff211aeb2f -[NSConcreteAttributedString initWithString:attributes:] + 27
4   JietuFramework                      0x0000000105ef2920 -[JTCaptureSizeInfoSubView drawRect:] + 228
5   ???                                 0x0000000106285613 0x0 + 4398274067
6   AppKit                              0x00007fff234c8709 -[NSView _recursive:displayRectIgnoringOpacity:inContext:stopAtLayerBackedViews:] + 2115
7   AppKit                              0x00007fff234c8a9a -[NSView _recursive:displayRectIgnoringOpacity:inContext:stopAtLayerBackedViews:] + 3028
8   AppKit                              0x00007fff22da0c29 -[NSView(NSLayerKitGlue) _drawViewBackingLayer:inContext:drawingHandler:] + 967
9   QuartzCore                          0x00007fff26bc3051 CABackingStoreUpdate_ + 190
10  QuartzCore                          0x00007fff26c27441 ___ZN2CA5Layer8display_Ev_block_invoke + 53
11  QuartzCore                          0x00007fff26bc25a4 -[CALayer _display] + 2183
12  AppKit                              0x00007fff22da07a1 -[_NSBackingLayer display] + 475
13  AppKit                              0x00007fff22d0b778 -[_NSViewBackingLayer display] + 555
14  QuartzCore                          0x00007fff26bc15b8 _ZN2CA5Layer17display_if_neededEPNS_11TransactionE + 874
15  QuartzCore                          0x00007fff26cfb373 _ZN2CA7Context18commit_transactionEPNS_11TransactionEdPd + 517
16  QuartzCore                          0x00007fff26b9ef91 _ZN2CA11Transaction6commitEv + 783
17  AppKit                              0x00007fff22db59cb __62+[CATransaction(NSCATransaction) NS_setFlushesWithDisplayLink]_block_invoke + 285
18  AppKit                              0x00007fff234ffd0e ___NSRunLoopObserverCreateWithHandler_block_invoke + 41
19  CoreFoundation                      0x00007fff20418d9d __CFRUNLOOP_IS_CALLING_OUT_TO_AN_OBSERVER_CALLBACK_FUNCTION__ + 23
20  CoreFoundation                      0x00007fff20418c2d __CFRunLoopDoObservers + 549
21  CoreFoundation                      0x00007fff204180dd __CFRunLoopRun + 838
22  CoreFoundation                      0x00007fff204176be CFRunLoopRunSpecific + 563
23  HIToolbox                           0x00007fff28683fd0 RunCurrentEventLoopInMode + 292
24  HIToolbox                           0x00007fff28683dcc ReceiveNextEventCommon + 709
25  HIToolbox                           0x00007fff28683aef _BlockUntilNextEventMatchingListInModeWithFilter + 64
26  AppKit                              0x00007fff22c30f85 _DPSNextEvent + 883
27  AppKit                              0x00007fff22c2f74b -[NSApplication(NSEvent) _nextEventMatchingEventMask:untilDate:inMode:dequeue:] + 1366
28  AppKit                              0x00007fff22c21bda -[NSApplication run] + 586
29  AppKit                              0x00007fff22bf5f31 NSApplicationMain + 816
30  libdyld.dylib                       0x00007fff2033c631 start + 1
)
libc++abi.dylib: terminating with uncaught exception of type NSException
```

看日志，崩溃原因很简单，创建 `NSAttributedString` 的时候传入了 `nil`。看堆栈是在 `JietuFramework` 的 `-[JTCaptureSizeInfoSubView drawRect:] + 228` 中调用的。拖到 IDA 中，F5 一下：

![-w859](https://i.loli.net/2020/12/07/HqslQXhJ6DLwCUV.jpg)

崩溃时，伪代码中的 `v5` 为 nil，导致崩溃，而 `v5` 指向的则是 `JTCaptureSizeInfoSubView` 的 `sizeInfoStr` 属性。

在另一台 10.15.7 的 macOS  设备上，通过 `Frida` 打印日志，得知 `sizeInfoStr` 的值是类似 `1920 * 1080` 这样的字符串。简单写个 `Frida` 脚本，判断在 `self.sizeInfoStr` 为 `nil` 是，返回 `1920 * 1080`，测试是否崩溃。脚本如下：

```javascript
if (ObjC.available) {
  console.log('\n[*] Starting Hooking');

  var func = ObjC.classes.JTCaptureSizeInfoSubView['- sizeInfoStr']

  Interceptor.attach(func.implementation, {
    onEnter: function (args) {
    },
    
    onLeave: function (returnValue) {
      var ret = (new ObjC.Object(returnValue)).toString();
      if (ret == 'nil') {
        var newStr = ObjC.classes.NSString.stringWithString_('1920 * 1080');
        returnValue.replace(newStr);
      }
    }
  });
  console.log('\n[*] Starting Intercepting');
} else {
  console.log('Objective-C Runtime is not available!');
}
```

执行 `frida -f /Applications/Jietu.app/Contents/MacOS/Jietu -l ret.js`，测试崩溃解决。

## patch 崩溃

如果要日常使用肯定不能这样 frida 加载个脚本去进行修复，最好是能直接对原本的二进制文件进行修改，傻瓜化修复此问题。因此，我们需要使用二进制 hook 的方法，替换掉有问题的方法实现，解决此崩溃。

在 iOS 越狱设备中，可以很简单的利用 theos 生成基于 `Cydia Substrate` 的 hook 代码，这里我不准备引入这么重的框架，因为出问题的地方是个 OC 方法，可以通过 `method swizzling` 交换方法实现很简单的实现 hook。但，这个代码我也不准备手写，像大家介绍一个只有一个文件的 hook 方案：[CaptainHook](https://github.com/rpetrich/CaptainHook)。它仅有一个头文件，通过宏和 OC runtime 相关特性实现运行时的方法替换。使用 CaptainHook 实现的修复代码如下：

```objectivec
#import "CaptainHook.h"
#import <Foundation/Foundation.h>

// 声明我们准备 hook 的类
CHDeclareClass(JTCaptureSizeInfoSubView);

// 构造一个新的方法, 参数含义依次为: 参数个数, 返回值类型, 类名, 方法名, [参数类型, ...]
CHMethod(0, NSString *, JTCaptureSizeInfoSubView, sizeInfoStr) {
    // 获取原方法返回
    NSString *ret = CHSuper(0, JTCaptureSizeInfoSubView, sizeInfoStr);
    return ret ?: @"1920 * 1080";
}

// 在 runtime 初始化时调换实现
CHConstructor {
    NSLog(@"HOOK Enabled!");
    CHLoadLateClass(JTCaptureSizeInfoSubView);
    CHHook(0, JTCaptureSizeInfoSubView, sizeInfoStr);
}
```

将上述代码保存为 .m 文件，与 `CaptainHook.h` 一同放到一个 framework 工程中，编译生成我们的目标 framework。

接下来，我们想办法让 App 在启动时加载我们的 framework，让我们的修改生效。

macOS 的加载器支持从 `DYLD_INSERT_LIBRARIES` 环境变量中加载动态库，所以我们可以这样简单测试一下：

```shell
DYLD_INSERT_LIBRARIES=/path/to/your/framework/Versions/A/framework_name /Applications/Jietu.app/Contents/MacOS/Jietu
```

不出意外的话，就可以在终端下看到我们打印的 `HOOK Enabled!` 字样，崩溃修复。

下面我们来让 Jietu 自行加载我们的 framework。

在 Mach-O 文件格式中，在文件头的位置存着一些被称作 `Load Command` 的字段，用于声明在 App 启动时需要加载的动态库路径，可以使用 `otool -L` 打印出来，比如：

```
Jietu:
	/System/Library/Frameworks/CoreServices.framework/Versions/A/CoreServices (compatibility version 1.0.0, current version 775.8.2)
	/System/Library/Frameworks/Security.framework/Versions/A/Security (compatibility version 1.0.0, current version 57740.20.22)
	/System/Library/Frameworks/SystemConfiguration.framework/Versions/A/SystemConfiguration (compatibility version 1.0.0, current version 888.20.5)
	/System/Library/Frameworks/ApplicationServices.framework/Versions/A/ApplicationServices (compatibility version 1.0.0, current version 48.0.0)
	/usr/lib/libc++.1.dylib (compatibility version 1.0.0, current version 307.4.0)
	@rpath/JietuFramework.framework/Versions/A/JietuFramework (compatibility version 1.0.0, current version 1.0.0)
	@rpath/ZipArchive.framework/Versions/A/ZipArchive (compatibility version 1.0.0, current version 1.0.0)
	/usr/lib/libicucore.A.dylib (compatibility version 1.0.0, current version 57.1.0)
	@rpath/JTRecordSDK.framework/Versions/A/JTRecordSDK (compatibility version 1.0.0, current version 1.0.0)
	@rpath/AFNetworking.framework/Versions/A/AFNetworking (compatibility version 1.0.0, current version 1.0.0)
	@rpath/CocoaLumberjack.framework/Versions/A/CocoaLumberjack (compatibility version 1.0.0, current version 1.0.0)
	/System/Library/Frameworks/CoreLocation.framework/Versions/A/CoreLocation (compatibility version 1.0.0, current version 2100.3.14)
	/System/Library/Frameworks/ServiceManagement.framework/Versions/A/ServiceManagement (compatibility version 1.0.0, current version 972.20.3)
	@rpath/MASShortcut.framework/Versions/A/MASShortcut (compatibility version 1.0.0, current version 1.0.0)
	/usr/lib/libz.1.dylib (compatibility version 1.0.0, current version 1.2.8)
	/System/Library/Frameworks/Cocoa.framework/Versions/A/Cocoa (compatibility version 1.0.0, current version 22.0.0)
	/System/Library/Frameworks/Foundation.framework/Versions/C/Foundation (compatibility version 300.0.0, current version 1349.0.0)
	/usr/lib/libobjc.A.dylib (compatibility version 1.0.0, current version 228.0.0)
	/usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1238.0.0)
	/System/Library/Frameworks/AppKit.framework/Versions/C/AppKit (compatibility version 45.0.0, current version 1504.59.0)
	/System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation (compatibility version 150.0.0, current version 1348.15.0)
	/System/Library/Frameworks/CoreGraphics.framework/Versions/A/CoreGraphics (compatibility version 64.0.0, current version 1070.6.0)
	/System/Library/Frameworks/CoreText.framework/Versions/A/CoreText (compatibility version 1.0.0, current version 1.0.0)
	/System/Library/Frameworks/IOKit.framework/Versions/A/IOKit (compatibility version 1.0.0, current version 275.0.0)
	/System/Library/Frameworks/ImageIO.framework/Versions/A/ImageIO (compatibility version 1.0.0, current version 1.0.0)
	/System/Library/Frameworks/QuartzCore.framework/Versions/A/QuartzCore (compatibility version 1.2.0, current version 1.11.0)
```

所以我们只要想办法在这里插入我们修复 framework 的 Load Command 就可以让它在启动时自动加载修复了。这里使用的工具是：[insert_dylib](https://github.com/Tyilo/insert_dylib)，虽然 Xcode 自带的 `install_name_tool` 也能干类似的事情，不过需要先移除签名，insert_dylib 会自动干这个事情，我就直接用它了。把我们的 framework 复制到 `/Applications/Jietu.app/Contents/Frameworks` 下，执行如下命令添加 Load Command: 

```shell
insert_dylib @rpath/your.framework/Versions/A/framework_name /Applications/Jietu.app/Contents/MacOS/Jietu
```

这里解释下命令中的 `@rpath` 是硬编码在二进制文件中的运行时搜索路径的代称，在这里就值的是 App 目录中的 `Contents/Frameworks` 目录，这样不管这个应用复制到那里，总能通过相对路径找到 framework 文件。

到此，修复工作就暂时告一段落，我把相关代码托管到了 github 上，可以直接取用： [tylinux/JTFix](https://github.com/tylinux/JTFix)

enjoy~

