# 搭建私有Cydia源

在通过 ``TheOS`` 完成 Tweak 的开发后，我们通常会执行 ``make package install`` 命令来将 Tweak 安装到越狱设备上。但如果需要将 Tweak 部署到大量设备上，安装和更新都是一个问题。这个时候，我们可以通过部署私有的 Cydia 源来完成 Tweak 的安装和更新。

<!--more-->

## 依赖
为了一次性把我们自己的 Tweak 以及依赖的其他库安装上，应该在我们的 Tweak 中写明依赖的库。具体修改的是 Tweak 工程中的 control 文件。control 文件内容如下：

```
Package: 12306
Name: 12306
Depends: mobilesubstrate, com.conradkramer.open
Version: 0.0.1
Architecture: iphoneos-arm
Description: An awesome MobileSubstrate tweak!
Maintainer: windy
Author: windy
Section: Tweaks
```

在 ``Depends`` 项中添加 Tweak 的依赖，以逗号隔开。要注意：这里填写的是包名，比如 ``Open`` 这个工具，需要填写的是 ``com.conradkramer.open``，可以先用Cydia安装，然后 ``dpkg -l`` 查看。

补全依赖之后，就可以 ``make package`` 生成新的 deb 包了。

## 搭建
deb 的源本质上就是需要特定结构的目录，基本的目录结构如下：

```
.
├── 12306_0.0.1-1+debug_iphoneos-arm.deb
├── 12306daemon_0.0.1-1+debug_iphoneos-arm.deb
├── Packages.bz2
└── Release
```

如上所示，除了 ``.deb`` 包文件以外，源目录中还包含 ``Packages.bz2`` 和 ``Release`` 两个文件。其中，Release是一个普通的文本文件，用于描述当前源的信息，示例内容如下：

```
Origin: Test Repo
Label: Test Repo
Suite: stable
Version: 1.0
Codename: ios
Architectures: iphoneos-arm
Components: main
Description: This is a test Cydia repo.
```

这些信息会在 Cydia 的源列表及 Tweak 搜索列表中显示。

``Packages.bz2`` 则是一个 bzip2 压缩过的文件，原始文件为 Packages，通过如下命令生成：

```bash
# 扫名当前目录下的 .deb 文件，生成 Packages 文件
dpkg-scanpackages -m . /dev/null > Packages

# 压缩 Packages 文件
bzip2 Packages
```

Packages 文件中包含源中每个包文件的信息，包括文件路径、大小、依赖、架构及校验信息等。
文件内容示例如下：

```
Package: 12306
Version: 0.0.1-2+debug
Architecture: iphoneos-arm
Maintainer: windy
Installed-Size: 720
Depends: mobilesubstrate, com.conradkramer.open
Filename: ./12306_0.0.1-1+debug_iphoneos-arm.deb
Size: 149474
MD5sum: ab455157951b24cb235766656b73d0c5
SHA1: caafa284cce8c45dbaa44c0de7e1d9ef4342870a
SHA256: a07fab6619b2f82344467f20d76a91ee6268f3e6d024bf9d6dae2b93d012629d
Section: Tweaks
Description: An awesome MobileSubstrate tweak!
Author: windy
Name: 12306

Package: 12306daemon
Version: 0.0.1-2+debug
Architecture: iphoneos-arm
Maintainer: windy
Installed-Size: 76
Depends: mobilesubstrate,com.conradkramer.open
Filename: ./12306daemon_0.0.1-1+debug_iphoneos-arm.deb
Size: 3374
MD5sum: eeddb216336577f199b5b6080e74c4fc
SHA1: 993bf3ba059caf9ab67a6456b523c1ec64a1b624
SHA256: daf8ad0f22bbae19c910ce1115d151a0d7cbf71cf0a8ff3bf4975f5bb2ecb9b6
Section: Tweaks
Description: An awesome MobileSubstrate tweak!
Author: windy
Name: 12306daemon

```

## 部署
部署比较简单，只需要在服务器上安装&&启动 nginx，将上述目录放置在 nginx 根目录下既可。也可以放置在子目录中，但在 Cydia 中输入源地址时，要包含相应的子目录。

## 测试
打开 Cydia ，在源编辑页面选择 ”添加“，输入服务器地：
![](/images/15033805128579.jpg)


点击 “添加”后，会自动更新源缓存，下载Release 和 Packages.bz2 文件。更新完成后，即可 ”搜索“ 中搜索安装我们的 Tweak 了。 Enjoy it.


