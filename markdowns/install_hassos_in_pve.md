# 在  PVE 中安装 HAOS

1. 创建 Linux 2.6-5.x 虚拟机，不使用 CD/DVD

![](https://pan.xnure.com/OneDrive/Pics/blog/16246361883928.jpg ':size=600')

2. 勾上 `Qemu Agent`

![](https://pan.xnure.com/OneDrive/Pics/blog/16246362280947.jpg ':size=600')

3. 硬盘随便选一个，反正等会儿要删掉

![](https://pan.xnure.com/OneDrive/Pics/blog/16246362674731.jpg ':size=600')

4. CPU/内存看着给，1C1G 或者 2C2G 应该就够了
5. 添加一个网络设备

![](https://pan.xnure.com/OneDrive/Pics/blog/16246363309074.jpg ':size=600')

6. 完成

7. 在『Hardware』 中 rmeove 掉默认创建的硬盘
8. BIOS 改为 "OVMF(UEFI)", 并新建一个 "EFI Disk"（如果没有的话）
9. ssh 登录到 PVE 实例中，从 https://github.com/home-assistant/operating-system/releases/ 下载最新版本的 haos 镜像，主要选择 vmdk 版本的，比如 `haos_ova-6.1.vmdk.zip`。
10. 解压下载好的镜像后，`unzip`解压， 然后 `qm importdisk 10x haos_ova-6.1.vmdk local-lvm` 这样，导入磁盘，注意替换 `10x` 为创建的 haos 虚拟机 id
11. 在 『hardware』界面选择 `unused Disk`，编辑，添加，注意要改成 `SATA`
    ![](https://pan.xnure.com/OneDrive/Pics/blog/16249798173781.jpg ':size=600')
12. 在 『options-Boot Order』 处，仅把 `sata0` 选中，去掉其他的设备。
13. 开机