---
title: 《iOS逆向工程》- 砸壳
date: 2017-07-24 14:15:53
tags: [reverse,iOS]
---

砸壳，与Android、Windows平台上做逆向分析的时候进行的“脱壳”十分相似，不过也有不同，Android上/Windows上的“加壳”操作，是由App开发者进行的，而iOS的加壳操作则是由苹果爸爸进行的。而且，这个壳的主要目的不是防止被逆向分析，而是一种**DRM(数字版权管理)**手段，它与iTunes Store中的其他资源一样，使用``FairPlay``([Wikipedia](https://en.wikipedia.org/wiki/FairPlay))进行加密，只能在特定账户的特定设备上运行。

砸壳需要在越狱设备上进行，需要一个叫``dumpdecrypted``的工具，具体步骤如下：

## Clone && 编译
dumpedcrypted的代码托管在Github上，我们先Clone再编译

```bash
# clone
git clone https://github.com/stefanesser/dumpdecrypted.git

# compile 
cd dumpdecrypted
make
```

## 签名
经过上边的编译之后，会在工程目录下，生成一个**dumpdecrypted.dylib**动态链接库文件，之后我们需要把它上传到越狱过的设备上使用，但在此之前，我们首先需要为它进行签名，因为在iOS设备上，没有或签名损坏的可执行文件无法执行。

```bash
## 列出可签名证书
security find-identity -v -p codesigning

## 为dumpecrypted.dylib签名
codesign --force --verify --verbose --sign "iPhone Developer: xxx xxxx (xxxxxxxxxx)" dumpdecrypted.dylib
```

## 上传
现在，我们需要把签过名的 dumpdecrypted.dylib 上传到越狱设备上随便一个可写的目录中，为了方便，我们选择 **/Library/MobileSubstrate/DynamicLibraries/** 这个目录，这里存放的是我们编写的或者使用 Cydia 安装的各种Tweak。

```bash
# 上传
scp -P 2222 dumpdecrypted.dylib root@localhost:/Library/MobileSubstrate/DynamicLibraries/
```

## 使用
万事具备，只欠东风。我们的工具已经准备完毕，可以对应用进行砸壳啦！

```bash
# 登录到设备
ssh root@localhost -p 2222

# 查找待砸壳应用路径
ps ax | grep xxx

# 切换工作目录
cd /var/containers/Bundle/Application/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx/xxx.app/

# 砸壳！！
DYLD_INSERT_LIBRARIES=/Library/MobileSubstrate/DynamicLibraries/dumpdecrypted.dylib ./xxxxx
```
之后会在当前目录生成一个 **xxxxx.decrypted**的文件，这个就是砸壳之后的可执行文件了。

## 原理
iOS 的动态链接库 dyld 支持动态链接库插入功能，通过向宏 **DYLD_INSERT_LIBRARIES** 里写入动态库的完整路径，就可以在可执行文件加载的时候，将动态链接库插入。这就是砸壳那一步干的事情，插入dumpdecrypted.dylib。

dumpdecrypted.c里只有一个函数，如下：
![](/images/15008778067222.jpg)
注意源码中的``__attribute__((constructor))``一行，这表示在动态库被加载的时候执行它所修饰的函数。在dumpdecrypted.dylib被加载的时候，dyld 已经完成了对可执行文件当前设备架构mach-o文件的解密，在这个函数中，就是将内存中已经解密的数据dump出来，回写到xxx.decrypted文件中。

## Tips-1
对于通用二进制(Universal binary / fat binary)文件，dyld只会对当前设备架构部分进行解密，比如下边这个二进制文件
![](/images/15008777979548.jpg)
包含armv7 && arm64两种架构，那在32bit设备上（比如iPhone5）进行砸壳之后，只有armv7的部分是解密的，同理，在64bit设备上只有arm64部分是解密的。

通过iOS上的App Store下载的App，只会包含与设备架构相同的部分，如果想要在64bit设备上解密armv7部分，那么就需要这么干：

1. 通过macOS上的 iTunues 工具，从App Store下载响应的App，因为macOS上无法确认用户设备架构，此时下载的App是包含两种架构的。
2. 对下载的iPA进行解包，拿到二进制可执行文件：

```bash
## 从iTunes上下载的应用放在这里，复制出来
cp ~/Music/iTunes/iTunes\ Media/Mobile\ Applications/JD\ 130389.ipa .

## iPa实际上就是个zip压缩文件
unzip JD\ 130389.ipa

## 从解压出来的Payload/xxx.app中复制相应的可执行文件出来
cp Payload/xxx.app/xxx .

## 使用lipo工具，对可执行文件进行“瘦身”，注意不要使用 -thin 参数，需要保持输出仍是一个fat binary
lipo -remove arm64 xxx -output xxx.armv7

## 上传到越狱设备，替换响应的可执行文件
scp -P 2222 xxx.armv7 root@localhost:/var/containers/Bundle/Application/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx/xxx.app/xxxx

## 再次砸壳，此时生成的就是32bit的解密文件了
DYLD_INSERT_LIBRARIES=/Library/MobileSubstrate/DynamicLibraries/dumpdecrypted.dylib ./xxxxx
```


