# Android 设备上使用 Termux 安装运行 gitlab-runner

## 安装 Termux

1. Termux: <https://f-droid.org/packages/com.termux/>
2. Termux-boot: <https://f-droid.org/packages/com.termux.boot/>

## 换源

Termux 默认软件源国内链接可能不顺畅，可以改用清华的源，如下：

```shell
# 执行如下命令更换三个源
termux-change-repo
```

## 安装并启用 sshd

该步骤主要是为了远程操作，避免在手机上大量输入。

```shell
# 安装 openssh
apt install openssh termux-services

# 启动 sshd
sshd

# 修改密码
passwd

# 获取用户名
whoami
```

完成后执行 `exit` 关闭会话，重新打开 APP 后执行：

```shell
sv-enable sshd

sv up sshd
```

使能 `sshd` 服务。

之后，在 PC/Mac 上执行:

```shell
adb forward tcp:8022 tcp:8022

ssh $(user)@127.0.0.1 -p 8022
```

即可远程登录到 Termux 中。

## 编译 gitlab-runner

### 1. 安装依赖

```shell
apt install golang git
```

### 2. clone 源码

```shell
git clone https://gitlab.com/gitlab-org/gitlab-runner.git -b v13.11.0
```

### 3. 安装 go 依赖 && 编译

```shell
cd gitlab-runner
go get 
go build
```

将生成的 `gitlab-runner` 可执行文件 copy 到 `$HOME/../var/bin/` 目录，即可完成安装。

### 注册 runner

和其他平台一致，执行 `gitlab-runner register` 注册即可。可能会有一些错误和警告，可以忽略。
注意 executor type 选择 `shell`

### 自启动 gitlab-runner

```shell
cd $HOME/../usr/var/service

mkdir -p gitlab-runner/log
cd gitlab-runner

ln -sf /data/data/com.termux/files/usr/share/termux-services/svlogger log/run

touch run down
chmod +x run
chmod +x run
```

在 `run` 中写入如下内容:

```shell
#!/bin/sh

exec gitlab-runner run --working-directory $HOME --config $HOME/.gitlab-runner/config.toml 2>&1
```

保存退出。

重启终端，执行 `sv-enable gitlab-runner` 启用自启动；`sv up gitlab-runner` 启动 gitlab-runner.

测试结果如下图：

![](https://pan.xnure.com/OneDrive/Pics/blog/16214386035933.jpg ':size=600')

## 参考链接

1. [Termux 源使用帮助](http://mirrors.ustc.edu.cn/help/termux.html)
2. [Termux-services](https://wiki.termux.com/wiki/Termux-services)
3. [Termux:Boot](https://wiki.termux.com/wiki/Termux:Boot)
