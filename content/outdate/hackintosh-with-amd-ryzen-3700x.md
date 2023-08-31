--- 
title: "喜提新开(you)发(xi)机"
date: 2019-12-22T00:42:33+08:00
tags: [hackintosh]
categories: ["硬件"]
---

上次配置的 AMD 黑苹果放到公司，替代 Macbook Pro 2015 做日常开发了，虽然主频只有 3.8Ghz，但是 8C16T，32GB 内存，性能还是吊打 Macbook Pro 的 2.2G 4C8T，16GB的。

家里的老台式还是 2014 年的时候配置的，当时是通过开源夏令营获得了 4400 块的奖金。研究了好几天配置了一台 Core i5 4590 4C4T + 8GB 内存的 MATX 台式。虽然后来内存加到了 16GB, 也添加了 AMD RX470D 显卡，但在搞点儿开发的时候，还是有些力不从心。所以萌生了配置一台新设备的想法。

<!--more-->

最初预想的配置：

```
主板：MSI MEG X570 ACE
CPU：AMD Ryzen 3900X  
内存：DDR4 3600 16GB X2
散热：U12/D15顶级风冷
电源：AG-850M
显卡：AMD 5700XT
硬盘：SN750 500GB + P4510 2TB + MX500 1TB（已有）
```

然而现实很骨干，并没有那么多预算，最终的配置是：

```
主板：ASUS Prime X579 Pro
CPU：AMD Ryzen 3700X  
内存：科赋 DDR4 3200 16GB X2
散热：盒装 CPU 自带
电源：AJ-850M
显卡：XFX 470D
硬盘：SN750 500GB + P4510 2TB + MX500 1TB（已有）
```

本着早买早享受的原则，11.1 京东下单，内存则是咸鱼购入。

## 超频
买了 AMD 不超频有点儿不合适，PBO 1s 真男人看着难受。

### CPU
1.3V 超 4.2 GHz，单烤 PBO 半小时没有问题，懒得仔细调了

### 内存
主板刚到的时候，用的是 1003 的 BIOS，内存可以超到 3800 MHz @C16。更新了 10月31日发布的 1004 之后，这个频率就开不了机了。。只能退而求其次，3666，详细参数如下：

* 时序： 16-20-21-20-38
* 小参：只改了 tRFC1、tRFC2、tRFC4为 494，367，226

内存延迟 `68.2ns`，还可以，比默认的 90 多强不少

## 系统
Windows 自不必说，偶尔还是会玩儿一会儿的 CS:GO，主要记录一下在这台 PC 安装 Hackintosh 遇到的问题。

AMD 平台在 [AMD_Vanilla](https://github.com/AMD-OSX/AMD_Vanilla) 的加持下，安装的难以程度已经可以与 Intel 平台的相媲美，甚至会更方便一些。我之前使用的 AMD 1700 Hackintosh 安装过程特别顺利，但在这台 3700X 的设备上碰到了不少的问题。主要有：

### Clover 无法引导
在安装过程中，Clover 始终无法引导，卡在 `.........` 一排省略号上，貌似是 `AptioMemoryFix` 相关的 kext 的问题，一直找不到解决方案。之后尝试了国外网友分享的他的配置，基于 OpenCore，可以引导 macOS 10.15.1，并在此基础上加了自己的一些配置，详见最下方的 gayhub 链接。

### P4510 无法识别/使用
之前在大船靠岸的时候，1500 块上车了一块 Intel 的 P4510 SSD，容量 2TB，U.2 接口，通过 PCIE3.0 x 16 的转接卡连接在计算机上。上边安装了 Windows 10 1909 版本。但在 macOS 中，此硬盘不仅不能被当做系统盘，连数据盘都不能做，只要在系统启动过程中，识别到此硬盘，就会导致 kernel panic。

解决方案：参考：[HackrNVMeFamily co-existence with IONVMeFamily using class-code spoof](tonymacx86.com/threads/guide-hackrnvmefamily-co-existence-with-ionvmefamily-using-class-code-spoof.210316/)，通过 SSDT 补丁的方式，在 macOS 下屏蔽此硬件，成功进入系统。

### 无法进入 BIOS 设置界面
这个问题从最开始就困扰着我，直到昨天的偶尔一次实验才证明这个问题和 OpenCore 相关。。

问题的表现是这样的，开机的时候提示 F2 或者 DEL 进入 BIOS 设置，但是按完之后屏幕一直只显示黑色北京，无法 BIOS 设置。系统启动，F8 选择启动硬盘功能不收影响。原来一直以为是大船 SSD 导致的这个问题（有一次拔掉硬盘后成功进入了）。直到昨天重置 BIOS 设置后，进入 Windows 不影响再次进入 BIOS，但是进入 Hackintosh 之后就会触发此问题，于是尝试 OpenCore 的 `reset NVRAM` 选项，问题解决。

### 欧版 Magic Keyboard 2 键位问题
为了剩 100 块钱，买了 欧版的 Magic Keyboard 2，但是键位与英版和国行有较大差异，主要有：

1. 数字区最左侧，第二排第一个键，不是 `~`，而是一个 `§`
2. 左 shift 和 `z` 之间还有一个键，是 `~`...

虽然能用，但是和普通键盘差异比较大，总是按错。。硬件方面解决起来难度比较大，所以通过软件层面解决：把相应的按键映射到我们想要的按键上。这里用到一款开源工具：`Karabiner-Elements`，可以很方便的把某个按键映射到另一个按键上。我主要替换的有：

1. 把原 `§` 替换成 `~`，这个按键就和正常键盘一致了。这俩键在 `Karabiner-Elements` 里的名称分别是：`non_us_backslash` 和 `grave_accent_and_tilde`
2. 把 `~` 替换成左 `shift`，这样 `z` 左右的都是 shift 了，虽然是两个分开的按键，总好过按错。。

这样就基本完美了，除了 `|` 键在 `'` 和 `enter` 之间，回车的时候，小拇指的移动距离相比之前更远一些，习惯了一下，也还可以。


## 参考连接
1. [默频使用不好吗？锐龙三代3700X的内存超频详细教程](https://post.smzdm.com/p/a99ve07e/)
2. [HackrNVMeFamily co-existence with IONVMeFamily using class-code spoof](tonymacx86.com/threads/guide-hackrnvmefamily-co-existence-with-ionvmefamily-using-class-code-spoof.210316/)
3. [AMD_Vanilla](https://github.com/AMD-OSX/AMD_Vanilla)
4. [我的配置文件](https://github.com/tylinux/hackintosh-ASUS-X570-Prime-Plus-3700x)
