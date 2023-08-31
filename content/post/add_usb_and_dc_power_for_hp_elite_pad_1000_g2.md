---
title: "翻车日记: HP ElitePad 1000 G2 加装 USB 2.0 接口"
date: 2021-01-25T19:20:58+08:00
categories: ["硬件"]
---

> 文中记录的改装方法确认可以生效，翻车的是我这个个案

前几日脑子一热，闲鱼入手一台 HP ElitePad 1000 G2 Windows 平板，单主机 199，加改装 DC 充电 260。这个平板很神奇，因为充电器接口使用的是 HP 自己的接口，所以充电器的价格几乎快和主机一个加钱了 ಥ_ಥ，所以入手了改装充电的套餐。

回来之后，感觉自带的 Windows 10 版本比较老，想升级一下系统，然后系统自带的更新不可用，还没有 USB 接口，闲鱼上有 SD 卡重装系统的教程，还特娘的要 30，感觉这平板不值钱，其他的都特娘的值钱。

所以，开始研究怎么特娘的给他加个 USB 接口（噩梦的开始）。

## 改装 USB 2.0 端口

拆开主机，取下屏幕，映入眼帘的是一块硕大的电池，娇小的主板，和一个过时的 3G 网卡：
![9E87CA78-B6C5-4C6D-B9FA-DFB84D2F458B_1_105_c](https://i.loli.net/2021/01/25/uLz3daRIrMo4DJk.jpg)

这里的网卡型号是[华为 MU736](http://download-c.huawei.com/download/downloadCenter?downloadId=14243)，按照文档所述，网卡接口是 M.2 Socket 2，具体来讲应该是 M.2 Socket 2 Key B，接口的主要功能包括：

> PCIe x2 / SATA /USB 2.0 / USB 3.0 / HSIC / SSIC / Audio / UIM / I2C

再依据 M.2 Socket 2 Key B 的 pinout，可以确定 USB 2.0 的 D+ 和 D- 的引脚位置。

![-w668](https://i.loli.net/2021/01/25/9HJ1NGnWwV3za8Q.jpg)

再通过测量网卡接口与主板上焊点的引脚对应关系，就可以找到 D+ 和 D- 对应的引脚焊点了，入下图：

![-w791](https://i.loli.net/2021/01/25/6iNPvuI8LkK7lfO.jpg)

确定了数据引脚，下面需要找个 +5V 和 GND 引脚。GND 好找，到处都是，主板上测了一圈没找到 +5V，所以就从电池线中接出了 +5V 和 GND。电池的电压 >7V 左右，用了个 5V 稳压模块，焊好后如下图：

![2021-01-25 18.53.55](https://i.loli.net/2021/01/25/1va8h6KEgsdqNJb.jpg)

Type-A 太大了，平板里放不下，所以接出一个 Type-C 的母口，在外头再转成 Type-A 的母口，亲测鼠标，U盘可用~

### 翻车
在装回屏幕的过程中不小心把焊好的 D+ 和 D- 扯断了，然后带电焊接了一下，就再也没有反应了ಥ_ಥ。

## 改装直流充电（未验证！）

这部分没有亲自试验，因为我买的是卖家已经改好充电的，我偷懒没有重新焊，只拆开看了下原理，整理如下，仅供参考。

### 原理图
![-w478](https://i.loli.net/2021/01/25/MKidpLI9gm7Hhfs.jpg)

RED, YELLOW, BROWN 代指下图中的红色，黄色，棕色线

![71A7431D-3E6A-4568-B484-034CB8B526A7_1_105_c](https://i.loli.net/2021/01/25/irpwjBma67OfCFu.jpg)

![8B6F0E25-5C22-46C1-BA89-F900235887B4_1_105_c](https://i.loli.net/2021/01/25/QKHx78qmu35REf2.jpg)

