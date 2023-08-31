---
title: "Kindle PaperWhite 3 扩容 32GB + 改无线充电"
date: 2022-05-19T00:54:26+08:00
categories: ["硬件"]
---

手里有个 2015 年买的 Kindle Paperwhite 3，看完的书没几本，主要用来『盖泡面』了。前段时间掏出来给它充了个电，顺便试着给它越了个狱。一不小心给系统搞得有点儿问题，卡死在一棵大树的 Logo 上。索性试着给它更换个更大容量的存储。因为基础不扎实，中间踩了很多坑，eMMC 拆焊 20 多次。不过好在最终还是搞定了，记录一下，供后来者参考。

<!-- more -->

![](https://pan.xnure.com/OneDrive/Pics/blog/16529654482282.jpg)

(焊盘干掉了一堆点，幸好都是空点)

## 插播一点 eMMC 的小知识

eMMC 标准中，将内部的 Flash Memory 划分为 4 类区域，最多可以支持 8 个硬件分区，如下图所示：

![](https://pan.xnure.com/OneDrive/Pics/blog/16529655302085.jpg)

一般情况下，Boot Area Partitions 和 RPMB Partition 的容量大小通常都为 4MB，部分芯片厂家也会提供配置的机会。General Purpose Partitions (GPP) 则在出厂时默认不被支持，即不存在这些分区，需要用户主动使能，并配置其所要使用的 GPP 的容量大小，GPP 的数量可以为 1 - 4 个，各个 GPP 的容量大小可以不一样。User Data Area (UDA) 的容量大小则为总容量大小减去其他分区所占用的容量

eMMC 的每一个硬件分区的存储空间都是独立编址的，即访问地址为 0 - partition size。具体的数据读写操作实际访问哪一个硬件分区，是由 eMMC 的 Extended CSD register 的 PARTITION_CONFIG Field 中 的 Bit[2:0]: PARTITION_ACCESS 决定的，用户可以通过配置 PARTITION_ACCESS 来切换硬件分区的访问。也就是说，用户在访问特定的分区前，需要先发送命令，配置 PARTITION_ACCESS，然后再发送相关的数据访问请求。

Kindle 自带的 4GB eMMC 芯片型号是 **THGBMBG5D1KBAIT**，为 eMMC 5.0 标准。Boot Area Partitions 大小都是 2MB，用于存储 bootloader。

> 如下图这种，使用 `6438SN` 转接 eMMC 的板子，只能读取 eMMC 中的 User Data Area，无法读取 boot 分区，也没法操作 boot 分区！
> ![](https://pan.xnure.com/OneDrive/Pics/blog/16529659813609.jpg)

## 备份

刚开始，我就是使用这种转接板对原有的 eMMC 进行备份，再恢复到新的 eMMC 上，但是刷入 u-boot 失败，也无法正确读取 NVRAM，错误日志如下：

```
Board: Unknown
Boot Reason: [ POR ]
Boot Device: NAND
Board Id:
S/N:
I2C:   ready
Invalid board id!  Can't determine system type for RAM init.. bailing!
DRAM:   0 kB
Using default environment

In:    serial
Out:   serial
Err:   serial

Warning: fail to get ext csd for MMC!
idme_get_var ERROR: couldn't switch to boot partition
POST done in 0 ms
Warning: fail to get ext csd for MMC!
idme_get_var ERROR: couldn't switch to boot partition
Battery voltage: 3995 mV
```

一度怀疑是 eMMC 质量/版本/厂商/写入姿势的问题，更换了 eMMC 4.5 的芯片，多次重试也不行。之后去了解了 eMMC 的规范才知道 boot 分区用这种方式不能读取和写入。

找到了问题那就继续找解决方案，通过转接的方式不可行，必须得让系统识别为 `mmc` 设备。我把目光放到了另一件吃灰神器：树莓派上。

首先掏出来树莓派 3B，它有两套 sd 接口，一套 sd0，连接 tf 卡槽。另一套在 GPIO 里，在 ALT3 下，GPIO 22-27 就是 `SDIO` 的几个 pin。然而，在 manjaro Linux 下每次尝试将 GPIO 23 切换到 ALT3，都会卡死整个系统。不得不放弃。

再掏出来树莓派 4B（差生文具多..），树莓派 4 支持从 USB 设备启动，所以之前我就给它装了个 2258H 的 U 盘，tf 接口自然就空闲下来了。直接飞线连接，成功访问到 eMMC 的 boot 分区！

接线图如下：

![](https://pan.xnure.com/OneDrive/Pics/blog/16528802144252.jpg)
![](https://pan.xnure.com/OneDrive/Pics/blog/16528865075422.jpg)
![](https://pan.xnure.com/OneDrive/Pics/blog/16529669604346.jpg)

执行如下命令备份所有分区内容：

```shell
sudo dd if=/dev/mmcblk0 of=kpw3_backup_mmc.img bs=1M
sudo dd if=/dev/mmcblk0boot0 of=boot0.img
sudo dd if=/dev/mmcblk0boot1 of=boot1.img
```

## 恢复

因为我有备份，所以就直接用备份干了。如果是因为 eMMC 损坏需要更换芯片，需要编译 u-boot，修正 NVRAM 变量等，具体可以参照参考文档 10、11。

恢复和备份差不多，还是用 `dd`, 命令如下：

```shell
sudo dd if=kpw3_backup_mmc.img of=/dev/mmcblk0 bs=1M && sync

# mmc 的 boot 分区在 Linux 下默认是只读的，要写入需要先改成 rw
echo 0 > /sys/block/mmcblk0boot0/force_ro
dd if=boot0.img  of=/dev/mmcblk0boot0

echo 0 > /sys/block/mmcblk0boot1/force_ro
dd if=boot1.img  of=/dev/mmcblk0boot1
```

之后，还要指定启动分区，修改 eMMC 启动分区需要安装 `mmc-utils`，之后执行 `sudo mmc bootpart enable 1 1 /dev/mmcblk0` 来指定从第1个 boot 分区启动。
然后可以执行 `sudo mmc extcsd read /dev/mmcblk0` 读取 extcsd 信息，修改成功会有如下信息：

```
Boot configuration bytes [PARTITION_CONFIG: 0x48]
 Boot Partition 1 enabled
 No access to boot partition
```

然后把 eMMC 干回去，升级就算完成了..
一半

因为用户分区是直接从之前的 4G eMMC 恢复的，虽然新的 eMMC 是 32GB 的，但是分区表里用户分区还是只有之前的 3GB，在使用之前还需要修正一下分区表。主要过程是进入 Kindle 的 diag 模式，获取 root shell，这个部分参考下边的 `越狱` 部分。获取 shell 后，使用 `fdisk /dev/mmcblk0` 对磁盘分区进行操作。

1. `fdisk -l`，获取 mmcblk0p4 的起始位置，我这里是 19521。
2. `fdisk /dev/mmcblk0`, `d` 删除第4个分区。
3. `n` 创建新分区，起始位置 19521，大小默认全部。
4. `c` 修改分区标识，选择 `b`(vfat)
5. `w` 保存修改

之后重启，正常加载 kernel，当出现 `Press [ENTER] for recovery menu...` 时，按下回车键，进入 Recovery 模式。

此时会有几个菜单选项（倒计时 10s 正常 boot，可以一直按回车键保持）：

```
3. Load MMC0 over USB storage
4. Erase MMC0
I. Initialize Partition Table (fdisk) and format FAT
O. Format and overwrite FAT partition
E. Export FAT partition
U. Update using update*.bin file on FAT partition
M. Update using update*.bin file on FAT partition of second MMC port
D. dmesg / kernel printk ring buffer.
Q. quit
```

输入 `I` 初始化分区表，格式化用户分区；输入 `E` 挂载为存储设备，连接 PC，把从 [Kindle E-Reader Software Updates - Amazon Customer Service](https://www.amazon.com/gp/help/customer/display.html?nodeId=GKMQC26VQQMM8XSW) 下载的系统文件放入根目录。完成后弹出设备，输入 `U` 更新系统。

更新完成后，设备就进入可用状态，可以正常使用了。接下来就是完成之前未竟的事业，给它越狱。

## 越狱

Kindle PaperWhite 3 可以直接通过 TTL 接口获取 root 权限，所以可以不关心是什么版本的系统。不过如果不想拆机或者是 KPW4 以上的没有 TTL 接口的机型，可以参考：[Tutorial WatchThis - Software Jailbreak for any Kindle <= 5.14.2 - MobileRead Forums](https://www.mobileread.com/forums/showthread.php?t=346037) 来越狱。

Kindle PaperWhite 3 的 TTL 测试点如下图：

![](https://pan.xnure.com/OneDrive/Pics/blog/16519965472876.jpg)

注意需要使用 1.8V 电平的 USB-TTL，3.3V 不可用。

越狱大致步骤如下：

1. 连接 TTL，重启 Kindle
2. 在u-boot 启动阶段，提示 `Hit any key to stop autoboot:` 倒计时结束前，按下任意键终端 u-boot 启动过程，进入 u-boot 命令行
3. 执行 `bootm 0xE41000` 进入诊断模式。（也可以 `idme bootmode diags`, 不过这个方法效果是持久的，需要再次进入 u-boot 命令行执行 `idme bootmode` 才能恢复正常启动）
4. 在诊断模式参考中，点选 `Reboot or Disable Diags`， 在之后的菜单中点选 `Exit to login prompt`，TTL 会提示登录，用户名 root, 密码使用如下 Python 代码计算得到：(序列号在 TTL 日志中可以获得)
    ```python
    import hashlib
    print("fiona%s"%hashlib.md5("序列号(无空格)\n".encode('utf-8')).hexdigest()[13:16])
    ```
5. 登录后，执行如下命令，移除 root 用户密码
    ```shell
    mkdir /tmp/mnt
    mount /dev/mmcblk0p1 /tmp/mnt
    vi /tmp/mnt/etc/passwd
    ```
6. 重启，正常启动系统后，在 TTL 终端按下回车会提示登录，输入用户名 root 回车即可。
7. Kindle 使用 USB 连接 PC，会自动挂载为存储设备。从参考文档 9 中下载 `K5 KindleBreak JailBreak`，将解压后的 **jb.sh** 等文件复制到 Kindle 根目录，TTL 执行 `bash jb.sh`，之后系统后自动重启，完成越狱。这一步的主要功能其实是将一个 developer public key 内置到系统目录中，以使之后的插件和自定义软件可以正常运行。
8. 建议在 TTL 终端执行 `passwd` 为 root 用户新增/修改密码，不然之后 SSH 连接可能会有问题。至此，TTL 的使命完成。
9. 为了方便连接和管理 Kindle 文件，推荐安装 `USBNetwork Hack` 和 [HTTP file server for KUAL](https://github.com/ngxson/hobby-kindle-http-file-server)，之后就可以通过网页管理文件，通过 USB 或者无线 SSH 登录到 Kindle 中。
10. 插件的安装方法见参考文档 9

## 无线充电

原材料是一个几毛钱的 iPhone 无线充电接收器：

![](https://pan.xnure.com/OneDrive/Pics/blog/16529636500255.jpg)

小心撕开外表皮的两层塑封（也可以不撕或者保留背面的，直接贴在 Kindle 的后壳上）

一共三个触点，分别是 **GND**、**+5V** 和 **ID**，分别接在 Kindle 的 MicroUSB 座上即可。成品如图：

![](https://pan.xnure.com/OneDrive/Pics/blog/16529635900937.jpg)

测试可以和 USB 口同时使用，充满也可以正常截止。

## 总结

至此，我获得了一台无线充电、32GB "海量"存储，可以 SSH 和远程管理的 "无线 Kindle"，虽然性能依旧羸弱，但至少比之前玩儿法还是多了不少的。希望我之后能用它多看基本书吧(狗头）。

## 参考文档

1. [us-17-Etemadieh-Hacking-Hardware-With-A-10-SD-Card-Reader-wp.pdf](https://www.blackhat.com/docs/us-17/wednesday/us-17-Etemadieh-Hacking-Hardware-With-A-$10-SD-Card-Reader-wp.pdf)
2. [SDIO at Raspberry Pi GPIO Pinout](https://pinout.xyz/pinout/sdio)
3. [RPi BCM2711 GPIOs - eLinux.org](https://elinux.org/RPi_BCM2711_GPIOs)
4. [https://www.kernel.org/doc/Documentation/mmc/mmc-dev-parts.txt](https://www.kernel.org/doc/Documentation/mmc/mmc-dev-parts.txt)
5. [Samsung eMMC moviNAND Product family eMMC Specification compatibility](https://web.archive.org/web/20200120234346/http://web3032.sh1.magic2008.cn.m1.magic2008.cn/uFile/3032/201144131450191.pdf)
6. [Working with eMMC](https://www.embeddedartists.com/wp-content/uploads/2020/04/Working_with_eMMC.pdf)
7. [eMMC 分区管理 · Linux Kernel Internals](https://linux.codingbelief.com/zh/storage/flash_memory/emmc/emmc_partitions.html)
8. [Jailbreaking My Kindle Paperwhite 3 | deCryptronics](https://decryptronics.github.io/electronics/2020/07/12/jailbreaking-my-kindle-paperwhite-3.html)
9. [Tools Snapshots of NiLuJe's hacks - MobileRead Forums](https://www.mobileread.com/forums/showthread.php?t=225030)
10. [Kindle Paperwhite 2 强行救砖(1) - module ZephRay;](https://web.archive.org/web/20210116081307/https://www.zephray.me/post/kpw2_debrick_1)
11. [Kindle Paperwhite 2 强行救砖(2) - module ZephRay;](https://web.archive.org/web/20210117084623/https://www.zephray.me/post/kpw2_debrick_2)