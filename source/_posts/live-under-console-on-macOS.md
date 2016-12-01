---
title: 在macOS下高效使用命令行
date: 2016-08-31 00:46:08
tags: [macOS,Console]
---

相对于Windows和Linux，macOS最吸引人的地方在于精致的图形界面与强大的命令行的完美结合。熟悉macOS历史的同学应该知道，macOS的内核衍生自FreeBSD，属于正统Unix。因此，macOS下的各种终端命令的参数格式都是BSD式，对于习惯了Linux参数格式的我来讲有些许不适用，好在有Homebrew的加持，可以很方便的改回到Linux方式：

## 使用Linux式命令

Linux下的标准命令包含在由GNU提供的coreutils包中，在Mac下可以通过Homebrew安装coreutils包来获取支持。

```shell
brew install coreutils
```

安装之后，默认coreutils的命令都加上了前缀``g``，比如要使用coreutils提供的``ls``命令，需要使用``gls``来执行。当然，也可以像我一样，把coreutils的命令设为默认，取代macOS提供的命令。在你的shell配置文件：bash是``~/.bashrc``，zsh是``~/.zshrc``中追加如下两条配置：

```shell
# 把coreutils的bin目录放在PATH前边，这样就优先执行coreutils的命令
PATH="/usr/local/opt/coreutils/libexec/gnubin:$PATH"
# 优先调用coreutls的man信息
MANPATH="/usr/local/opt/coreutils/libexec/gnuman:$MANPATH"
```

coreutils的``ls``命令默认没有颜色，同样在配置文件中加入下边这行：

```shell
alias ls="ls --color=tty"
```

## 修改Homebrew源

由于众所周知的原因，西方资本主义国家的大部分网站或被屏蔽、或被干扰，无法正常流利地为国内用户服务。而Homebrew的两个主要部分：git repo (github)和binary(bintray)不幸都在其中。为了加快Homebrew的下载速度，除了搬梯子架代理之外，我们还可以使用国内良心组织/个人提供国内镜像。比如中科大LUG（Linux User Group），使用如下命令修改：

```shell
# 详见https://lug.ustc.edu.cn/wiki/mirrors/help/brew.git
# 替换homebrew默认源
cd /usr/local
git remote set-url origin git://mirrors.ustc.edu.cn/brew.git

# 详见https://lug.ustc.edu.cn/wiki/mirrors/help/homebrew-bottles
# 替换homebrew bottles默认源
echo 'export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.ustc.edu.cn/homebrew-bottles' >> ~/.bashrc
```

还有其他组织/个人，比如[搬](http://ban.ninja/)，[tycdn](http://homebrew-mirror-china.tycdn.net/)等等，修改方式与中科大源一致，只是地址不一样。

## 让终端程序使用代理

在Mac下，可以在``设置``->``网络``中方便地为应用程序设置网络代理，包括``HTTP``、``HTTPS``、``Socks``等各种协议。但是这些都是针对图形界面应用的，对于终端程序，这些设置并不起作用，要让终端程序通过代理链接网络，还需要进行其他设置。

* 环境变量

  对于支持从环境变量中读取代理配置的程序，比如wget,git等，可以通过设置``http_proxy``或者``https_proxy``环境变量使代理生效。

  ```shell
  export http_proxy=http://ip:port
  wget http://www.baidu.com
  ```

* proxychains

  对于不支持环境变量配置代理的应用，或者代理类型不是http/https，比如shadowsocks、GoAgent使用的socks5协议，那么上边的方法就无效了。对于这种情况，可以使用``proxychains``命令来使代理生效。

  首先通过Homebrew安装``proxychains-ng``包：

  ```shell
  brew install proxychains-ng
  ```

  之后需要对proxychain进行配置，proxychains的配置文件路径是``/usr/local/etc/proxychains.conf``。打开配置文件，注释掉最后一行的默认配置，在之后按照``协议 IP 端口 用户名(可选) 密码(可选)``的格式添加自己的代理服务器配置。示例如下：

  ```shell
  # ProxyList format
  #       type  ip  port [user pass]
  #       (values separated by 'tab' or 'blank')
  #
  #       only numeric ipv4 addresses are valid
  #
  #
  #        Examples:
  #
  #            	socks5	192.168.67.78	1080	lamer	secret
  #		http	192.168.89.3	8080	justu	hidden
  #	 	socks4	192.168.1.49	1080
  #	        http	192.168.39.93	8080
  #
  #
  #       proxy types: http, socks4, socks5
  #        ( auth types supported: "basic"-http  "user/pass"-socks )
  #
  [ProxyList]
  # add proxy here ...
  # meanwile
  # defaults set to "tor"
  #socks4 	127.0.0.1 9050
  socks5 127.0.0.1 1080
  ```

  proxychains本身支持``代理链``，顾名思义就是通过代理A连接代理B再连接代理C...连接目标服务器，如需使用代理链，只需要按次序将代理服务器信息填写到配置文件中既可。

* 其他程序

  有些程序自身支持代理，比如curl和git等。这里针对这些程序介绍一下它们的代理设置方法。

  * curl

    curl支持通过配置文件设置代理的方法，打开curl配置文件（``~/.curlrc``），在其中写入：

    ```shell
    proxy="protocal://ip:port"
    # protocal可以是http、https、socks4/5
    ```

    ​

    * git

      git也支持通过将代理信息写入配置文件的方式设置代理：

      ```shell
      # git支持http、https、socks代理
      git config --global http.proxy "protocal://ip:port"
      git config --global https.proxy "protocal://ip:port"
      ```

      或者直接打开git配置文件（``~/.gitconfig``），写入如下配置：

      ```shell
      [http]
      	proxy="protocal://ip:port"
      [https]
      	proxy="protocal://ip:port"
      ```​
      
