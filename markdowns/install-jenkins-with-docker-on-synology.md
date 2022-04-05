# 在群晖中使用 Docker 安装 Jenkins

之前家里的 Jenkins 是跑在媳妇儿的老戴尔笔记本上，平台跑一些 DDNS、Blog 自动更新以及 Github Mirros 的任务。有种杀机用牛刀的感觉，为了响应国家节能减排的号召 (:D，准备把 Jenkins 迁移到家里的黑群晖上。但在折腾的过程中碰到一些问题，特此记录。

<!--more-->

## 下载镜像

下载的时候要注意，群晖的 Docker 里推荐的 Jenkins 是个老版本，要安装新版本的才行，不然安装插件的时候可能会报版本过低的错误。
![-w1057](https://i.loli.net/2018/12/30/5c289daf74ad9.jpg ':size=600')

`latest` Tag 里的镜像是基于 Debian，相对比较大，1GB 左右。对容量有有求的可以使用 `alpine` tag，只有不到 300MB。

## 启动镜像

这里就是出问题的地方了。为了方便安装，我把 `/var/jenkins_home` 这个目录映射到群晖里的某个目录下。比如这样：
![-w651](https://i.loli.net/2018/12/30/5c289daf556ee.jpg ':size=600')

然后在启动的时候，容器异常终止了，报错信息是：

```
touch: cannot touch '/var/jenkins_home/copy_reference_file.log': Permission denied
Can not write to /var/jenkins_home/copy_reference_file.log. Wrong volume permissions?
```

参考 [[1]](https://github.com/jenkinsci/docker/blob/master/Dockerfile) 中可以知道，Docker 中运行的用户是 jenkins:jenkins, GID、UID 均为 1000，而这个用户没有 `DockerExt` 这个目录的读写权限，导致程序异常终止。解决方案如下：

## 解决方案
### 方案一：
本方案需要 SSH 到 Synology 系统中，通过命令行的方式创建 Docker Container

#### 优点：
不需要修改文件目录属性

#### 缺点：

1. 需要 SSH 登录，输入命令创建 Docker Container
2. 在容器中执行 `ssh-keygen` 或者 `git clone` 命令时会报 `No user exists for uid xxxx` 错误

#### 操作步骤
1. 打开群晖系统的 SSH 登录功能：`Control Panel` -> `Terminal & SNMP` -> `Enable SSH Service`
    
2. SSH 登录后执行 `cat /etc/passwd`，找到当前用户的 UID
    ![-w562](https://i.loli.net/2018/12/30/5c289daf45272.jpg ':size=600')

3. 执行如下命令启动 Docker 实例
    
    ```bash
    sudo docker run -u 1027 \ # 指定运行的用户
    -p 8080:8080 -p 50000:50000 \ # 端口映射
    -v /volume4/DockerExt/JenkinsHome/:/var/jenkins_home \ # 文件目录映射
    jenkins/jenkins:alpine # 待启动镜像
    ```
    因为我们指定在 Docker 中使用 `UID=1027` 这个用户执行，而这个用户对于 `/volume4/DockerExt/JenkinsHome/` 这个目录是权限的，所以 Jenkins 就可以正常运行了～
    
4. 返回群晖的图形化 Docker 界面重启该实例

### 方案二：

修改本地文件目录属性为 `777`（在群晖系统中， 修改 owner 为 1000:1000 的方式无效）

#### 执行步骤：
1. 同方案一一致，打开 SSH 并登录
2. 执行 `sudo chown -R 777 /volume4/DockerExt/JenkinsHome/` 修改目录权限
3. 在图形管理界面中创建 Container


### 方案三
创建自己的 Dockerfile

#### 操作步骤：
创建 `Dockerfile`，内容如下（基于alpine tag，latest可参考 [[2]](https://github.com/jenkinsci/docker/issues/177)）

```Dockerfile
FROM jenkins/jenkins:alpine
USER root
ENV GOSU_VERSION 1.11
RUN set -eux; \
    \
    apk add --no-cache --virtual .gosu-deps \
    dpkg \
    gnupg \
    ; \
    \
    dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"; \
    wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch"; \
    wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc"; \
    \
    # verify the signature
    export GNUPGHOME="$(mktemp -d)"; \
    # for flaky keyservers, consider https://github.com/tianon/pgp-happy-eyeballs, ala https://github.com/docker-library/php/pull/666
    gpg --batch --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4; \
    gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu; \
    command -v gpgconf && gpgconf --kill all || :; \
    rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc; \
    \
    # clean up fetch dependencies
    apk del --no-network .gosu-deps; \
    \
    chmod +x /usr/local/bin/gosu; \
    # verify that the binary works
    gosu --version; \
    gosu nobody true
```

在同目录下创建 `entrypoint.sh` 文件

```bash
#!/bin/bash
set -e
if [ "$1" = 'jenkins' ]; then
    chown -R jenkins:jenkins "$JENKINS_HOME"
    exec gosu "$@"
fi
exec "$@"
```

保存后执行：

```bash
docker build -t jenkins:alpine -t
```

原理是在启动 Docker 容器的时候，自动修改 `$JENKINS_HOME` 目录的 owner。

## 参考
[1]. [https://github.com/jenkinsci/docker/blob/master/Dockerfile](https://github.com/jenkinsci/docker/blob/master/Dockerfile)
[2]. [https://github.com/jenkinsci/docker/issues/177](https://github.com/jenkinsci/docker/issues/177)