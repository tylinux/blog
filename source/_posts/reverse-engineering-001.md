---
title: 《iOS逆向工程》- 越狱
date: 2017-07-24 14:15:50
tags: [reverse,iOS]
---

> 有这么一种事儿，它在Android上叫Root，在iOS上叫越狱，在Symbian上叫免签，在Web入侵时叫提权，在生活里，它叫表白…名字和领域不同，但道理惊人地相同：之前举步维艰，之后为所欲为

移动设备操作系统相比与PC系统有很大不同，移动设备出于设备配置、电量、用户隐私等方面考虑， 会对系统中应用的权限进行限制，比如限制应用后台运行、限制调用部分API。其中，尤以iOS限制最为严格，所有应用运行于沙箱之中，只能访问有限的公有API，使用网络、位置等信息都需要用户许可，无法在后台常驻，在上线之前还要接受苹果爸爸的审核。当然这也是iOS能保持省电、流畅、安全的重要原因。但是，在这样封闭的操作系统下，我们无法对运行着的进程进行动态调试，也无法获取到解密之后的二进制进行逆向分析，所以，在进行iOS逆向分析之前，首先要对系统进行破解以获得更高的权限，以达到我们“为所欲为”的目的。

## 越狱
运行于 iOS 系统中的应用，被限制在一个个的沙盒之中，犹如坐牢一般。而破解之后就可以越过沙盒，不受限制地访问系统资源，因此，破解iOS系统被称作“越狱(jailbreak)”。

越狱根据一次越狱操作的时效性，可以分为完美越狱（untethered jailbreak）和非完美越狱（tethered jailbreak）两种，区别在于，完美越狱一次越狱之后可以始终保持越狱状态，而非完美越狱重启之后越狱环境就会丢失，需要再次进行越狱操作。

每一次越狱工具发布之后，苹果爸爸就会在下一次的系统升级中对越狱用到的漏洞进行修补，随着 iOS 系统版本的迭代，发现可用于越狱的系统漏洞也越来越难，iOS8 之后至今再没有出现完美越狱的方案，而 iOS 10开始，非完美越狱也越来越难，虽然在 Google Project Zero 的“帮助”下，Luca Todesco 开发了 **Yalu102** ，但是支持设备有限，越狱稳定性不高。

## Cydia
在 iOS 设备越狱之后，通常都会安装一个叫 “Cydia” 的App，Cydia 由 Jay Freeman（saurik）和他的公司开发，用于安装、管理越狱设备上的第三方软件、插件。它移植了Debian上的包管理器dpkg并提供了图形化前端，方便普通用户使用。Cydia 中还有个 Cydia Store，提供付费的第三方应用。

## CydiaSubstrate
除了Cydia之外，通常越狱工具还会为我们安装一个框架：CydiaSubstrate。在 iOS7 之前也叫MobileSubstrate，也是由saurik开发的。它为越狱设备提供了一个稳定的代码修改平台，通过MS框架，开发着可以很方便的动态修改App的行为。Cydia 中提供的许多第三方App，都是基于MS框架开发的。

## SSH
在设备越狱之后，我们不可避免地要修改设备文件或者上传/下载文件到设备中，这时，我们就需要一个沟通的桥梁：SSH。

SSH需要通过Cydia安装，在Cydia中搜索安装“openssh”:
![](/images/15008777283509.jpg)

安装之后，连入同一个子网下，既可通过``ssh root@xxx.xxx.xxx.xxx``的方式登录到设备。（默认密码**alpine**，登录之后可通过``passwd``命令修改默认密码）

## Tips-1
通过无线网络登录SSH有如下几个缺点：

* 设备IP不固定，除非通过路由指定IP，否则每次重连都可能导致IP变化
* 同一个子网下的所有设备均可通过SSH登录到越狱设备，不够安全
* 无线网络不够稳定，带宽较小，上传/下载大文件时需要较长时间

基于上边的几个原因，推荐一个更好的解决方案：通过USB连接登录。
通过USB连接登录设备需要在上位机上安装一个工具：**iproxy**，它可以将通过USB连接的 iOS 设备上的端口映射到本地端口，之后通过 **localhost:本地端口** 的形式既可与设备进行通信，使用方法如下：

```bash
# iproxy 本地端口 设备端口
# 比如：越狱设备的SSH绑定端口是22，映射到本地端口2222：
iproxy 2222 22

# 之后，既可通过localhost与设备通信了
ssh -P 2222 root@localhost
```

直接通过终端执行iproxy命令映射端口需要单独占用一个终端/Tab，如果不小心关闭了终端就会导致通信中断。所以。。。我们可以把它写成一个服务：

1. 在 ``~/Library/LaunchAgents`` 目录下新建 **com.usbmux.iproxy.plist** 文件

``` bash
touch ~/Library/LaunchAgents/com.usbmux.iproxy.plist
```

2. 将如下内容复制到刚刚新建的文件中：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.usbmux.iproxy</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/iproxy</string>
        <string>2222</string>
        <string>22</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

3. 执行如下命令启动iproxy服务

```bash
launchctl load com.usbmux.iproxy.plist
```

之后，iproxy就不依赖终端，独立运行于后台了。


