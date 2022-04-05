# iOS 11.0 - 11.1.2 越狱插件安装指南

> Electra 1.0 已经释出，包含 Cydia，下边的内容可能不适用于新版本的 Electra，仅供理解 Cydia 原理用。

<!--more-->

<br/>
**以下内容仅供参考**

> 放出越狱工具是不可能放出的，一辈子都不可能放出的。
> --- 国内 XX 安全实验室

果然靠国内的安全团队放出来越狱工具是不靠谱的，虽然这次 iOS 11 越狱漏洞的 [Writeup](http://blog.pangu.io/iosurfacerootuserclient-port-uaf/) 是盘古先发出来的，然而文末的这句：
>最后想说*****这次又是被谁撞了 TT

看起来很不爽啊。。
同一天，Google Project Zero 的大婶 [Ian Beer](https://twitter.com/i41nbeer) 注册 Twitter，并发推表示：__

![](https://i.loli.net/2018/02/07/5a7b1fa2ad33e.jpg)

看起来(应该是)是被 Ian Beer 撞了，5 天后，Ian Beer 放出完整的 `tfp0 (Task for pid 0)` [代码](https://bugs.chromium.org/p/project-zero/issues/detail?id=1417#c3)。之后另一位知名 iOS/macOS 安全研究员 [Jonathan Levin](https://twitter.com/Morpheus______) （《深入解析Mac OS X & iOS操作系统》系列图书的作者）在 `Ian Beer` 代码的基础上，开发了 `LiberIOS` 这一越狱工具，不过，由于 `CydiaSubstrate` 没有适配 iOS 11，所以越狱完成后没有 `Cydia` 商店，也不能安装常规的 `Tweak`。再之后，知名 Tweak 开发者 [CoolStar](https://twitter.com/coolstarorg) 基于 [Comex]() 开发的 `CydiaSubstrate` 的开源替代: [Substitute](https://github.com/comex/substitute)，开发了 [Electra](https://github.com/coolstar/electra.git) 越狱工具。支持 iOS11.0 - iOS 11.1.2 的全部 iOS 设备。此外，由于有 `Substitute` 的支持，不少基于 `CydiaSubstrate` 开发的 Tweak 也能运行。截止目前(2018-02-07)的版本(Beta 10)，运行 `Cydia` 需要的 `GPG` 和 `DPKG` 和 `APT` 都已经完成移植，推测在下一个 Beta 版本（也可能会是第一个 Release 版本）中，`Cydia` 就可以被适配到 iOS11 系统上。本文就是来介绍一下，Electra 中的插件目录结构以及如何手动完成一个 Tweak 的安装（因为没有 `Cydia`）。

## 越狱

1. 进入 [https://coolstar.org/electra/](https://coolstar.org/electra/) 下载最新的 Electra 的 ipa包。

2. 使用 `Cydia Impactor` 安装 ipa
3. 信任证书
4. 启动 `Electra` 进行越狱
5. Enjoy

## 目录一览

Electra 定义的目录结构与传统使用 `Cydia Substrate` 的越狱环境稍有不同。
Electra 将 Tweak 文件放置在`/bootsrap`目录下：

```
.
├── Library
│   ├── Application\ Support
│   ├── LaunchDaemons
│   ├── PreferenceBundles
│   ├── PreferenceLoader
│   ├── SBInject
│   └── Themes
├── README
├── amfid_payload.dylib
├── bin
│   ├── bash
│   ├── bzip2
│   ├── cp
│   ├── date
│   ├── dd
│   ├── dir
│   ├── echo
│   ├── egrep
│   ├── false
│   ├── fgrep
│   ├── grep
│   ├── gunzip
│   ├── gzexe
│   ├── gzip
│   ├── kill
│   ├── launchctl
│   ├── ln
│   ├── ls
|   ├── ...
│   └── znew
├── buildlist.sh
├── etc
│   ├── dropbear
│   └── profile
├── inject_criticald
├── jailbreakd
├── jailbreakd_client
├── pspawn_payload.dylib
├── sbin
│   ├── dmesg
│   ├── dynamic_pager
│   ├── ifconfig
│   ├── kextunload
│   ├── md5
│   ├── mknod
│   ├── nologin
│   ├── ping
│   └── shutdown
├── unjailbreak.sh
└── usr
    ├── bin
    ├── include
    ├── lib
    ├── libexec
    ├── local
    ├── sbin
    └── share
```

## 安装 Tweak

Electra 目前因为缺乏 DPKG 的支持以及目录结构有所改动，所以暂时无法直接安装 deb 包，我们需要手动完成这一步骤：

1. **下载**

以 `Cylinder` 为例：
打开 [http://apt.thebigboss.org/onepackage.php?bundleid=com.r333d.cylinder](http://apt.thebigboss.org/onepackage.php?bundleid=com.r333d.cylinder) 下载 Deb 文件。

2. **解包**

执行如下命令解包：

```bash
dpkg -x xxxxx.deb .
```

(如果找不到 `dpkg` 命令，macOS 下使用 `brew install dpkg` 进行安装，其他系统自行查找安装)

3. **上传**

通常的 Tweak 解包出来的目录类似这样：

```
Library
└── MobileSubstrate
    └── DynamicLibraries
        ├── weixin_tweak.dylib
        └── weixin_tweak.plist
```

    在 Electra 中，我们需要将 `Library/MobileSubstrate/DynamicLibraries` 中的 `.dylib` 文件和相应的 `.plist` 文件 通过 scp 复制到 iOS 系统中的 `/bootstrap/Library/SBInject/` 目录下。

但是也有一些 Tweak 会包含更多的文件，比如 `Cylinder`:

```
Library
├── Cylinder
│   ├── Beta382
│   ├── EXAMPLE.lua
│   ├── JGTweaks
│   ├── KnifeOfPi
│   ├── Qaanol
│   ├── ViktorX11
│   ├── cylgom
│   ├── gertab
│   ├── r_idn
│   ├── rweichler
│   └── supermamon
├── MobileSubstrate
│   └── DynamicLibraries
├── PreferenceBundles
│   └── CylinderSettings.bundle
└── PreferenceLoader
    └── Preferences

17 directories, 1 file
```

这种应该这么处理：

* `MobileSubstrate/DynamicLibraries` 下的 `.dylib` 和 `.plist` 文件按照之前的方式，复制到 `/bootstrap/Library/SBInject/` 目录下。
* `PreferenceBundles` 中的 `.bundle` 文件，整体复制到设备的 `/bootstrap/Library/PreferenceBundles/` 目录下。
* `PreferenceLoader/Preferences` 下的 `.plist` 文件，复制到设备的 `/bootstrap/Library/PreferenceLoader/Preferences/` 目录下。
* 对于类似与 `Cylinder` 这样的 “多余” 目录，通通复制到设备的 `/Library` 目录，**注意，是 /Library 而不是 /bootstrap/Library 哟**

4. **重启**

大部分的 Tweak 安装是不需要重启设备哒，只需要 `Respring` 既可（就是重启 SpringBoard）。
`ssh` 登录到设备，执行:

```shell
killall SpringBoard
```

Enjoy!

## P.S

在 Ian Beer 公布 iOS 11.1.x 的越狱漏洞后没几天，阿里潘多拉安全实验室宣布已经攻破了 iOS 11.2 系统，完成了 iOS 11.2 越狱。然而，和 KeenTeam 及盘古的套路一样，说什么仅用于安全研究，不会对外公布。照这个套路，我也可以宣布我已经攻破了 iOS 11.3，并且是完！美！越！狱！但是，仅用于安全研究，不对外公布的哟～

![](https://i.loli.net/2018/02/07/5a7b1fa375aec.jpg)
