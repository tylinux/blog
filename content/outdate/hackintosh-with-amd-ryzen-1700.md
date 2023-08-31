---
title: AMD Ryzen 1700 也吃黑苹果
date: 2019-05-07 19:10:39
tags: [hackintosh]
categories: ["硬件"]
---

公司配发的笔记本是 `MacBook Pro 15' Mid 2015`，随着公司工程的逐步膨胀，老家伙干活越来越吃力。便有了组建一台黑苹果干编译这些脏活儿累活儿，笔记本就用来开会的想法。

<!--more-->

## 双路 E5
关于黑苹果的配置，考虑了好几种方案，原本是准备上双路 E5 洋垃圾，配置方案如下：

| 配件 | 型号 | 价格  |
| --- | --- | --- |
| CPU | E5-2667 v2 x 2 | 985 x 2 |
| 内存 | 三星 DDR3 1866 ECC REG 16GB * 4 | 158 x 4 |
| 主板 | 超微 X9DAi | 1580 |
| 显卡 | XFX RX570 4G 矿渣 | 299 |
| 电源 | 长城矿龙 1250W 模组电源  | 158 |
| 机箱 | 先马坦克3 | 199 |

但是这个配置问题在于，主板太贵了，还是二手的；双路 E5 的功耗又很大。E5 的黑苹果也没看到很多文章。就在爬楼找 E5 黑苹果的教程贴的过程中，发现了这个 [repo](https://github.com/cheneyveron/clover-x79-e5-2670-gtx650)。作者在文档中有这么一段：

> 如今X79只能使用DDR3内存，最高1866MHz，并且E5 v2处理器性价比已经不高。Intel 7系以上处理器性价比极低，新配电脑推荐使用Ryzen + x370主板。Ryzen黑苹果我自认为已经找到了一种近乎"完美"的方案：见[我的博客](https://www.itmanbu.com/ryzen-hackintosh-using-kvm-proxmox.html)、[远景论坛](http://bbs.pcbeta.com/viewthread-1813655-1-1.html)

## AMD YES！
在作者的博客中，介绍了在 `Proxmox` 系统中借助 `KVM` 安装 macOS 的方法。经过作者测试，虚拟化的 macOS 在 CPU 性能上会有 5% 左右的损失，GPU 性能因为可以 PCI passthrough，所以理论上是没有损失的。

在之后的爬贴过程中，又发现了作者在 PCBeta 中发的另一贴：[AMD Ryzen不用替换内核，裸机性能爆炸，还能使用iMessage/直接升级](http://bbs.pcbeta.com/viewthread-1814040-1-4.html)。我之前之所以不考虑使用 AMD 平台黑苹果，是因为传统 AMD 黑苹果需要替换内核，系统升级会比较滞后。在这个帖子中，作者介绍了 [AMD_Vanilla](https://github.com/AMD-OSX/AMD_Vanilla) 这个项目。此项目是基于 Clover EFI 提供的 KernelToPatch 功能，对 macOS 的内核进行 Patch，使其可以正常运行在 AMD 平台上。解决了传统 AMD 黑苹果因为修改系统文件导致 Facetime、iMessage 等系统软件无法运行的问题。但同时，因为其原理还是对内核打补丁，所以一些依赖 Intel 平台特性的软件，比如 VMware Fusion、Docker等还是无法运行。不过开源的 VirtualBox 是可以正常运行在 AMD 平台下的，我平台也就需要运行个 Windows 和 Genymotion，这些都是可以在 VirtualBox 里运行的。就是你了！

**AMD YES！**

我最喜欢 AMD 的两点：便宜、更新不换主板，所以在 Ryzen zen 和 zen+ 中，我选择了前者，毕竟，现在散片 Ryzen 1700 才 890！新的配置单如下：

| 配件 | 型号 | 价格  |
| --- | --- | --- |
| CPU | Ryzen 1700 散片 | 板U套装 |
| 主板 | 华硕 Prime X370 Pro | 1509 |
| 内存 | 十铨冥神 DDR4 3000 16GB x 2 | 1139 |
| 显卡 | XFX RX570 4G 矿渣 | 299 |
| 电源 | 鑫谷 GP700G  600W 全模组电源 | 439 |
| 机箱 | 追风者 P300 | 249 |
| 散热 | 大镰刀 STB120 | 112 |
| 硬盘 | 西部数据 SN750 500GB | 559 |

以 4K 出头的价格组装完成了我的第一台 AMD 黑苹果，除了矿渣显卡，其他的都是全新件，而且等 Zen2 上市，2700X 价格崩盘的时候还可以升级一波 Zen+ 7nm. 

**AMD YES！**


## 装机（略）

## 装系统

装机完成之后，按照 [https://hack.slim.ovh/](https://hack.slim.ovh/) 提供的教程一步一步来就可以。

我装系统的时候偷了个懒。事情是这个样子的：

我去年的时候嫌弃 MacBook Pro 里的 256GB SSD不够用，就自己升级了 Intel 760P 1TB。后来笔记本的反光涂层大规模脱落 + 电池鼓包，趁五一假期有空，就送去了 GeniusBar 更换屏幕和电池。自己后换的 SSD 自然就被我拆下来了。在装机的时候，媳妇儿一句：`你装完系统还得配环境吧？` 提醒了我，我何不尝试直接引导原来 SSD 上的系统，所以，我只制作了一个 Clover 引导 U 盘，就完事儿了。。。


## 小问题解决

系统跑起来了，常用的应用也可以很正常地跑起来，不过还是有些小小的问题需要修复一下。

### 主板 9针 USB 接口无效

之前买的 Apple 无线网卡+蓝牙需要连接主板上的9针 USB 接口，然而我怎么插也没有反应。进入 Windows 系统中是可以正常识别硬件的，那就说明是 macOS 的问题。一通瞎捣鼓，通过增加 USB 端口限制补丁解决了，就是在 Clover Configurator 中启用下边几项（应该是其中一项有左右，懒得测试了）

![15572319696203](https://i.loli.net/2019/05/08/5cd23a7cd225f.jpg)

### 无法打开 jpg 图片

原因是在 10.14 系统中，如果有核心显卡的话，默认会使用核心显卡硬解码 JPG 图片。我在 Clover 仿冒的设备型号是 iMac 14,2，是有核心显卡的机型，然而 Ryzen 1700并没有核显，所以就 GG 了。解决方法有俩：

1. 仿冒没有核显的设备型号，比如 Mac Pro
2. 使用 [NoVPAJpeg](https://github.com/vulgo/NoVPAJpeg) 关闭 JPG 硬解码

我选择了第二种。

### “关于设备” 中 CPU 型号显示 Unknown
毕竟 Mac 没有使用 Ryzen CPU 的设备型号。修改方法：

使用 `Plistedit Pro` 或者其他可以编辑 bplist 文件的编辑器，打开 `/System/Library/PrivateFrameworks/AppleSystemInfo.framework/Versions/A/Resources/你系统的语言（比如 en.lproj）` 目录下的 `AppleSystemInfo.strings` 文件，把其中的 `<key>UnknownCPUKind</key>` 的值改成相应的 CPU 型号，比如 AMD Ryzen 1700。


### Docker 无法使用

偶尔还是需要用一下 docker 的，所以得想办法把它跑起来。修改方案是把 docker engine 跑在 virtualbox 里，具体方法如下：

1. 使用 docker-machine 命令创建新的 docker engine 环境：
     
    ```bash
    docker-machine create -d virtualbox --virtualbox-no-vtx-check default
    ```

2. 修改 docker 环境变量
    
    ```bash
    eval $(docker-machine env)
    ```

### (遇到再更新)
