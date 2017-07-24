---
title: 《iOS逆向工程-介绍》
date: 2017-07-24 14:12:53
tags: [reverse,iOS]
---

## 什么是逆向
在我们通常的程序开发过程中，要经历从编码，编译，链接最后到生成二进制的可执行程序这样一个过程。在这一过程中，源码文件中的注释、变量名、函数名甚至部分逻辑都会被编译器修改或移除，最终生成的二进制文件是一个面向机器的指令&&资源合集。逆向工程则是从最后的二进制文件入手，通过反汇编、静态分析、动态调试等手段，达到了解程序执行逻辑，修改或者重新实现这一逻辑的目的。

## 为什么要逆向
通常情况下，软加开发商交付给我们的都是已经编译好的可执行文件，此时软件对于我们来说就是一个黑匣子，我们可以控制和了解的，只有软件开发商暴露给我们的有限的接口和功能，至于程序中某个部分的具体逻辑，我们无从知晓。如果我们需要了解程序的更多细节，修改/绕过程序中的某些逻辑，就需要通过逆向工程，从二进制文件入手，尝试从汇编代码中理清原始逻辑，并修改/绕过以达到目的。甚至于，在通过逆向工程了解了原有程序的相关逻辑之后，可以对原程序重新实现。

事实上，许多的知名程序都来源于逆向工程，比如：

* Samba：一个允许非Windows系统与Windows系统共享文件的开源项目。由于微软没有公开Windows文件共享机制的信息，Samba必须作逆向工程，以便在非Windows系统上，仿真出同样的行为。
* Wine：对Windows API做了同样的工作，
* OpenOffice.org：对Microsoft Office文件格式作逆向工程。
* ReactOS：竭力在ABI及API上，兼容NT系Windows系统，以便让为Windows所编写的软件和驱动程序可以在其上运行。


## 怎么逆向
逆向分析通常需要结合静态代码分析与动态调试技术。静态代码分析是通过阅读反汇编之后的汇编代码，结合静态分析工具生成的伪代码来理解代码逻辑或找出代码漏洞。动态调试则是通过调试工具挂载（attach）到正在运行的目标进程上，通过对进程下断点观察进程运行时的数据流向，执行过程等信息了解代码逻辑。

除此之外，为了保护自己的软件不被逆向/篡改，软件开发商通常会对软件进行混淆、加密、加壳等操作，在真正分析软件的逻辑之前，通常需要先对应用进行脱壳、反混淆等操作。拿到真正的包含软件逻辑的可执行文件之后，才能开始分析其逻辑。

