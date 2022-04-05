# 使用 Linux deploy 在 Android 设备上运行 Linux 发行版

在学习 ARM 汇编的时候，需要在本地搭建 arm 环境，当时所用的方法是使用 QEMU 模拟树莓派。然而由于 QEMU 对树莓派支持有限，性能堪忧。昨天翻出 2013 时候淘的一部 LG GPro，突然想到可以在 Android 设备上跑个 Linux 发行版来解决这个问题。

<!--more-->

（手机长这样：
![-w540](https://i.loli.net/2018/01/22/5a65a5eecc4f8.jpg)
（感人的大黑边😭

## 设备要求
* Rooted

## 安装
从 Google Play 下载安装 `Linux deploy` App，打开，长这样：
![-w540](https://i.loli.net/2018/01/22/5a65a5ef56687.jpg)

点击左上角图标进入菜单，`Profiles` 里是我们创建的 Linux 实例，可以从这里切换已安装的不同发行版。`Repository` 则是 Linux Deploy 的源，默认是作者提供的 [http://hub.meefik.ru](http://hub.meefik.ru)（看来作者应该是战斗民族的）。

![-w540](https://i.loli.net/2018/01/22/5a65a5ed94b47.jpg)

下图是默认源所包含的镜像列表：可以看到，只有 `debain` 的两个镜像是免费的，其他的要跳转到 Goole Play 进行付费才能导入。先以 `Debian Arm` 这个镜像为例，演示下使用方法。
![-w540](https://i.loli.net/2018/01/22/5a65a5eec96d3.jpg)

在镜像列表对应条目上点击，选择 `Import`之后，会回到下图这样的界面，但此时，所用的 Profile 已经改变了（注意标题）
![-w540](https://i.loli.net/2018/01/22/5a65a5ef56687.jpg)

点击右下角的菜单图标，进入镜像设置，如下图。在可以选择镜像的容器化方式（默认 chroot，可选 proot）、架构（默认 ARMv7，选择 ARM64 将直接使用对应的官方源进行安装，不使用作者的镜像）、镜像地址、安装路径、生成的本地镜像文件大小及格式（默认 ext2, 推荐 ext4）以及是否启用 SSH、VNC等服务。

![-w540](https://i.loli.net/2018/01/22/5a65a5eddec06.jpg)

配置完成之后，返回主界面，点击右上角选项图标，选择安装，就开始生成本地镜像，下载远程镜像及安装附加软件包，安装完成之后，点击左下角启动既可即刻启动 Linux 发行版。

## 破解 && 加速
在国内这个网络大环境下，先不说 Google Play 上不去，在我这里连接作者的源也是个问题，100多M的文件要下载好久。所以要想快速安装 && 安装其他需要付费的镜像，就需要做一些 Hack 的事情。

首先，对软件的网络请求进行抓包，发现在更新源缓存的时候，会请求这个地址：[http://hub.meefik.ru/index.gz](http://hub.meefik.ru/index.gz)，下载后解压，发现文件内容如下：

```
PROFILE=archlinux_arm
DESC=Arch Linux ARM base system.
SIZE=131
PROTECTED=true

PROFILE=archlinux_x86
DESC=Arch Linux x86 base system.
SIZE=108
PROTECTED=true

PROFILE=centos_arm
DESC=Cent OS 7 ARM base system.
SIZE=225
PROTECTED=true

PROFILE=centos_x64
DESC=Cent OS 7 x86_64 base system.
SIZE=249
PROTECTED=true

PROFILE=centos_x86
DESC=Cent OS 7 x86 base system.
SIZE=250
PROTECTED=true

PROFILE=debian_arm
DESC=Debian 9 (stretch) ARM base system (free).
SIZE=132

PROFILE=debian_x86
DESC=Debian 9 (stretch) x86 base system (free).
SIZE=145

PROFILE=fedora_arm
DESC=Fedora 25 ARM base system.
SIZE=163
PROTECTED=true

PROFILE=fedora_x86
DESC=Fedora 25 x84 base system.
SIZE=217
PROTECTED=true

PROFILE=gentoo_arm
DESC=Gentoo ARM base system.
SIZE=356
PROTECTED=true

PROFILE=gentoo_x86
DESC=Gentoo x86 base system.
SIZE=389
PROTECTED=true

PROFILE=kalilinux_arm
DESC=Kali Linux ARM base system.
SIZE=149
PROTECTED=true

PROFILE=kalilinux_x86
DESC=Kali Linux x86 base system.
SIZE=163
PROTECTED=true

PROFILE=kalitop10_arm
DESC=Kali Linux ARM Top 10 security tools (tools.kali.org) with LXDE, VNC and SSH.
SIZE=1048
PROTECTED=true

PROFILE=kalitop10_x86
DESC=Kali Linux x86 Top 10 security tools (tools.kali.org) with LXDE, VNC and SSH.
SIZE=1128
PROTECTED=true

PROFILE=opensuse_arm
DESC=openSUSE 13.2 ARM base system.
SIZE=134
PROTECTED=true

PROFILE=opensuse_x86
DESC=openSUSE 13.2 x86 base system.
SIZE=137
PROTECTED=true

PROFILE=slackware_arm
DESC=Slackware 14.2 ARM base system.
SIZE=98
PROTECTED=true

PROFILE=slackware_x86
DESC=Slackware 14.2 x86 base system.
SIZE=104
PROTECTED=true

PROFILE=ubuntu_arm
DESC=Ubuntu 16.04 LTS (Xenial Xerus) ARM base system.
SIZE=91
PROTECTED=true

PROFILE=ubuntu-lxde_arm
DESC=Ubuntu 16.04 LTS (Xenial Xerus) ARM includes LXDE, VNC and SSH.
SIZE=241
PROTECTED=true

PROFILE=ubuntu-lxde_x86
DESC=Ubuntu 16.04 LTS (Xenial Xerus) x86 includes LXDE, VNC and SSH.
SIZE=274
PROTECTED=true

PROFILE=ubuntu_x86
DESC=Ubuntu 16.04 LTS (Xenial Xerus) x86 base system.
SIZE=98
PROTECTED=true
```
哇！发现了什么！要付费的镜像配置中包含一项 `PROTECTED=true`，那如果把这个干掉，是不是就可以直接添加了？
修改 index 文件内容，删除所有的 `PROTECTED=true`，`gzip index` 重新生成 `index.gz`, 使用 `python3 -m SimpleHTTPServer 8080` 直接在当前目录下启动一个 HTTP 服务，在设备上修改源地址为 PC 的 IP + 8080 端口，比如 `http://192.168.1.100:8080`，刷新源缓存，点击一个之前付费的条目，果然没有了付费的选项，直接就可以 `Import`。

但是，在点击导入的时候，会弹 Toast 报错，查看 Python Server，发现软件还请求了一个 `GET /config/archlinux_arm.conf` 这样的接口，访问[hub.meefik.ru/config/archlinux_arm.conf](hub.meefik.ru/config/archlinux_arm.conf)，返回如下：

```
DESC="Arch Linux ARM base system."
TARGET_PATH="${EXTERNAL_STORAGE}/archlinux_arm.img"
TARGET_TYPE="file"
DISK_SIZE="2000"
FS_TYPE="ext2"
SOURCE_PATH="http://hub.meefik.ru/rootfs/archlinux_arm.tgz"
DISTRIB="archlinux"
ARCH="armv7h"
USER_NAME="android"
PRIVILEGED_USERS="root dbus"
LOCALE="en_US.UTF-8"
INCLUDE="bootstrap"
```

看得出来，基本就是镜像配置那部分的内容了，包含了默认的磁盘镜像大小、格式、安装位置等信息，以及下载URL！看到这里
![](https://i.loli.net/2018/01/22/5a65a5ee2a991.jpg)

是不是直接替换 URL 后边的镜像名字，就得到了各个镜像的安装包？试了一下下，别说，还真是。那么，镜像的全部下载地址就是：

```
http://hub.meefik.ru/rootfs/archlinux_arm.tgz
http://hub.meefik.ru/rootfs/archlinux_x86.tgz
http://hub.meefik.ru/rootfs/centos_arm.tgz
http://hub.meefik.ru/rootfs/centos_x64.tgz
http://hub.meefik.ru/rootfs/centos_x86.tgz
http://hub.meefik.ru/rootfs/debian_arm.tgz
http://hub.meefik.ru/rootfs/debian_x86.tgz
http://hub.meefik.ru/rootfs/fedora_arm.tgz
http://hub.meefik.ru/rootfs/fedora_x86.tgz
http://hub.meefik.ru/rootfs/gentoo_arm.tgz
http://hub.meefik.ru/rootfs/gentoo_x86.tgz
http://hub.meefik.ru/rootfs/kalilinux_arm.tgz
http://hub.meefik.ru/rootfs/kalilinux_x86.tgz
http://hub.meefik.ru/rootfs/kalitop10_arm.tgz
http://hub.meefik.ru/rootfs/kalitop10_x86.tgz
http://hub.meefik.ru/rootfs/opensuse_arm.tgz
http://hub.meefik.ru/rootfs/opensuse_x86.tgz
http://hub.meefik.ru/rootfs/slackware_arm.tgz
http://hub.meefik.ru/rootfs/slackware_x86.tgz
http://hub.meefik.ru/rootfs/ubuntu_arm.tgz
http://hub.meefik.ru/rootfs/ubuntu-lxde_arm.tgz
http://hub.meefik.ru/rootfs/ubuntu-lxde_x86.tgz
http://hub.meefik.ru/rootfs/ubuntu_x86.tgz
```

接着就好办了，翻墙 + aria2 多线程加速下载到本地，在 `index.gz` 所在目录下新建 `config` 目录，访问对应镜像的 config URL，保存到 config 目录下，修改 `SOURCE_PATH` 到本地 Server 的路径，Done～


