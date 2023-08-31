---
title: "macOS 下开发 51 单片机应用"
date: 2019-09-27T00:41:14+08:00
tags: [51,单片机,硬件]
categories: ["硬件"]
---

最近 DIY 之心又又又又复活了，翻出来吃灰多年的 51 开发板，重新学习一下 51。现在主力系统已经换成了 macOS，在折腾环境搭建的过程中，踩了一丢丢坑，特此记录一下。

<!--more-->

## 环境搭建

在 macOS 下没有 Keil C51 （有也不想用ಥ_ಥ），之前都是用的 `sdcc` 编译，`stcflash` 烧录。这会想起来之前在 VSCode 尝试过的 `PlatformIO IDE` 插件，搜了一下，果然支持，开搞。

### 安装 PlatformIO IDE
很简单，在 VSCode 的应用市场里，搜索 `PlatformIO IDE` 安装即可。

### 安装 MCS-51 (8051) 支持

默认情况下，`PlatformIO IDE` 没有安装 8051 的支持库，导致我们创建工程的时候，无法选择 8051 平台，所以先安装一下：

![-w1286](https://i.loli.net/2019/09/27/ehD7QgiLZzpojXG.jpg)

我使用的 宏晶 `STC89C52RC` 正在支持板子列表中~

![-w1237](https://i.loli.net/2019/09/27/wvjBZoPAIhg2lTV.jpg)

## Hello, LED

新建工程：
![-w601](https://i.loli.net/2019/09/27/KJT1mXB84rfCkbH.jpg)

新建文件 `led.c`，写入如下内容：

```c
#include <8052.h>

int main(int argc, char *argv[]) {
    P1_0 = 0xff;
    while(1) {
        P1_0 = 0x0;
    }
}
```

`PlatformIO IDE` 使用的编译工具是 `sdcc`，所以头文件及 GPIO 口的表示方式与 keil 稍有不同，见下表：

| | SSDC | keil |
| --- | --- | --- |
| 头文件 | 8051.h/8052.h | reg51.h/reg52.h |
| IO口 | P1_0 | P1^0 |
| IO口定义 | #define LED P1_0 | sbit LED = P1^0 |
| 中断函数 | void INT0_ISR() __interrupt 0 | void INT0_ISR() interrupt 0 |

![-w675](https://i.loli.net/2019/09/27/DTlzRcEMbtd4gaO.jpg)

编译烧录之后，顺利点亮 LED ~
![-w858](https://i.loli.net/2019/09/27/FIreEH1QvKRbUm7.jpg)

## 附录
1. [STC89C52RC datasheet](http://www.stcmcudata.com/datasheet/STC89C52.pdf)