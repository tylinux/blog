---
title: 解 React Native『*** Terminating app due to uncaught exception 'std::__1::system_error', reason: 'mutex lock failed: Invalid argument'』 Crash
date: 2019-08-13 15:23:40
tags: [iOS]
---

我司客户端中使用了 React Native 0.54.3 版本，自接入开始，就出现了一类很诡异的 Crash，崩溃信息如下：

```
Incident Identifier: 916505BF-F7E5-451E-9753-610B112D52CD
CrashReporter Key:   b88d7a65a6fdfb6830fd28b6bb8ce61d3a94b4b9
Hardware Model:      iPhone8,1
Process:         imeituan [369]
Path:            /var/containers/Bundle/Application/2E7EA9D4-576E-4D1A-AC4F-CA141E78E4BB/imeituan.app/imeituan
Identifier:      com.meituan.imeituan
Version:         31746 (10.1.201)
Code Type:       ARM-64
Parent Process:  ? [1]

Date/Time:       2019-08-11 20:57:00.000 +0800
OS Version:      iOS 12.4 (16G77)
Report Version:  104

Exception Type:  EXC_CRASH (SIGABRT)
Exception Codes: 0x00000000 at 0x0000000000000000
Crashed Thread:  38

Application Specific Information:
*** Terminating app due to uncaught exception 'std::__1::system_error', reason: 'mutex lock failed: Invalid argument'
```

崩溃线程没有调用栈信息，类似下图：

![](https://i.loli.net/2019/08/13/BUi4wILt6MKRN2j.jpg)

经过观察，此类崩溃还有一个共同特点，就是主线程都有调用 `exit`，意味着程序正在退出，在退出过程中发生的崩溃。主线程调用栈如下：

```
Thread 0:
0   imeituan                        std::__1::unordered_map<int, agora::rtc::PeerCounterProperty, std::__1::hash<int>, std::__1::equal_to<int>, std::__1::allocator<std::__1::pair<int const, agora::rtc::PeerCounterProperty> > >::~unordered_map() + 0
1   libsystem_c.dylib               __cxa_finalize_ranges + 384
2   libsystem_c.dylib               exit + 24
3   UIKitCore                       -[UIApplication terminateWithSuccess] + 0
4   UIKitCore                       __98-[__UICanvasLifecycleMonitor_Compatability deactivateEventsOnly:withContext:forceExit:completion:]_block_invoke.261 + 344
5   UIKitCore                       _runAfterCACommitDeferredBlocks + 296
6   UIKitCore                       _cleanUpAfterCAFlushAndRunDeferredBlocks + 352
7   UIKitCore                       _afterCACommitHandler + 116
8   CoreFoundation                  __CFRUNLOOP_IS_CALLING_OUT_TO_AN_OBSERVER_CALLBACK_FUNCTION__ + 32
9   CoreFoundation                  __CFRunLoopDoObservers + 412
10  CoreFoundation                  __CFRunLoopRun + 1228
11  CoreFoundation                  CFRunLoopRunSpecific + 436
12  GraphicsServices                GSEventRunModal + 104
13  UIKitCore                       UIApplicationMain + 212
14  imeituan                        main (main.m:36)
15  libdyld.dylib                   start + 4
```

因为没有堆栈，加上用户不感知，就放了几个版本，Crash 量倒也稳定。
然而，在最近的版本中，做了个 React Native 的 RCTBridge 永久驻留的需求，这个崩溃就开始飙升了，只能硬着头皮搞了。

一番搜索，发现 `RCTFont.mm` 有个类似的 Crash: [issue](https://github.com/facebook/react-native/issues/13588)，修复[PR](https://github.com/facebook/react-native/pull/22607/files)。修改内容如下图：

![](https://i.loli.net/2019/08/13/SmBwNZrKGaPCA5J.jpg)

就是把 `static std::mutex fontCacheMutex;` 改成了 `static std::mutex *fontCacheMutex`，普通的 `std::mutex` 变量改成了指针变量。区别在哪里呢？

回忆一下上边的错误信息：`mutex lock failed: Invalid argument`，说明调用 `std::lock_guard<std::mutex> lock` 时传入的参数不是一个正确的 `std::mutex` 对象。结合 Crash 发生在 App  exit 的时候，我们基本可以推断出 Crash 原因： `static std::mutex fontCacheMutex;` 在 App exit 的时候，被释放了，而其他线程在它被释放之后，又调用了 `std::lock_guard<std::mutex> lock`，因为它已经被释放了，已经不是一个 `std::mutex`，导致了崩溃。

那为什么主线程 exit 的时候，`fontCacheMutex` 就被释放掉了呢？这就要从 static 对象的生命周期说起了（我也是现查的ಥ_ಥ）

编写如下 C++ 代码：

```c++
#include <mutex>

void test() {
    static std::mutex s_mutex;
    static int testVar;
}

int main(int argc, char *argv[]) {
    test();
}
```

编译成可执行文件，然后 IDA Pro 反编译一下：

```c++
void test(void)
{
  if ( !`guard variable for'test(void)::s_mutex )
  {
    if ( (unsigned int)__cxa_guard_acquire(&`guard variable for'test(void)::s_mutex) )
    {
      std::__1::mutex::mutex((std::__1::mutex *)&test(void)::s_mutex);
      __cxa_atexit(&std::__1::mutex::~mutex, &test(void)::s_mutex, &_mh_execute_header);
      __cxa_guard_release(&`guard variable for'test(void)::s_mutex);
    }
  }
}
```

`guard_for_bar` 啥的是编译器生成的用来保证线程安全和一次初始化的变量，咱不关注，重点是 ` __cxa_atexit(&std::__1::mutex::~mutex, &test(void)::s_mutex, &_mh_execute_header);` 一行，`__cxa_atexit` 是用来注册当调用 `exit`，或者动态库被卸载时执行的函数的，这里注册的是 `std::__1::mutex::~mutex`。就是 `s_mutex` 的析构函数。此函数会在 exit 时被调用，销毁此对象。

所以，真相就是：`static std::mutex fontCacheMutex;` 会在 `exit` 时被析构掉，之后再 lock 此变量就 GG 了！

那为啥改成 `static std::mutex *fontCacheMutex` 就好使了呢？那是因为 `static std::mutex *` 是一个指针类型变量，编译器不会为普通类型的静态变量注册释放函数的。

知道原因就好办啦，虽然没有崩溃堆栈，但是我们有源码，React 仓库里全局搜索: `static std::mutex`，找到 `RCTCxxUtils.mm` 文件中的一处使用：

```objc
JSContext *contextForGlobalContextRef(JSGlobalContextRef contextRef)
{
  static std::mutex s_mutex;
  static NSMapTable *s_contextCache;

  if (!contextRef) {
    return nil;
  }

  // Adding our own lock here, since JSC internal ones are insufficient
  std::lock_guard<std::mutex> lock(s_mutex);
  if (!s_contextCache) {
    NSPointerFunctionsOptions keyOptions = NSPointerFunctionsOpaqueMemory | NSPointerFunctionsOpaquePersonality;
    NSPointerFunctionsOptions valueOptions = NSPointerFunctionsWeakMemory | NSPointerFunctionsObjectPersonality;
    s_contextCache = [[NSMapTable alloc] initWithKeyOptions:keyOptions valueOptions:valueOptions capacity:0];
  }

  JSContext *ctx = [s_contextCache objectForKey:(__bridge id)contextRef];
  if (!ctx) {
    ctx = [JSC_JSContext(contextRef) contextWithJSGlobalContextRef:contextRef];
    [s_contextCache setObject:ctx forKey:(__bridge id)contextRef];
  }
  return ctx;
}
```

照猫画虎，替换成 `static std::mutex *s_mutex = new std::mutex;`。

Bug Fixed!

## 参考资料:
1. [__cxa_atexit](http://refspecs.linuxbase.org/LSB_3.0.0/LSB-PDA/LSB-PDA/baselib---cxa-atexit.html)
2. [深入理解函数内静态局部变量初始化](https://www.cnblogs.com/william-cheung/p/4831085.html)