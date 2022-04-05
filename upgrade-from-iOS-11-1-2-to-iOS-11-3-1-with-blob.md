# 使用 futurerestore 从 iOS 11.1.2 升级至 11.3.1

<!--more-->

## 物料
1. 使用 iOS 11.1.2 系统的 iPad Air2
2. 保存的 iOS 11.3.1 的 SHSH2 文件
3. iOS 11.3.1 的 IPSW 文件 [下载](https://ipsw.me/)
4. iOS 11.4.1 的 IPSW 文件 [下载](https://ipsw.me/)
5. futurerestore [下载](https://github.com/encounter/futurerestore/releases/)
6. NonceSet112 [下载](https://github.com/julioverne/NonceSet112)

## 设置 Nonce
1. 使用文本编辑器打开准备好的 11.3.1 的 SHSH2 文件，搜索 `generator`，找到该 SHSH2 文件的 generator,类似这样：
```xml
<key>generator</key>
<string>0x8e3821950b87d6b8</string>
```

2. 打开 iPad 上的 NonceSet112 App，在其获取 Root 权限之后，将 `boot generator` 设置为刚刚找到的值，并点击保存
![](https://i.loli.net/2018/12/24/5c20fa9b75be1.jpg)

## futurerestore
1. 解压 iOS 11.4.1 的 IPSW 文件，复制 `BuildManifest.plist` 和 `Firmware/all_flash/sep-firmware.j81.RELEASE.im4p` 文件 到 11.3.1 IPSW 文件同一目录下备用。
2. 解压下载好的 `futurerestore` 到 11.3.1 IPSW 文件同一目录
3. 执行如下命令恢复 11.3.1 系统镜像
    
    ```bash
    ./futurerestore -t iPad_Air2_11.3.1.shsh2 -s sep-firmware.j81.RELEASE.im4p --no-baseband -p BuildManifest.plist -m BuildManifest.plist iPad_64bit_TouchID_11.3.1_15E302_Restore.ipsw
    ```
    注意其中的 `--no-baseband` 选项，因为我的 iPad Air2 是 Wifi 版本，所以指定了这一选项。如果是插卡版本或者是 iPhone，请使用 `-b xxx.bbfw` 指定 `Firmware` 目录下的相应文件。

4. 等待程序执行完成即可
