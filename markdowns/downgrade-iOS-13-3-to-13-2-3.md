# iPhone SE 降级 iOS 13.2.3

手头有部之前在咸鱼上 80 块购入的有 ID 的 iPhone SE，系统 iOS 13.1.2，使用 checkra1n 绕过了 iCloud Lock。今儿翻出来想玩玩儿 checkra1n，想都没想就升级到了最新的 iOS 13.3，升级结束才想起来，自 iOS 13.0 beta4 开始，Apple 修复了通过重命名 `Setup.app` 的方式绕过 iCloud Lock 的漏洞，一试果然，重命名 `Setup.app` 后，Home 键不响应，重启之后，文件系统自动恢复到修改之前。一番搜索无果，想起自己保存了自 iOS 12.4 开始的所有 APTicket，遂决定恢复到 iOS 13.2.3，中间碰到一点儿小问题，特此记录一下。

<!--more-->

## Set Nonce

### What' Nonce

> 在信息安全中，Nonce是一个在加密通信只能使用一次的数字。在认证协议中，它往往是一个随机或伪随机数，以避免重放攻击。

iOS/iTunes 在更新设备固件的过程中，会将设备的 ECID，系统版本等信息，以及一个一次使用的 `Nonce` 发送给 Apple 的验证服务器，服务器在校验通过后，会返回校验结果给 iOS/iTunes，结果使用非对称算法加密，在没有私钥的情况下无法解密，也无法伪造。

但是，我们可以将校验结果保存下来，之后 Apple 不再提供此版本校验的时候（假设不考虑 SEP 兼容性），在越狱后通过 `nvram` 固定 `nonce` 为此校验结果使用的，来重放校验过程，实现 iOS 系统降级/更新到不提供验证的版本。

### Find tool

`checkra1n` 利用 A5-A11 系列 CPU 的 BootROM 级漏洞，实现无视 iOS 系统版本的越狱操作。所以在升级到最新的 iOS 13.3 系统之后，尽管被卡在了 AppleID 验证页面上，但是可以通过 `checkra1n` 越狱，获得一个 SSH 连接:

![-w324](https://pan.xnure.com/OneDrive/Pics/blog/15781353990076.jpg)

远程登录设备之后，就要想办法设置 `nonce` 了。
一番搜索，大部分的 nonce setter 都是 UI 界面的，或者集成在越狱工具中，没有单独可以使用的命令行文件。不过偶然找到了一个 `GeneratorAutoSetter` 的工具，顺藤摸瓜找到了一个命令行版本的 nonce setter: `dimentio`。不过 clone 下来编译之后并不能在 iOS 上跑，因为缺少必要的权限，可以通过 `ldid` 工具添加，或者直接使用 [issue](https://github.com/0x7ff/dimentio/issues/2) 中其他人提供的编译好的版本。

### Set Nonce

接下来上传工具，设置 Nonce，futurerestore 就可以，不过默认情况下 iOS 文件系统是只读挂载，需要重新挂载一下：

```bash
mount -o rw,union,update /
```

之后，`scp -P 2222 dimentio root@127.0.0.1:/usr/bin/`，注意，这里一定要上传到 `/usr/bin/` 或者 `/usr/local/bin` 这样默认有执行权限的目录下。
最后执行 `dimentio 你的 Nonce` 完成设置

![-w507](https://pan.xnure.com/OneDrive/Pics/blog/15781361303550.jpg)

## 恢复

参考 [使用 futurerestore 从 iOS 11.1.2 升级至 11.3.1](https://www.tylinux.com/post/upgrade-from-iOS-11-1-2-to-iOS-11-3-1-with-blob/)

不过我在恢复的过程中碰到点儿问题。。。`futurerestore` 的 `180` 版本，使用 iOS 13.3 的 baseband 和 SEP 文件，在最后恢复基带的时候报错，信息如下：

```text
Received Baseband SHSH blobs
common.c:printing 20753 bytes plist:

...(plist file content)

ERROR: zip_name_locate: Firmware/Mav10-9.30.02.Release.bbfw
ERROR: Unable to extract baseband firmware from ipsw
ERROR: Unable to send baseband data
ERROR: Unable to successfully restore device
No data to read (timeout)
FDR 0x7fdfd5424910 terminating...
Cleaning up...
[exception]:
what=ERROR: Unable to restore device

code=67829777
line=1035
file=futurerestore.cpp
commit count=29:
commit sha  =2994651a10d8176a298b31e7706b4b6af97975d1:
Done: restoring failed!
```

意思是 `Firmware/Mav10-9.30.02.Release.bbfw` 这个文件在 ipsw 文件中不存在。搜索了一下 issue，找到了同样错误的 [issue#296](https://github.com/tihmstar/futurerestore/issues/296)，开发者表示已经尝试修复了此问题，修复的版本就是我在用的这个。。。

琢磨了一下，在 iOS 13.2.3 的 IPSW 文件中肯定是没有 iOS 13.3 的基带文件啊，报错可以理解。那我把 iOS 13.3 的基带文件放到 iOS 13.2.3 的 IPSW 文件中，它不就找到了吗？尝试了一下，果然可以，成功日志如下：

```text
Reading data from /var/tmp/ffffffffffffffffffffffffffffffff00000019N4y7pO
Sending BasebandData now...
Done sending BasebandData
FDR 0x7fc229f6e2b0 timeout waiting for command
FDR 0x7fc229f6e2b0 waiting for message...
No data to read (timeout)
Updating Baseband completed.
Updating SE Firmware (59)
Updating Veridian (66)
Fixing up /var (17)
Creating system key bag (50)
No data to read (timeout)
FDR 0x7fc229f6e2b0 timeout waiting for command
FDR 0x7fc229f6e2b0 waiting for message...
No data to read (timeout)
No data to read (timeout)
FDR 0x7fc229f6e2b0 timeout waiting for command
FDR 0x7fc229f6e2b0 waiting for message...
No data to read (timeout)
No data to read (timeout)
FDR 0x7fc229f6e2b0 timeout waiting for command
FDR 0x7fc229f6e2b0 waiting for message...
No data to read (timeout)
FDR 0x7fc229f6e2b0 got sync message
Connecting to FDR client at port 49203
FDR Received 131 bytes
Got device identifier 6633487374b0dc5119cff
FDR connected in reply to sync message, starting command thread
FDR 0x7fc229f6e2b0 waiting for message...
FDR 0x7fc229ca44c0 waiting for message...
FDR 0x7fc229ca44c0 got plist message
FDR Received 59 bytes
FDR sending 52 bytes:
common.c:printing 214 bytes plist:

...

FDR Sent 52 bytes
FDR 0x7fc229ca44c0 terminating...
Modifying persistent boot-args (25)
Unmounting filesystems (29)
Unmounting filesystems (29)
Unmounting filesystems (29)
Unmounting filesystems (29)
Got status message
Status: Restore Finished
FDR 0x7fc229f6e2b0 terminating...
Cleaning up...
Done: restoring succeeded!
```

## 参考

[SHSH_Protocol](https://www.theiphonewiki.com/wiki/SHSH_Protocol)
[futurerestore](https://github.com/tihmstar/futurerestore)
