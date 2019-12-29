--- 
title: "macOS 10.15.1 下编译 VirtualBox 6.1.0"
date: 2019-12-29T18:44:33+08:00
tags: [hackintosh,ryzen,virtualbox]
categories: ["软件开发"]
---

在 AMD CPU 的机器上安装黑苹果之后，能用的虚拟机软件基本只有 VirtualBox 了。虽然能用，但是性能差的让人抠脚。通常来讲，虚拟机软件会优先利用 CPU 的虚拟化特性，比如 Intel 的 `VT-X/VT-D` 以及 AMD 的 `SVM`，在硬件虚拟化不可用的时候，会使用纯软件模拟的方式运行 Guest 系统指令。macOS 截止目前，全部运行在 Intel 的 CPU 上，所以其虚拟化框架 `Hypervisor.framework`，也全部是基于 Intel 的虚拟化指令实现，并没有兼容 AMD，这也是 `VMWare` 等其他虚拟机软件无法在 AMD CPU 的黑苹果上运行的根本原因。

VirtualBox 看起来没有强依赖 `Hypervisor.framework`，因此在 AMD CPU 上也可以运行。但是这糟糕的性能让我怀疑它没有使用 `SVM` 来运行虚拟机，而是纯软件模拟。为了一探究竟，我准备在 macOS 上自行编译 VirtualBox。

<!--more-->

## 准备工作

1. 系统：macOS 10.15.1 
2. CPU：AMD Ryzen 3700X
3. Xcode：Xcode 11.3
4. 重启至 Recovery 模式，关闭 `SIP`

## 编译

### 准备源码
VirtualBox 的源码在其[下载页面](https://www.virtualbox.org/wiki/Downloads)即可看见。有两种，SVN 同步或者直接下载当前版本的 tar 包。没用过 SVN，我选择下载 tar 包，下载链接：[VirtualBox-6.1.0.tar.bz2](https://download.virtualbox.org/virtualbox/6.1.0/VirtualBox-6.1.0.tar.bz2)

### 安装编译依赖
按照官方的编译指南，编译 VirtualBox 需要 `libidl openssl pkg-config qt` 这些第三方依赖，不过指南里用的是 `MacPort`，而我使用的是 `Homebrew`，所以，安装命令有所不同：

```shell
brew install libidl openssl pkg-config qt
```

除此之外，在编译过程中还会用到 `Java`，所以还得安装 `JDK`。可以选择从 Oarcle 的官网下载安装，或者使用 `jabba` 安装：

```bash
# 安装 Jabba 
curl -sL https://github.com/shyiko/jabba/raw/master/install.sh | bash && . ~/.jabba/jabba.sh
jabba install openjdk@1.13.0
jabba alias default openjdk@1.13.0
```

### 安装 Mac OS X 10.9 SDK
VirtualBox 的编译脚本是以 10.9 版本系统为目标 SDK 编写的，而且其使用的部分 IOKit 的方法已经在 10.11 版本中移除，使用新版本 SDK 无法编译通过，所以在开始编译之前需要安装一下 10.9 的 SDK。

用的工具是 `XcodeLegacy`，一个开源的 shell 脚本，可以自动处理和安装低版本 Xcode 中携带的 SDK。
除此之外，还需要一个 Xcode 6.4 版本的安装镜像，下载地址（官方地址，需要登录）：[Xcode_6.4.dmg](https://download.developer.apple.com/Developer_Tools/Xcode_6.4/Xcode_6.4.dmg)，下载完成后，与 `XcodeLegacy` 放置在同一目录。

使用方式：

```bash
wget https://raw.githubusercontent.com/devernay/xcodelegacy/master/XcodeLegacy.sh
chmod +x XcodeLegacy.sh
./XcodeLegacy.sh -osx109 buildpackages
sudo ./XcodeLegacy.sh -osx109 install
```

### 编译
按照编译指南，执行 `./configure --disable-hardening` 生成编译脚本，报错如下：

```text
...
Checking for Darwin version:   failed to determine Darwin version. (uname -r: 19.0.0)
Check /Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/configure.log for details
```

从字面意思来看，就是未知的 Darwin 系统版本：19.0.0，打开 `configure` 文件，编辑 `check_darwinversion` 函数，添加对 macOS 10.15 的支持：

```diff
@@ -2196,6 +2196,15 @@ check_darwinversion()
   test_header "Darwin version"
   darwin_ver=`uname -r`
   case "$darwin_ver" in
+  19\.*)
+      check_xcode_sdk_path "$WITH_XCODE_DIR"
+      [ $? -eq 1 ] || fail
+      darwin_ver="10.15" # macOS Catalina
+      sdk=$WITH_XCODE_DIR/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.9.sdk
+      cnf_append "VBOX_WITH_MACOSX_COMPILERS_FROM_DEVEL" "1"
+      cnf_append "VBOX_PATH_MACOSX_DEVEL_ROOT" "$WITH_XCODE_DIR/Developer"
+      CXX_FLAGS='--std=c++11'
+      ;;
     17\.*)
       check_xcode_sdk_path "$WITH_XCODE_DIR"
       [ $? -eq 1 ] || fail
```

顺便添加了 `--std=c++11`，打开 C++ 11 的支持。
再次执行 `./configure --disable-hardening`，报错如下：

```text
...
Checking for Darwin version: Please specify --with-xcode-dir option.
Check /Users/tylinux/Developer/Sources/vbox/VirtualBox-6.1.0/configure.log for details
```

要求使用 `--with-xcode-dir` 传入 `Xcode` 的安装路径，OK，改用新的命令 `./configure --disable-hardening --with-xcode-dir=/Applications/Xcode.app`，报错如下：

```text
...
Checking for ssl:
  libcrypto not found at  -lssl -lcrypto or openssl headers not found
  Check the file /Users/tylinux/Developer/Sources/vbox/VirtualBox-6.1.0/configure.log for detailed error information.
Check /Users/tylinux/Developer/Sources/vbox/VirtualBox-6.1.0/configure.log for details
```

找不到 `openssl`，执行 `./configure --help`，可以看到其支持通过 `--with-openssl-dir=` 指定 `openssl` 目录，OK，命令改成：`./configure --disable-hardening --with-xcode-dir=/Applications/Xcode.app --with-openssl-dir=/usr/local/opt/openssl@1.1/`，这是 Homebrew 安装的 openssl 的路径，报错如下：

```text
...
Checking for Qt5:
  ** Qt5 framework not found (can be disabled using --disable-qt)!
Check /Users/tylinux/Developer/Sources/vbox/VirtualBox-6.1.0/configure.log for details
```

找到 openssl 了，但是 qt5 没有找到，同样的，我们通过 `--with-qt-dir` 指定一下，命令：`./configure --disable-hardening --with-xcode-dir=/Applications/Xcode.app --with-openssl-dir=/usr/local/opt/openssl@1.1/ --with-qt-dir=/usr/local/Cellar/qt/5.14.0`，配置成功，日志如下：

```text
Checking for environment: Determined build machine: darwin.amd64, target machine: darwin.amd64, OK.
Checking for kBuild: found, OK.
Checking for Darwin version: found version 10.15 (SDK: /Applications/Xcode.app/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.9.sdk), OK.
Checking for gcc: found version 4.2.1, OK.
Checking for Open Watcom:
  ** Open Watcom was not found, using alternative BIOS sources!
Checking for libIDL: found version 0.8.14, OK.
Checking for ssl: found version OpenSSL 1.1.1d  10 Sep 2019, OK.
Checking for libcurl: found version 7.64.1, OK.
Checking for OpenGL support: enabled
Checking for Qt5: found version 5.14.0, OK.
Checking for Python support: enabled
Checking for Java support: OK.

Successfully generated '/Users/tylinux/Developer/Sources/vbox/VirtualBox-6.1.0/AutoConfig.kmk' and '/Users/tylinux/Developer/Sources/vbox/VirtualBox-6.1.0/env.sh'.
Source '/Users/tylinux/Developer/Sources/vbox/VirtualBox-6.1.0/env.sh' once before you start to build VBox:

  source /Users/tylinux/Developer/Sources/vbox/VirtualBox-6.1.0/env.sh
  kmk


  +++ WARNING +++ WARNING +++ WARNING +++ WARNING +++ WARNING +++ WARNING +++
  Hardening is disabled. Please do NOT build packages for distribution with
  disabled hardening!
  +++ WARNING +++ WARNING +++ WARNING +++ WARNING +++ WARNING +++ WARNING +++

Enjoy!
```

按照提示，执行 `source /Users/tylinux/Developer/Sources/vbox/VirtualBox-6.1.0/env.sh` 配置环境变量，然后执行 `kmk` 开始编译。
报错如下：

```text
...
The failing command:
@yasm -f macho64 -DASM_FORMAT_MACHO -D__YASM__ -Worphan-labels -I/Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/src/VBox/Runtime/include/ -I/Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/src/libs/liblzf-3.4/ -I/Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/src/libs/libxml2-2.9.4/include/ -I/Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/include/ -I/Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/out/darwin.amd64/release/ -DVBOX -DVBOX_OSE -DVBOX_WITH_64_BITS_GUESTS -DRT_OS_DARWIN -D__DARWIN__ -DRT_ARCH_AMD64 -D__AMD64__ -D_REENTRANT -DLIBXML_STATIC -DLIBXML_STATIC_FOR_DLL -DIN_RING3 -DLOG_DISABLED -DIN_BLD_PROG -DIN_RT_R3 -DIN_ADV_BLD_PROG -DIN_RT_R3 -DLDR_WITH_NATIVE -DLDR_WITH_ELF32 -DLDR_WITH_LX -DLDR_WITH_MACHO -DLDR_WITH_PE -DRT_WITH_VBOX -DRT_NO_GIP -DRT_WITHOUT_NOCRT_WRAPPERS -DNOFILEID -DRT_WITH_ICONV_CACHE -DIPRT_WITHOUT_LDR_VERIFY -DRT_NO_GIP -DMAC_OS_X_VERSION_MIN_REQUIRED=1090 -DMAC_OS_X_VERSION_MAX_ALLOWED=1090 -l /Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/out/darwin.amd64/release/obj/RuntimeBldProg/common/misc/zero.lst -o /Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/out/darwin.amd64/release/obj/RuntimeBldProg/common/misc/zero.o /Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/src/VBox/Runtime/common/misc/zero.asm
kBuild: Compiling RuntimeBldProg - /Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/src/VBox/Runtime/common/misc/zero.asm
kmk: execvp: yasm: Bad CPU type in executable
kmk: *** [/Users/tylinux/Developer/Sources/vbox/VirtualBox-6.1.0/kBuild/footer-pass2-compiling-targets.kmk:292: /Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/out/darwin.amd64/release/obj/RuntimeBldProg/common/misc/zero.o] Error 127
kmk: *** Waiting for unfinished jobs....
...
```

`yasm: Bad CPU type in executable`，看起来 `yasm` 不是一个正确的 `Mach-O` 可执行文件。执行 `file tools/darwin.amd64/bin/yasm`，结果：

```text
tools/darwin.amd64/bin/yasm: Mach-O executable i386
```

嗯，macOS 10.15 正式放弃对 32bit 应用的支持，所以 `i386` 架构的可执行文件已经不可执行了。执行 `brew install yasm` 安装 yasm，然后 `cp /usr/local/Cellar/yasm/1.3.0_2/bin/yasm tools/darwin.amd64/bin/` 替换掉原来的 `yasm` 可执行文件。`kmk` 继续编译：

再次报错：

```text
...
kBuild: iasl VBoxDD - /Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/src/VBox/Devices/PC/vbox.dsl
kmk: execvp: /Users/tylinux/Developer/Sources/vbox/VirtualBox-6.1.0/tools/darwin.amd64/bin/iasl: Bad CPU type in executable
kmk: *** [/Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/src/VBox/Devices/Makefile.kmk:850: /Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/out/darwin.amd64/release/obj/VBoxDD/vboxaml.hex] Error 127
kmk: *** Waiting for unfinished jobs...
...
```

看来 `tools/darwin.amd64/bin/iasl` 也是一个 32bit 应用，不过这个 Homebrew 上没有，所以用知名大佬 `RehabMan` 的仓库中提供的 `iasl` 替代，下载地址：[acpica](https://bitbucket.org/RehabMan/acpica/downloads/)，下载完成后同样的方式替换掉 `tools/darwin.amd64/bin/iasl`。kmk` 继续编译：

报错信息：

```text
...
kBuild: Generating tstVMStructSize - /Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/out/darwin.amd64/release/obj/VMM/tstAsmStructsHC.h
In file included from /Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/src/VBox/Debugger/testcase/tstVBoxDbg.cpp:22:
In file included from /usr/local/Cellar/qt/5.14.0/Frameworks/QtWidgets.framework/Versions/5/Headers/qapplication.h:43:
In file included from /usr/local/Cellar/qt/5.14.0/Frameworks/QtWidgets.framework/Headers/qtwidgetsglobal.h:43:
In file included from /usr/local/Cellar/qt/5.14.0/Frameworks/QtGui.framework/Headers/qtguiglobal.h:43:
In file included from /usr/local/Cellar/qt/5.14.0/Frameworks/QtCore.framework/Headers/qglobal.h:105:
/usr/local/Cellar/qt/5.14.0/Frameworks/QtCore.framework/Headers/qcompilerdetection.h:558:6: error: Qt requires a C++11 compiler and yours does not seem to be that.
#    error Qt requires a C++11 compiler and yours does not seem to be that.
     ^
kBuild: Compiling tstMediumLock - /Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/src/VBox/Main/testcase/tstMediumLock.cpp
...
```

QT5 提供的头文件，需要编译器支持 C++ 11 才能使用，编辑 `tools/kBuildTools/VBoxXcode62.kmk`，给 C++ 文件和 Objective-C++ 文件添加 `--std=c++` 选项：

```diff
 TOOL_VBoxXcode62_CXXOBJSUFF       ?= .o
-TOOL_VBoxXcode62_CXXFLAGS         ?=
+TOOL_VBoxXcode62_CXXFLAGS         ?= --std=c++11
 TOOL_VBoxXcode62_CXXFLAGS.debug   ?= -g
 TOOL_VBoxXcode62_CXXFLAGS.profile ?= -O2 #-g -pg
 TOOL_VBoxXcode62_CXXFLAGS.release ?= -O2
@@ -107,7 +107,7 @@ TOOL_VBoxXcode62_OBJCINCS         ?=
 TOOL_VBoxXcode62_OBJCDEFS         ?=

 TOOL_VBoxXcode62_OBJCXXOBJSUFF        ?= .o
-TOOL_VBoxXcode62_OBJCXXFLAGS          ?=
+TOOL_VBoxXcode62_OBJCXXFLAGS          ?= --std=c++11
 TOOL_VBoxXcode62_OBJCXXFLAGS.debug    ?= -g
 TOOL_VBoxXcode62_OBJCXXFLAGS.profile  ?= -O2 #-g -pg
 TOOL_VBoxXcode62_OBJCXXFLAGS.release  ?= -O2
```

`kmk` 继续编译，错误如下：

```text
/Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/src/VBox/Devices/USB/darwin/USBProxyDevice-darwin.cpp:1126:34: error: comparison between pointer and integer ('CFMutableDictionaryRef' (aka '__CFDictionary *') and 'io_object_t'
      (aka 'unsigned int'))
    AssertReturn(RefMatchingDict != IO_OBJECT_NULL, VERR_OPEN_FAILED);
                 ~~~~~~~~~~~~~~~ ^  ~~~~~~~~~~~~~~
/Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/include/iprt/assert.h:390:26: note: expanded from macro 'AssertReturn'
        if (RT_LIKELY(!!(expr))) \
                         ^~~~
/Volumes/macOSData/Developer/Sources/vbox/VirtualBox-6.1.0/include/iprt/cdefs.h:1778:53: note: expanded from macro 'RT_LIKELY'
#  define RT_LIKELY(expr)       __builtin_expect(!!(expr), 1)
                                                    ^~~~
1 error generated.
```

指针类型和整型做比较，报错了，改成这样：

```diff
     CFMutableDictionaryRef RefMatchingDict = IOServiceMatching(kIOUSBDeviceClassName);
-    AssertReturn(RefMatchingDict != IO_OBJECT_NULL, VERR_OPEN_FAILED);
+    AssertReturn(RefMatchingDict, VERR_OPEN_FAILED);

     uint64_t u64SessionId = 0;
```

`kmk`，编译成功。

## 运行
编译结果在 `out/darwin.amd64/release/dist` 目录下，`VirtualBox.app` 是 App，`*.kext` 则是 VirtualBox 需要的内核扩展。执行 `loadall.sh` 加载内核扩展，报错如下：

```text
...
Code Signing Failure: not code signed
Disabling KextAudit: SIP is off
(kernel) kxld[org.virtualbox.kext.VBoxDrv]: The following symbols are unresolved for this kext:
(kernel) kxld[org.virtualbox.kext.VBoxDrv]:     _g_abSUPBuildCert
(kernel) kxld[org.virtualbox.kext.VBoxDrv]:     _g_cbSUPBuildCert
(kernel) Can't load kext org.virtualbox.kext.VBoxDrv - link failed.
...
```

嗯，我们的编译生成的 kext 没有代码签名，被拒绝加载了。

解决方案：

1. 按照 [https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/Procedures/Procedures.html](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/Procedures/Procedures.html) 所述，生成自签证书。
2. 在 VirtualBox 源码目录下新建 `LocalConfig.kmk`，文件内容：
    
    ```text
    VBOX_SIGNING_MODE = test
    VBOX_CERTIFICATE_SUBJECT_NAME = My Code Signing Cert
    ```
    其中，`VBOX_CERTIFICATE_SUBJECT_NAME` 就是你在生成自签证书是起的名字，重新 `kmk`，编译成功。

## 参考链接
1. [Mac OS X build instructions](https://www.virtualbox.org/wiki/Mac%20OS%20X%20build%20instructions)
2. [My experience building VirtualBox from Subversion on Mojave](https://forums.virtualbox.org/viewtopic.php?f=8&t=92989)
3. [xcodelegacy](https://github.com/devernay/xcodelegacy)
4. [jabba](https://github.com/shyiko/jabba)
