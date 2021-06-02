---
title: "也折腾博云物联辣鸡网络摄像头（上）"
date: 2021-06-03T00:54:26+08:00
categories: ["硬件"]
---


> 相关资源文件可至：https://github.com/tylinux/HackBoyunIPCamera 下载

前几天看了 [用垃圾网络摄像头构建的家庭直播系统](https://www.mydigit.cn/forum.php?mod=viewthread&tid=255164) 这篇帖子，也想试着玩儿玩儿网络摄像头，就买了帖子里提到的 38 俩包邮的博云物联摄像头。

到手拆机：

![IMG_0962](https://i.loli.net/2021/06/03/ghirFEwB4uPUs7p.jpg)

海思 HI3518CV100 的主控芯片
![IMG_0963](https://i.loli.net/2021/06/03/EIW3bNsHSCxKmuP.jpg)

瑞昱 RTL8188ETV WiFi 模块
![](https://i.loli.net/2021/06/03/1SRh3ouyecbUHv7.jpg)

开搞。

## TTL

第一步是先找到 TTL 接口，这样就能观察启动过程，刷完系统也好辨别是否工作正常，是哪里出了问题。
思路如下：

* 找明确标记为 RX, TX 的测试点
* 找比较可疑的两个、三个、或者四个并排的测试点
* 终极方案：把主控吹下来，按照 datasheet 里标记的 RX，TX 引脚找对应的测试点

很幸运，板子背面就有三个一排的可疑测试点，推测可能就是 TTL 接口，用万用表很轻松找到 GND，RX，TX 则通过上电时的电压变化来区分，因为上电时 TX 会有比较多的信息要输出，所以电压变化会比较大。

按照猜想焊上，连接 PC，波特率 115200，上电验证，成功~

TTL 测试点定义：

![](https://i.loli.net/2021/06/03/PBSalgxLQeyr5Gh.jpg)

启动日志：

```
U-Boot 2010.06-dirty (Feb 06 2015 - 19:53:21)

Check spi flash controller v350... Found
Spi(cs1) ID: 0xEF 0x40 0x17 0x00 0x00 0x00
Spi(cs1): Block:64KB Chip:8MB Name:"W25Q64FV"
In:    serial
Out:   serial
Err:   serial
Hit any key to stop autoboot:  0 
8192 KiB hi_sfc at 0:0 is now current device

## Booting kernel from Legacy Image at 82000000 ...
   Image Name:   Linux-3.0.8
   Image Type:   ARM Linux Kernel Image (uncompressed)
   Data Size:    1707544 Bytes = 1.6 MiB
   Load Address: 80008000
   Entry Point:  80008000
   Loading Kernel Image ... OK
OK

Starting kernel ...

Uncompressing Linux... done, booting the kernel.
Linux version 3.0.8 (root@skyi) (gcc version 4.4.1 (Hisilicon_v100(gcc4.4-290+uclibc_0.9.32.1+eabi+linuxpthread)) ) #163 Tue Nov 18 10:43:40 CST 2014
CPU: ARM926EJ-S [41069265] revision 5 (ARMv5TEJ), cr=00053177
CPU: VIVT data cache, VIVT instruction cache
Machine: hi3518
Ignoring unrecognised tag 0x726d6d73
Memory policy: ECC disabled, Data cache writeback
AXI bus clock 200000000.
Built 1 zonelists in Zone order, mobility grouping on.  Total pages: 10160
Kernel command line: mem=40M console=ttyAMA0,115200 root=/dev/mtdblock2 mtdparts=hi_sfc:256K(boot),1792K(kernel),5120K(rootfs),448K(ui),576K(conf)
PID hash table entries: 256 (order: -2, 1024 bytes)
Dentry cache hash table entries: 8192 (order: 3, 32768 bytes)
Inode-cache hash table entries: 4096 (order: 2, 16384 bytes)
Memory: 40MB = 40MB total
Memory: 36132k/36132k available, 4828k reserved, 0K highmem
Virtual kernel memory layout:
    vector  : 0xffff0000 - 0xffff1000   (   4 kB)
    fixmap  : 0xfff00000 - 0xfffe0000   ( 896 kB)
    DMA     : 0xffc00000 - 0xffe00000   (   2 MB)
    vmalloc : 0xc3000000 - 0xfe000000   ( 944 MB)
    lowmem  : 0xc0000000 - 0xc2800000   (  40 MB)
    modules : 0xbf000000 - 0xc0000000   (  16 MB)
      .init : 0xc0008000 - 0xc0020000   (  96 kB)
      .text : 0xc0020000 - 0xc0406000   (3992 kB)
      .data : 0xc0406000 - 0xc0435560   ( 190 kB)
       .bss : 0xc0435584 - 0xc0450bd8   ( 110 kB)
SLUB: Genslabs=13, HWalign=32, Order=0-3, MinObjects=0, CPUs=1, Nodes=1
NR_IRQS:128 nr_irqs:128 128
sched_clock: 32 bits at 100MHz, resolution 10ns, wraps every 42949ms
Console: colour dummy device 80x30
Calibrating delay loop... 218.72 BogoMIPS (lpj=1093632)
pid_max: default: 32768 minimum: 301
Mount-cache hash table entries: 512
CPU: Testing write buffer coherency: ok
NET: Registered protocol family 16
Serial: AMBA PL011 UART driver
uart:0: ttyAMA0 at MMIO 0x20080000 (irq = 5) is a PL011 rev2
console [ttyAMA0] enabled
uart:1: ttyAMA1 at MMIO 0x20090000 (irq = 5) is a PL011 rev2
bio: create slab <bio-0> at 0
SCSI subsystem initialized
usbcore: registered new interface driver usbfs
usbcore: registered new interface driver hub
usbcore: registered new device driver usb
cfg80211: Calling CRDA to update world regulatory domain
Switching to clocksource timer1
NET: Registered protocol family 2
IP route cache hash table entries: 1024 (order: 0, 4096 bytes)
TCP established hash table entries: 2048 (order: 2, 16384 bytes)
TCP bind hash table entries: 2048 (order: 1, 8192 bytes)
TCP: Hash tables configured (established 2048 bind 2048)
TCP reno registered
UDP hash table entries: 256 (order: 0, 4096 bytes)
UDP-Lite hash table entries: 256 (order: 0, 4096 bytes)
NET: Registered protocol family 1
squashfs: version 4.0 (2009/01/31) Phillip Lougher
JFFS2 version 2.2. (NAND) © 2001-2006 Red Hat, Inc.
fuse init (API version 7.16)
msgmni has been set to 70
Block layer SCSI generic (bsg) driver version 0.4 loaded (major 253)
io scheduler noop registered
io scheduler deadline registered (default)
io scheduler cfq registered
brd: module loaded
wifi power on
wifi_power driver init
adc init OK !
encrypt driver init
hi_rfled driver probe OK !
higpio driver initialize.
Spi id table Version 1.22
Spi(cs1) ID: 0xEF 0x40 0x17 0x00 0x00 0x00
SPI FLASH start_up_mode is 3 Bytes
Spi(cs1): 
Block:64KB 
Chip:8MB 
Name:"W25Q64FV"
spi size: 8MB
chip num: 1
5 cmdlinepart partitions found on MTD device hi_sfc
Creating 5 MTD partitions on "hi_sfc":
0x000000000000-0x000000040000 : "boot"
0x000000040000-0x000000200000 : "kernel"
0x000000200000-0x000000700000 : "rootfs"
0x000000700000-0x000000770000 : "ui"
0x000000770000-0x000000800000 : "conf"
Fixed MDIO Bus: probed
RTL871X: module init start
RTL871X: rtl8188eu v4.3.0.7_12758.20141114
RTL871X: build time: Sep 17 2015 17:18:55
usbcore: registered new interface driver rtl8188eu
RTL871X: module init ret=0
usbmon: debugfs is not available
ehci_hcd: USB 2.0 'Enhanced' Host Controller (EHCI) Driver
hiusb-ehci hiusb-ehci.0: HIUSB EHCI
hiusb-ehci hiusb-ehci.0: new USB bus registered, assigned bus number 1
hiusb-ehci hiusb-ehci.0: irq 15, io mem 0x100b0000
hiusb-ehci hiusb-ehci.0: USB 0.0 started, EHCI 1.00
hub 1-0:1.0: USB hub found
hub 1-0:1.0: 1 port detected
ohci_hcd: USB 1.1 'Open' Host Controller (OHCI) Driver
hiusb-ohci hiusb-ohci.0: HIUSB OHCI
hiusb-ohci hiusb-ohci.0: new USB bus registered, assigned bus number 2
hiusb-ohci hiusb-ohci.0: irq 16, io mem 0x100a0000
hub 2-0:1.0: USB hub found
hub 2-0:1.0: 1 port detected
input: higpio-keys as /devices/platform/higpio-keys/input/input0
Hisilicon Watchdog Timer: 0.01 initialized. default_margin=15 sec (nowayout= 1, nodeamon= 1)
usbcore: registered new interface driver usbhid
usbhid: USB HID core driver
TCP cubic registered
NET: Registered protocol family 17
registered taskstats version 1
drivers/rtc/hctosys.c: unable to open rtc device (rtc0)
�VFS: Mounted root (squashfs filesystem) readonly on device 31:2.
Freeing init memory: 96K
usb 1-1: new high speed USB device number 2 using hiusb-ehci
init started: BusyBox v1.20.2 (2015-06-12 14:53:47 CST)
starting pid 459, tty '': '/etc/init.d/rcS'
bFWReady == _FALSE call reset 8051...

            _ _ _ _ _ _ _ _ _ _ _ _
            \  _  _   _  _ _ ___
            / /__/ \ |_/
           / __   /  -  _ ___
          / /  / /  / /
  _ _ _ _/ /  /  \_/  \_ ______
___________\___\__________________

RTL871X: rtw_ndev_init(wlan0)
RTL871X: rtw_ndev_init(wlan1)
#mount all.....
#Starting mdev.....
mount: mounting none on /proc/bus/usb failed: No such file or directory
Hisilicon Media Memory Zone Manager
hi3518_base: module license 'Proprietary' taints kernel.
Disabling lock debugging due to kernel taint
Hisilicon UMAP device driver interface: v3.00
pa:82800000, va:c3280000
load sys.ko ...OK!
load viu.ko ...OK!
ISP Mod init!
load vpss.ko ....OK!
load venc.ko ...OK!
load group.ko ...OK!
load chnl.ko ...OK!
load h264e.ko ...OK!
load jpege.ko ...OK!
load rc.ko ...OK!
load region.ko ....OK!
load vda.ko ....OK!
hi_i2c init is ok!
Kernel: ssp initial ok!
acodec inited!
insert audio
==== Your input Sensor type is ov9712 ====
[RCS]: /etc/init.d/S00devs
mknod: /dev/console: File exists
mknod: /dev/ttyAMA0: File exists
mknod: /dev/ttyAMA1: File exists
mknod: /dev/null: File exists
[RCS]: /etc/init.d/S01udev
udevd (626): /proc/626/oom_adj is deprecated, please use /proc/626/oom_score_adj instead.
[RCS]: /etc/init.d/S80network
starting pid 630, tty '/dev/ttyS000': '/bin/login'
IPCAM login: ==> rtl8188e_iol_efuse_patch 
open higpio device success.
RTL871X: nolinked power save enter
open higpio device success.
wifi_enable == 0
==> rtl8188e_iol_efuse_patch 
RTL871X: nolinked power save leave
open higpio device success.
RTL871X: nolinked power save enter
==> rtl8188e_iol_efuse_patch 
RTL871X: nolinked power save leave
RTL871X: assoc success

process '/bin/login' (pid 630) exited. Scheduling for restart.
starting pid 977, tty '/dev/ttyS000': '/bin/login'
```

结合日志信息，可知该网络摄像头配置如下：

| Feature                 | Specification                     |
| :---------------------- | :-------------------------------- |
| SoC                     | HI3518CV100, ARM926EJ-S@100Mh     |
| Memory                  | 40 MB                             |
| Flash                   | W25Q64FV 8MB NOR Flash            |
| Sensor                  | OV9712 720P/30Hz image Sensor     |
| WiFi Module             | Realtek RTL8188ETV 802.11 b/g/n   |


## OpenIPC

搞定了 TTL ，就可以尝试刷成 OpenIPC 了，OpenIPC 官方 [网站](https://openipc.org/firmware/) 或者官方 [Github Repo](https://github.com/OpenIPC/chaos_calmer) 上下载 Hi3518CV100 的 u-boot、 kernel 等资源

![](https://i.loli.net/2021/06/03/rn52GfSpLthcA8o.jpg)

按照 OpenIPC 文档上的步骤：

1. 把下载好的 u-boot,kernle, rootfs 放到格式化成 fat32 的 TF 卡里: OK
2. 上电后在 TTL Console 里按回车进入 u-boot 的终端：OK
3. 执行 `sf probe 0` 选定 SPI Flash 设备: OK
4. `mw.b 0x82000000 ff 1000000; fatload mmc 0:1 0x82000000 openwrt-hi35xx-XXXXX-u-boot.bin` 从 TF 卡加载 u-boot 镜像: X

问题来了，这原来的 u-boot 版本太老了，没有 `mmc` 这个命令，没法读写 TF 卡。替代方案是用 `tftp`，但是这也没有网线，u-boot 不支持无线。没啥好招了，只能把 flash 吹下来，上编程器了。（没有编程器架子 ಥ_ಥ）

Flash 上编程器之后，首先备份一下，有备无患。命令如下：

```bash
ch341prog -v -tt -r hi3518cv100.bin
```

然后使用 `binwalk hi3518cv100.bin`，看一下原来 flash 地址布局：

```
DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
123156        0x1E114         CRC32 polynomial table, little endian
262144        0x40000         uImage header, header size: 64 bytes, header CRC: 0x9A61CF8D, created: 2015-10-14 12:42:37, image size: 1707544 bytes, Data Address: 0x80008000, Entry Point: 0x80008000, data CRC: 0x48A1D0B0, OS: Linux, CPU: ARM, image type: OS Kernel Image, compression type: none, image name: "Linux-3.0.8"
262208        0x40040         Linux kernel ARM boot executable zImage (little-endian)
272652        0x4290C         LZMA compressed data, properties: 0x5D, dictionary size: 67108864 bytes, uncompressed size: -1 bytes
2097152       0x200000        Squashfs filesystem, little endian, version 4.0, compression:xz, size: 4654288 bytes, 450 inodes, blocksize: 131072 bytes, created: 2015-10-14 14:39:06
7340032       0x700000        Squashfs filesystem, little endian, version 4.0, compression:xz, size: 219138 bytes, 161 inodes, blocksize: 131072 bytes, created: 2015-09-01 13:38:07
...
```

可以看出 flash 内存空间分 4 部分，分别是：

| 地址区间                 | 大小        | 内容                     |
| :---------------------- |:---------- | :---------------------- |
| 0x0 ~ 0x3FFFF           | 256 KB     | u-boot                  |
| 0x40000 ~ 0x1FFFFF      | 1.75 MB    | Linux Kernel Image      |
| 0x200000 ~ 0x6FFFFF     | 5 MB        | RootFS                  |
| 0x700000 ~ 0x7FFFFF     | 1 MB        | Web 资源                 |

这就很简单了:

1. 编程器清空 flash：`ch341prog -v -tt -e`
2. 刷写 `openwrt-hi35xx-18cv100-u-boot.bin`: `ch341prog -v -tt -w openwrt-hi35xx-18cv100-u-boot.bin`
3. 把 flash 从编程器上吹下来，再吹回板子上
4. 上电！

GG

TTL 终端没有任何反应。。重试也不行。。

* flash 吹坏了？拆装 * 3
* u-boot 文件用错了？拆装 * 3
* 编程器没操作对？拆装 * 3
* 没有 kernel 启动不了？拆装 * 3

感觉再拆下去，编程器转接板，flash，摄像头至少得坏一个，赶紧下单买了个编程器夹，顺便买了几个编程器座子，焊上之后长这样：

![IMG_0980](https://i.loli.net/2021/06/03/4KsahMRTpmIY1gt.jpg)

突然想到，有没有可能下载的 u-boot 本身是不适配这个板子的，因为 bootloader 是和硬件强相关的，可能 SoC 一样但是其他硬件不一样，导致 u-boot 起不来。

bootloader 的主要作用就是枚举硬件，接着引导操作系统，所以理论上用原有的 u-boot 也是可以启动 OpenIPC 的 Linux Kernel 的。说干就干：

OpenIPC 提供的文件只有三个，没有原版 Web 资源文件那个 Squashfs 镜像，所以只要把原版的 u-boot，OpenIPC 的 Linux Kernel Image以及对应的 RootFS，按照起始地址
`0x0`, `0x40000`, `0x200000` 合并成一个二进制文件即可。

### 提取原版 u-boot

```
# 从备份的镜像中提取前 256KB 内容到 u-boot.bin
dd if=./hi3518cv100.bin of=u-boot.bin bs=1024 count=256
```

### 准备 Linux Kernle Image
OpenIPC 提供的 uImage 文件大小为 1.3 MB，不足 1.75 MB，可以通过如下方式构造出来：

```
# 创建一个 1.75 MB 的空文件
dd if=/dev/zero of=./kernel.bin bs=1k count=1792

# 把 openwrt-hi35xx-18cv100-default-uImage 写入到 kernel.bin 
dd if=openwrt-hi35xx-18cv100-default-uImage of=kernel.bin conv=notrunc
```

这样就有一个 1.75 MB 包含 uImage 的二进制文件了

因为 RootFS 是最后一个文件，虽然它的大小也不足剩余的 6MB，但是可以不用管，直接把它和前边的两个文件拼接到一起就行：

```
# 拼接
cat u-boot.bin kernel.bin openwrt-hi35xx-18cv100-default-root.squashfs > new.bin
```

搞定，再用 `binwalk` 验证一下起始地址：

```
DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
123156        0x1E114         CRC32 polynomial table, little endian
262144        0x40000         uImage header, header size: 64 bytes, header CRC: 0x20BB4D30, created: 2021-05-23 19:52:11, image size: 1315576 bytes, Data Address: 0x80008000, Entry Point: 0x80008000, data CRC: 0x2C1D389D, OS: Linux, CPU: ARM, image type: OS Kernel Image, compression type: none, image name: "OpenIPC.org | Linux-3.0.8"
262208        0x40040         Linux kernel ARM boot executable zImage (little-endian)
270076        0x41EFC         LZMA compressed data, properties: 0x6D, dictionary size: 1048576 bytes, uncompressed size: -1 bytes
2097152       0x200000        Squashfs filesystem, little endian, version 4.0, compression:xz, size: 4000748 bytes, 1628 inodes, blocksize: 262144 bytes, created: 2021-05-23 19:52:12
```

没有问题 ~ 烧录到板子上，上电，开机成功~日志如下：

```
U-Boot 2010.06-dirty (Feb 06 2015 - 19:53:21)

Check spi flash controller v350... Found
Spi(cs1) ID: 0xEF 0x40 0x17 0x00 0x00 0x00
Spi(cs1): Block:64KB Chip:8MB Name:"W25Q64FV"
In:    serial
Out:   serial
Err:   serial
Hit any key to stop autoboot:  0 
8192 KiB hi_sfc at 0:0 is now current device

## Booting kernel from Legacy Image at 82000000 ...
   Image Name:   OpenIPC.org | Linux-3.0.8
   Image Type:   ARM Linux Kernel Image (uncompressed)
   Data Size:    1315576 Bytes = 1.3 MiB
   Load Address: 80008000
   Entry Point:  80008000
   Loading Kernel Image ... OK
OK

Starting kernel ...

Uncompressing Linux... done, booting the kernel.
[    0.000000] Linux version 3.0.8 (runner@fv-az32-571) (gcc version 4.8.3 (OpenWrt/Linaro GCC 4.8-2014.04 latest-174-gf2830dcd3b) ) #1 Sun May 23 19:52:08 UTC 2021
[    0.000000] CPU: ARM926EJ-S [41069265] revision 5 (ARMv5TEJ), cr=00053177
[    0.000000] CPU: VIVT data cache, VIVT instruction cache
[    0.000000] Machine: hi3518
[    0.000000] Memory policy: ECC disabled, Data cache writeback
[    0.000000] AXI bus clock 200000000.
[    0.000000] Built 1 zonelists in Zone order, mobility grouping on.  Total pages: 10160
[    0.000000] Kernel command line: mem=40M console=ttyAMA0,115200 root=/dev/mtdblock2 mtdparts=hi_sfc:256K(boot),1792K(kernel),5120K(rootfs),448K(ui),576K(conf)
[    0.000000] PID hash table entries: 256 (order: -2, 1024 bytes)
[    0.000000] Dentry cache hash table entries: 8192 (order: 3, 32768 bytes)
[    0.000000] Inode-cache hash table entries: 4096 (order: 2, 16384 bytes)
[    0.000000] Memory: 40MB = 40MB total
[    0.000000] Memory: 37060k/37060k available, 3900k reserved, 0K highmem
[    0.000000] Virtual kernel memory layout:
[    0.000000]     vector  : 0xffff0000 - 0xffff1000   (   4 kB)
[    0.000000]     fixmap  : 0xfff00000 - 0xfffe0000   ( 896 kB)
[    0.000000]     DMA     : 0xffc00000 - 0xffe00000   (   2 MB)
[    0.000000]     vmalloc : 0xc3000000 - 0xfe000000   ( 944 MB)
[    0.000000]     lowmem  : 0xc0000000 - 0xc2800000   (  40 MB)
[    0.000000]     modules : 0xbf000000 - 0xc0000000   (  16 MB)
[    0.000000]       .init : 0xc0008000 - 0xc0024000   ( 112 kB)
[    0.000000]       .text : 0xc0024000 - 0xc0340000   (3184 kB)
[    0.000000]       .data : 0xc0340000 - 0xc0357220   (  93 kB)
[    0.000000]        .bss : 0xc0357244 - 0xc03680f8   (  68 kB)
[    0.000000] SLUB: Genslabs=13, HWalign=32, Order=0-3, MinObjects=0, CPUs=1, Nodes=1
[    0.000000] NR_IRQS:128 nr_irqs:128 128
[    0.000000] sched_clock: 32 bits at 100MHz, resolution 10ns, wraps every 42949ms
[    0.000070] Calibrating delay loop... 218.72 BogoMIPS (lpj=1093632)
[    0.070079] pid_max: default: 32768 minimum: 301
[    0.070511] Mount-cache hash table entries: 512
[    0.071726] CPU: Testing write buffer coherency: ok
[    0.076423] NET: Registered protocol family 16
[    0.091380] Serial: AMBA PL011 UART driver
[    0.091717] uart:0: ttyAMA0 at MMIO 0x20080000 (irq = 5) is a PL011 rev2
[    0.297458] console [ttyAMA0] enabled
[    0.302158] uart:1: ttyAMA1 at MMIO 0x20090000 (irq = 5) is a PL011 rev2
[    0.353261] bio: create slab <bio-0> at 0
[    0.374788] SCSI subsystem initialized
[    0.382197] usbcore: registered new interface driver usbfs
[    0.388460] usbcore: registered new interface driver hub
[    0.394855] usbcore: registered new device driver usb
[    0.407858] cfg80211: Calling CRDA to update world regulatory domain
[    0.415016] Switching to clocksource timer1
[    0.428448] NET: Registered protocol family 2
[    0.433192] IP route cache hash table entries: 1024 (order: 0, 4096 bytes)
[    0.440812] TCP established hash table entries: 2048 (order: 2, 16384 bytes)
[    0.448263] TCP bind hash table entries: 2048 (order: 1, 8192 bytes)
[    0.454878] TCP: Hash tables configured (established 2048 bind 2048)
[    0.461279] TCP reno registered
[    0.464454] UDP hash table entries: 256 (order: 0, 4096 bytes)
[    0.470442] UDP-Lite hash table entries: 256 (order: 0, 4096 bytes)
[    0.477471] NET: Registered protocol family 1
[    0.482799] RPC: Registered named UNIX socket transport module.
[    0.488744] RPC: Registered udp transport module.
[    0.493542] RPC: Registered tcp transport module.
[    0.498259] RPC: Registered tcp NFSv4.1 backchannel transport module.
[    0.553102] squashfs: version 4.0 (2009/01/31) Phillip Lougher
[    0.562431] JFFS2 version 2.2. (NAND) (SUMMARY)  © 2001-2006 Red Hat, Inc.
[    0.573927] msgmni has been set to 72
[    0.578721] io scheduler noop registered
[    0.582758] io scheduler deadline registered (default)
[    0.588234] io scheduler cfq registered
[    0.625934] brd: module loaded
[    0.633878] Spi id table Version 1.22
[    0.639204] Spi(cs1) ID: 0xEF 0x40 0x17 0x00 0x00 0x00
[    0.656119] SPI FLASH start_up_mode is 3 Bytes
[    0.660642] Spi(cs1): 
[    0.662842] Block:64KB 
[    0.665291] Chip:8MB 
[    0.667562] Name:"W25Q64FV"
[    0.670581] spi size: 8MB
[    0.673205] chip num: 1
[    0.675699] 5 cmdlinepart partitions found on MTD device hi_sfc
[    0.681665] Creating 5 MTD partitions on "hi_sfc":
[    0.686482] 0x000000000000-0x000000040000 : "boot"
[    0.695533] 0x000000040000-0x000000200000 : "kernel"
[    0.704726] 0x000000200000-0x000000700000 : "rootfs"
[    0.714055] 0x000000700000-0x000000770000 : "ui"
[    0.723055] 0x000000770000-0x000000800000 : "conf"
[    0.751933] Fixed MDIO Bus: probed
[    1.171386] himii: probed
[    1.299903] ehci_hcd: USB 2.0 'Enhanced' Host Controller (EHCI) Driver
[    1.306942] hiusb-ehci hiusb-ehci.0: HIUSB EHCI
[    1.312790] hiusb-ehci hiusb-ehci.0: new USB bus registered, assigned bus number 1
[    1.320817] hiusb-ehci hiusb-ehci.0: irq 15, io mem 0x100b0000
[    1.340127] hiusb-ehci hiusb-ehci.0: USB 0.0 started, EHCI 1.00
[    1.348445] hub 1-0:1.0: USB hub found
[    1.352363] hub 1-0:1.0: 1 port detected
[    1.359385] platform rtc-hi3518: rtc core: registered rtc-hi3518 as rtc0
[    1.372787] TCP cubic registered
[    1.376049] NET: Registered protocol family 17
[    1.380926] 802.1Q VLAN Support v1.8
[    1.387044] registered taskstats version 1
[    1.391516] platform rtc-hi3518: setting system clock to 2015-11-22 14:02:45 UTC (1448200965)
�[    1.410181] List of all partitions:
[    1.413746] 1f00             256 mtdblock0  (driver?)
[    1.418820] 1f01            1792 mtdblock1  (driver?)
[    1.423982] 1f02            5120 mtdblock2  (driver?)
[    1.429051] 1f03             448 mtdblock3  (driver?)
[    1.434172] 1f04             576 mtdblock4  (driver?)
[    1.439242] f000             256 romblock0  (driver?)
[    1.444350] f001            1792 romblock1  (driver?)
[    1.449419] f002            5120 romblock2  (driver?)
[    1.454545] f003             448 romblock3  (driver?)
[    1.459619] f004             576 romblock4  (driver?)
[    1.464714] No filesystem could mount root, tried:  squashfs
[    1.470437] Kernel panic - not syncing: VFS: Unable to mount root fs on unknown-block(31,2)
[    1.478788] Backtrace: 
[    1.481333] [<c0028680>] (dump_backtrace+0x0/0x10c) from [<c028c36c>] (dump_stack+0x18/0x1c)
[    1.489779]  r6:00008000 r5:c1979009 r4:c02fb840 r3:c034679c
[    1.495549] [<c028c354>] (dump_stack+0x0/0x1c) from [<c028c4b4>] (panic+0x68/0x17c)
[    1.503284] [<c028c44c>] (panic+0x0/0x17c) from [<c0008e58>] (mount_block_root+0x1e0/0x220)
[    1.511678]  r3:c201ff04 r2:00000020 r1:c201ff38 r0:c02fb840
[    1.517368]  r7:c00201a4
[    1.519936] [<c0008c78>] (mount_block_root+0x0/0x220) from [<c0009050>] (mount_root+0xbc/0xe4)
[    1.528616] [<c0008f94>] (mount_root+0x0/0xe4) from [<c00091e0>] (prepare_namespace+0x168/0x1bc)
[    1.537444]  r5:c00201a4 r4:c03572c0
[    1.541093] [<c0009078>] (prepare_namespace+0x0/0x1bc) from [<c0008a5c>] (kernel_init+0xf0/0x11c)
[    1.549970]  r6:c0038080 r5:c001f788 r4:c001f788
[    1.554693] [<c000896c>] (kernel_init+0x0/0x11c) from [<c0038080>] (do_exit+0x0/0x6fc)
[    1.562651]  r5:c000896c r4:00000000


U-Boot 2010.06-dirty (Feb 06 2015 - 19:53:21)

Check spi flash controller v350... Found
Spi(cs1) ID: 0xEF 0x40 0x17 0x00 0x00 0x00
Spi(cs1): Block:64KB Chip:8MB Name:"W25Q64FV"
In:    serial
Out:   serial
Err:   serial
Hit any key to stop autoboot:  0 
8192 KiB hi_sfc at 0:0 is now current device

## Booting kernel from Legacy Image at 82000000 ...
   Image Name:   OpenIPC.org | Linux-3.0.8
   Image Type:   ARM Linux Kernel Image (uncompressed)
   Data Size:    1315576 Bytes = 1.3 MiB
   Load Address: 80008000
   Entry Point:  80008000
   Loading Kernel Image ... OK
OK

Starting kernel ...

Uncompressing Linux... done, booting the kernel.
[    0.000000] Linux version 3.0.8 (runner@fv-az32-571) (gcc version 4.8.3 (OpenWrt/Linaro GCC 4.8-2014.04 latest-174-gf2830dcd3b) ) #1 Sun May 23 19:52:08 UTC 2021
[    0.000000] CPU: ARM926EJ-S [41069265] revision 5 (ARMv5TEJ), cr=00053177
[    0.000000] CPU: VIVT data cache, VIVT instruction cache
[    0.000000] Machine: hi3518
[    0.000000] Memory policy: ECC disabled, Data cache writeback
[    0.000000] AXI bus clock 200000000.
[    0.000000] Built 1 zonelists in Zone order, mobility grouping on.  Total pages: 10160
[    0.000000] Kernel command line: mem=40M console=ttyAMA0,115200 root=/dev/mtdblock2 mtdparts=hi_sfc:256K(boot),1792K(kernel),5120K(rootfs),448K(ui),576K(conf)
[    0.000000] PID hash table entries: 256 (order: -2, 1024 bytes)
[    0.000000] Dentry cache hash table entries: 8192 (order: 3, 32768 bytes)
[    0.000000] Inode-cache hash table entries: 4096 (order: 2, 16384 bytes)
[    0.000000] Memory: 40MB = 40MB total
[    0.000000] Memory: 37060k/37060k available, 3900k reserved, 0K highmem
[    0.000000] Virtual kernel memory layout:
[    0.000000]     vector  : 0xffff0000 - 0xffff1000   (   4 kB)
[    0.000000]     fixmap  : 0xfff00000 - 0xfffe0000   ( 896 kB)
[    0.000000]     DMA     : 0xffc00000 - 0xffe00000   (   2 MB)
[    0.000000]     vmalloc : 0xc3000000 - 0xfe000000   ( 944 MB)
[    0.000000]     lowmem  : 0xc0000000 - 0xc2800000   (  40 MB)
[    0.000000]     modules : 0xbf000000 - 0xc0000000   (  16 MB)
[    0.000000]       .init : 0xc0008000 - 0xc0024000   ( 112 kB)
[    0.000000]       .text : 0xc0024000 - 0xc0340000   (3184 kB)
[    0.000000]       .data : 0xc0340000 - 0xc0357220   (  93 kB)
[    0.000000]        .bss : 0xc0357244 - 0xc03680f8   (  68 kB)
[    0.000000] SLUB: Genslabs=13, HWalign=32, Order=0-3, MinObjects=0, CPUs=1, Nodes=1
[    0.000000] NR_IRQS:128 nr_irqs:128 128
[    0.000000] sched_clock: 32 bits at 100MHz, resolution 10ns, wraps every 42949ms
[    0.000070] Calibrating delay loop... 218.72 BogoMIPS (lpj=1093632)
[    0.070079] pid_max: default: 32768 minimum: 301
[    0.070510] Mount-cache hash table entries: 512
[    0.071725] CPU: Testing write buffer coherency: ok
[    0.076419] NET: Registered protocol family 16
[    0.091352] Serial: AMBA PL011 UART driver
[    0.091691] uart:0: ttyAMA0 at MMIO 0x20080000 (irq = 5) is a PL011 rev2
[    0.297429] console [ttyAMA0] enabled
[    0.302132] uart:1: ttyAMA1 at MMIO 0x20090000 (irq = 5) is a PL011 rev2
[    0.353104] bio: create slab <bio-0> at 0
[    0.374615] SCSI subsystem initialized
[    0.382028] usbcore: registered new interface driver usbfs
[    0.388278] usbcore: registered new interface driver hub
[    0.394685] usbcore: registered new device driver usb
[    0.407665] cfg80211: Calling CRDA to update world regulatory domain
[    0.414826] Switching to clocksource timer1
[    0.428235] NET: Registered protocol family 2
[    0.432977] IP route cache hash table entries: 1024 (order: 0, 4096 bytes)
[    0.440606] TCP established hash table entries: 2048 (order: 2, 16384 bytes)
[    0.448054] TCP bind hash table entries: 2048 (order: 1, 8192 bytes)
[    0.454667] TCP: Hash tables configured (established 2048 bind 2048)
[    0.461063] TCP reno registered
[    0.464240] UDP hash table entries: 256 (order: 0, 4096 bytes)
[    0.470226] UDP-Lite hash table entries: 256 (order: 0, 4096 bytes)
[    0.477247] NET: Registered protocol family 1
[    0.482557] RPC: Registered named UNIX socket transport module.
[    0.488502] RPC: Registered udp transport module.
[    0.493300] RPC: Registered tcp transport module.
[    0.498017] RPC: Registered tcp NFSv4.1 backchannel transport module.
[    0.552849] squashfs: version 4.0 (2009/01/31) Phillip Lougher
[    0.562147] JFFS2 version 2.2. (NAND) (SUMMARY)  © 2001-2006 Red Hat, Inc.
[    0.573636] msgmni has been set to 72
[    0.578434] io scheduler noop registered
[    0.582469] io scheduler deadline registered (default)
[    0.587938] io scheduler cfq registered
[    0.625549] brd: module loaded
[    0.633472] Spi id table Version 1.22
[    0.638774] Spi(cs1) ID: 0xEF 0x40 0x17 0x00 0x00 0x00
[    0.655687] SPI FLASH start_up_mode is 3 Bytes
[    0.660211] Spi(cs1): 
[    0.662411] Block:64KB 
[    0.664860] Chip:8MB 
[    0.667132] Name:"W25Q64FV"
[    0.670147] spi size: 8MB
[    0.672769] chip num: 1
[    0.675263] 5 cmdlinepart partitions found on MTD device hi_sfc
[    0.681228] Creating 5 MTD partitions on "hi_sfc":
[    0.686047] 0x000000000000-0x000000040000 : "boot"
[    0.695074] 0x000000040000-0x000000200000 : "kernel"
[    0.704254] 0x000000200000-0x000000700000 : "rootfs"
[    0.713587] 0x000000700000-0x000000770000 : "ui"
[    0.722569] 0x000000770000-0x000000800000 : "conf"
[    0.751434] Fixed MDIO Bus: probed
[    1.171691] himii: probed
[    1.299893] ehci_hcd: USB 2.0 'Enhanced' Host Controller (EHCI) Driver
[    1.306925] hiusb-ehci hiusb-ehci.0: HIUSB EHCI
[    1.312776] hiusb-ehci hiusb-ehci.0: new USB bus registered, assigned bus number 1
[    1.320815] hiusb-ehci hiusb-ehci.0: irq 15, io mem 0x100b0000
[    1.340129] hiusb-ehci hiusb-ehci.0: USB 0.0 started, EHCI 1.00
[    1.348444] hub 1-0:1.0: USB hub found
[    1.352361] hub 1-0:1.0: 1 port detected
[    1.359383] platform rtc-hi3518: rtc core: registered rtc-hi3518 as rtc0
[    1.372761] TCP cubic registered
[    1.376019] NET: Registered protocol family 17
[    1.380894] 802.1Q VLAN Support v1.8
[    1.387003] registered taskstats version 1
[    1.391474] platform rtc-hi3518: setting system clock to 2015-11-22 14:03:07 UTC (1448200987)
�[    1.405605] VFS: Mounted root (squashfs filesystem) readonly on device 31:2.
[    1.412941] Freeing init memory: 112K
[    2.014421] usb 1-1: new high speed USB device number 2 using hiusb-ehci
[    2.100346] init: Console is alive
[    3.772234] Initializing USB Mass Storage driver...
[    3.778131] usbcore: registered new interface driver usb-storage
[    3.784240] USB Mass Storage support registered.
[    4.190725] init: - preinit -
get_chip_id35180100() got unexpected 0xffffffff for 3518?v100
Check kernel modules loaded
Press the [f] key and hit [enter] to enter failsafe mode
Press the [1], [2], [3] or [4] key and hit [enter] to select the debug level
Failed to connect to ubus
Please press Enter to activate this console.



BusyBox v1.23.2 (2021-05-23 19:39:13 UTC) built-in shell (ash)


 ___                  _  ___  ___
/   \ ___  ___  _  _ | ||   \/  _|
| | ||   \/ _ \| \| || || | || |
| | || | |  __/| \\ || ||  _/| |_
\___/|  _/\___||_|\_||_||_|  \___|.ORG    v21.04.10.2
     |_|


OpenIPC is asking for your help to support development cost and long-term maintenance
of what we believe will serve a fundamental role in the advancement of a stable, flexible
and most importantly, Open IP Network Camera Framework for users worldwide.

Your contribution will help us advance development proposals forward, and interact with 
the community on a regular basis.

  https://openipc.org/contribution/
```

## TODO

虽然系统起来了，但是目前 Sensor 没有被正确识别，WiFi Module 没有正常驱动，u-boot 也是不支持 mmc 的老版本，更新固件困难。所以接下来要干的事情就是一一解决这些问题：

1. 移植 OpenIPC 的 u-boot
2. 驱动 WiFi Module
3. 识别 Sensor

## 参考资料

1. https://www.mydigit.cn/forum.php?mod=viewthread&tid=255164
2. https://github.com/felix-001/hackboyun/blob/develop/doc/Boyun_FlashFirmware.md
3. https://github.com/OpenIPC/chaos_calmer