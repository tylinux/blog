---
title: (译) 在 iOS 11.3 之后的系统中 remount RootFS 为可读写
date: 2018-06-12 02:30:48
tags: [iOS,Jailbreak]
---

> 原文链接：https://media.weibo.cn/article?id=2309404245794218721506
> 作者：Xiaolong Bai and Min (Spark) Zheng @ Alibaba Security Lab
> 译者：tylinux
> 博客地址: [https://www.tylinux.com](https://www.tylinux.com)

## 0x0 简介
对于越狱来讲，一个可读写的 Root 分区是必须的，因为越狱之后需要安装一些非沙盒的应用以及修改部分系统设置。但是，未越狱的 iOS 系统中， Root 文件系统默认是只读的，因此，现代越狱中的很重要的一步就是将 Root 文件系统重新挂载为可读写的。显然，苹果不会让你这么轻易地做到。

在本文中，我们将介绍苹果在 iOS 11.3 之后，针对 remount Root 文件系统为可读写问题新引入的缓解措施，同时，我们会介绍一种全新的，可以绕过这种缓解措施的技术。根据我们的研究，这种绕过技术可以与 Ian Beer 即将释出的 iOS 11.3.1 tfp0 漏洞协同工作，这就意味着，11.3.1 可以越狱了！

## 0x01 在 iOS 11.3 之前 remount Root 文件系统
当我们使用 `mount()` 系统调用重新挂载一个文件系统的时候，内核会调用 `__mac_mount()`，最终调用 `mount_common()` 函数进行挂载。在 `mount_common()` 函数中，存在一个 `MACF` 安全检查： `mac_mount_check_remount()`，用来检查本次重新挂载是否被允许，而这个检查最终执行的是 Sandbox Kext 中的 `hook_mount_check_remount()`函数，检查本次重新挂载是否为 Root 文件系统（RootFS），如果是，则终止本次挂载。如下图：

![](https://i.loli.net/2018/06/12/5b1ebf3c7e148.jpg)

在 iOS 11.3 之前的系统中，通常采用绕过沙盒检测的方式来 remount Root 文件系统，该方案由 `Xurub` 提出，先移除 Root 文件系统的 `ROOTFS` `RDONLY`, `NOSUID`标识再进行挂载。`Jonathan Levin` 在 `HITB 18` 上对此有更加详细的描述。

## 0x02 iOS 文件系统基础

出现了绕过技术，苹果自然也会升级自己的防御。自 iOS 11.3 开始，如果按照之前的方式remount Root 文件系统 ，当我们尝试修改 Root 文件系统时，内核会直接崩溃，日志如下：

![](https://i.loli.net/2018/06/12/5b1ebf3c94ca2.jpg)

这说明苹果在文件系统层面引入了新的缓解措施来阻止我们 remount Root 分区。我们仔细研究了 iOS 11.3 的文件系统，找出了几种方式来绕过新的缓解措施。在本文中，我们会详细介绍其中的一种。在开始之前，我们首先介绍一下 iOS 文件系统的一些基本结构以及刚刚内核为何会崩溃。

Darwin 内核支持许多不同的文件系统，比如 APFS、HFS+、FAT等等。当一个文件系统被挂载的同时，会生成一个通用的 `mount` 结构体（如下图）用来描述此文件系统是如何被挂载的。

![](https://i.loli.net/2018/06/12/5b1ebf3c9cc06.jpg)

在这个结构体中，`mnt_flag` 包含一些诸如 `RDONLY`、`ROOTFS`、`NOSUID` 这样的标志，来描述基本的挂载状态。`mnt_ops` 中则保存这一些函数指针，这些函数是由文件系统实现的 `mount`、`unmount`、`ioctl` 等等的已一些操作。而 `mnt_data` 则记录着具体的文件系统，比如 APFS，是如何组织和存储文件系统需要操作的关键数据。在具体的文件系统实现中，mount/unmount/remount 这些操作都是通过操作私有的 "mount" 结构体来使操作生效的。

## 0x03  根本问题

从崩溃日志中可以看到，`com.apple.xbs/Sources/apfs/apfs-748.52.14` 这条路径表明崩溃来源是 APFS 文件系统，同时也说明 iOS 的 Root 文件系统是 APFS 格式的。APFS（Apple File System）是有苹果开发的新型文件系统，具备克隆、加密及快照等等先进的功能，目前已经被应用于所有的苹果设备中。

所以，APFS 中什么地方触发了内核崩溃呢？想要回答这个问题，我们首先需要知道， Root 文件系统是如何被挂载到系统中的。在 iOS 中执行命令 `mount`，我们可以得到当前系统中挂载的所有分区信息，如下：

![](https://i.loli.net/2018/06/12/5b1ebf3c98eb5.jpg)

在 Root 文件系统的挂载路径中，有个奇怪的前缀：`com.apple.os.update-CA59XXXX@`，这个又是什么？我们先来在 macOS 上多个小实验。

![](https://i.loli.net/2018/06/12/5b1ebf3c8f058.jpg)

上图中，`tmutil localsnapshot /` 是为 Root 分区创建了一个快照，名字是 `com.apple.TimeMachine.2018-05-30-154704`。而 `mount -t apfs -o -s=com.apple.TimeMachine.2018-05-30-154704 / /tmp` 这条命令则是把创建的快照挂载到 `/tmp` 目录。挂载完成之后，我们会发现，挂载路径中也有个类似的奇怪前缀：`com.apple.TimeMachine.2018-05-30-154704@`。现在我们知道了，`com.apple.os.update-CA59XXXX@` 这个前缀表明，iOS 的 Root 分区，挂载的是一个文件系统快照！

苹果对文件系统快照的解释是：快照是文件系统某一时刻的只读实例，操作系统使用快照功能来更高效地创建备份，提供回滚到某一特定时间点的能力。显然，iOS 11.3 中新的缓解措施就是，把一个只读的文件系统快照挂载为 Root 分区。这也就解释了为什么我们改变 Root 文件系统的时候内核会崩溃了。

所以我们之所以重新挂载失败了是因为，尽管我们去掉了 `RDONLY` 的标志以使 Root 文件系统能被挂载为可读写，然而实际挂载的依然还是一个快照，而快照是只读的。而且，文件系统的私有 `mount` 结构中的 `mnt_dat` 项未被修改，依然是一个只读的快照。我们之前的方式，其实是尝试把一个只读的快照重新挂载为“可读写的”只读快照，自然是不可行的，所以就崩溃了。

为了了解这个问题的技术细节，我们首先回到之前的崩溃日志。在日志中有提到，崩溃原因是缺少某个范围的 `extent`。在 APFS 文件系统中，`extent` 是用来存储文件的位置和大小的数据结构。通过逆向 APFS 的内核扩展，确认 `extent` 以 B树 的形式存储在 APFS 私有 `mount` 结构体的 `mnt_data`项中。而在 APFS 快照的 `mnt_data` 中，不包含有效的 `extent` 结构，当我们尝试使用原有方式重新挂载 Root 分区并对它进行修改的时候，文件系统会去查找相应的 `extent` 结构，因为 Root 分区是快照，无法找到正确的 `extent` 结构，也就触发了内核崩溃。

![](https://i.loli.net/2018/06/12/5b1ebf3cb592f.jpg)


## 0x04 新的绕过方案

通过以上的分析，一个很明确的解决方案出现了：我们需要让文件系统成功地从快照的 `mnt_data` 中获取 `extent` 结构。为了达到这个目的，我们需要创建一个和可读写文件系统一样的，包含有效文件 `extent` 的 `mnt_data` 结构。然而，创建一个真是有效的 `mnt_data` 结构是一项复杂而又困难的工作。那么，让 APFS 文件系统像挂载一个可读写的 Root 分区一样，帮我们创建一个 `mnt_data` 行不行呢？没问题，只要我们给 Root 文件系统创建一个新的可读写挂载，然后再从这个可读写挂载中获取 `mnt_data` 结构就可以了。

所以，新的绕过姿势的完整思路已经出来了，总共分以下几步：

1. 把 Root 分区所在的块设备 `/dev/disk0s1s1` 以可读写的方式挂载到某个目录下，比如 `/var/mobile/tmp`
2. 从新的可读写挂载中获得 `mnt_data` 结构
3. 像 11.3 之前的方式一样，修改 Root 文件系统的 `mnt_flag`，然后 remount
4. 用刚刚获得的 `mnt_data` 结构，覆盖 Root 分区挂载的 `mnt_data` 结构

![](https://i.loli.net/2018/06/12/5b1ebf3ca45b0.jpg)

新的问题来了：iOS 不允许同一个块设备被挂载两次。具体判断是在 `mount_common()` 方法中：

![](https://i.loli.net/2018/06/12/5b1ebf3ca7ab4.jpg)

在 `vfs_mountedon()` 方法中，函数从设备的 vnode 中获取 v_specflags，然后检查其中是否包含 `SI_MOUNTEDON` 和 `SI_ALIASED` 标志：

![](https://i.loli.net/2018/06/12/5b1ebf3cb6812.jpg)

不过，我们可以通过清空设备 vnode 的 v_specflags 属性来绕过 `vfs_moutedon()` 中的检测。

至此，我们就基本实现了绕过 iOS 11.3 中的缓解措施，实现将 Root 分区 remount 为可读写的目的了。伪代码如下：

```c
void remountRootAsRW() {
    char *devpath = strdup(“/dev/disk0s1s1”);
    uint64_t devVnode = getVnodeAtPath(devpath);
    writeKern(devVnode + off_v_specflags, 0); // clear dev vnode’s v_specflags

    /* 1. 将 Root 分区所在块设备挂载到某个目录下 */
    char *newMPPath = strdup(“/private/var/mobile/tmp”);
    createDirAtPath(newMPPath);
    mountDevAtPathAsRW(devPath, newMPPath);

    /* 2. 从新的挂载中获得 mnt_data 结构 */
    uint64_t newMPVnode = getVnodeAtPath(newMPPath);
    uint64_t newMPMount = readKern(newMPVnode + off_v_mount);
    uint64_t newMPMountData = readKern(newMPMount + off_mnt_data);

    /* 3. 修改 Root 分区的挂载方式并重新挂载 */
    uint64_t rootVnode = getVnodeAtPath(“/”);
    uint64_t rootMount = readKern(rootVnode + off_v_mount);
    uint32_t rootMountFlag = readKern(rootMount + off_mnt_flag);
    writeKern(rootMount + off_mnt_flag, rootMountFlag & ~ ( MNT_NOSUID | MNT_RDONLY | MNT_ROOTFS));
    mount(“apfs”, “/”, MNT_UPDATE, &devpath);

    /* 4. 用新的 mnt_data 结构覆盖原有的 mnt_data */
    writeKern(rootMount + off_mnt_data, newMPMountData);
}
```

在代码中， `readKern()` 方法用于从某个内存地址中读取数据，`writeKern()` 用于向某个内存地址中写入数据。相关实现可以从 `Xerub`、`Electra`、`V0rtex`、`mach_portal` 以及 `Qilin` 等工具中找到。`getVnodeAtPath()` 是我们开发的一个小工具，用来获取某个路径的 vnode 地址，使用 `Ian Beer` 提供的技术实现内核代码执行。

使用本文讲述的新的绕过方式，就可以在 iOS 设备上获得一个可读写的 Root 文件系统。你可以在此之上修改系统文件、安装非沙盒的可执行文件等等。下图展示了一个已经成功挂载为可读写状态的 Root 文件系统和 iOS 11.3.1 系统的越狱环境。

![](https://i.loli.net/2018/06/12/5b1ebf4fee036.jpg)

## 0x05 结论

关于本文提到的绕过方式有一点要注意，当你重启设备后，对文件系统所做的所有修改都会被丢弃，所以这是一种不完美的 remount 方案（我们将在近期讨论一种完美的 remount 方案）。但是相信对于大部分的越狱群众来讲这已经足够了。

最后，我们将于 2018年8月9日指12日在拉斯维加斯举办的 DEFCON 黑客大会上，就 iOS 越狱与 macOS 漏洞检测等话题发表演讲。同时，欢迎大家关注我们的 Twitter 账户：@bxl1989、@SparkZheng.

![](https://i.loli.net/2018/06/12/5b1ebf3cb3a4e.jpg)

