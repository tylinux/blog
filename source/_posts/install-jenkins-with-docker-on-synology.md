---
title: 在群晖中使用 Docker 安装 Jenkins
date: 2018-12-30 18:29:07
tags: [docker,jenkins,synology]
---

之前家里的 Jenkins 是跑在媳妇儿的老戴尔笔记本上，平台跑一些 DDNS、Blog 自动更新以及 Github Mirros 的任务。有种杀机用牛刀的感觉，为了响应国家节能减排的号召 (:D，准备把 Jenkins 迁移到家里的黑群晖上。但在折腾的过程中碰到一些问题，特此记录。

## 下载镜像

下载的时候要注意，群晖的 Docker 里推荐的 Jenkins 是个老版本，要安装新版本的才行，不然安装插件的时候可能会报版本过低的错误。
![-w1057](https://i.loli.net/2018/12/30/5c289daf74ad9.jpg)

`latest` Tag 里的镜像是基于 Debian，相对比较大，1GB 左右。对容量有有求的可以使用 `alpine` tag，只有不到 300MB。

## 启动镜像

这里就是出问题的地方了。为了方便安装，我把 `/var/jenkins_home` 这个目录映射到群晖里的某个目录下。比如这样：
![-w651](https://i.loli.net/2018/12/30/5c289daf556ee.jpg)

然后在启动的时候，容器异常终止了，报错信息是：

```
touch: cannot touch '/var/jenkins_home/copy_reference_file.log': Permission denied
Can not write to /var/jenkins_home/copy_reference_file.log. Wrong volume permissions?
```

错误信息很明显，我把 `/var/jenkins_home` 映射到了本地目录，但是容器里对这个目录没有读写权限，所以就GG了。

参考 [[1]](https://github.com/jenkinsci/docker/blob/master/Dockerfile) 中可以知道，Docker 中运行的用户是 jenkins:jenkins, GID、UID 均为 1000，而这个用户没有 `DockerExt` 这个目录的读写权限，所以将 `DockerExt1 的 owner 修改为1000:1000 应该就可以解决问题。然而，我在群晖中并没有找到修改文件目录权限的地方，继续搜索。

在某个 Github issue 中有人提到，可以将 docker 中运行的用户指定为 root，即 UID 0 来测试是否是文件目录权限问题。那么我能不能这个样子搞一下，先让这个镜像跑起来呢？事实上，不行，群晖的 Docker 图形化界面并没有提供指定用户的能力。。有同志提出，可以先创建一个镜像，然后导出成 JSON 文件，修改后再导入，但是在导出的 JSON 文件中，我也没有找到可以修改用户的地方。GG。

## 解决方案

经过一番探索，我这样搞成功了，自我感觉还算优雅（尝试通过 SSH 登录后修改 `DockerExt` 的 owner 为 1000:1000，然而没有暖用）：

1. 打开群晖系统的 SSH 登录功能：`Control Panel` -> `Terminal & SNMP` -> `Enable SSH Service`
    
2. SSH 登录后执行 `cat /etc/passwd`，找到当前用户的 UID
    ![-w562](https://i.loli.net/2018/12/30/5c289daf45272.jpg)

3. 执行如下命令启动 Docker 实例
    
    ```bash
    sudo docker run -u 1027 \ # 指定运行的用户
    -p 8080:8080 -p 50000:50000 \ # 端口映射
    -v /volume4/DockerExt/JenkinsHome/:/var/jenkins_home \ # 文件目录映射
    jenkins/jenkins:alpine # 待启动镜像
    ```
    因为我们指定在 Docker 中使用 `UID=1027` 这个用户执行，而这个用户对于 `/volume4/DockerExt/JenkinsHome/` 这个目录是权限的，所以 Jenkins 就可以正常运行了～
    
4. 返回群晖的图形化 Docker 界面重启该实例

## 参考
[1]. [https://github.com/jenkinsci/docker/blob/master/Dockerfile](https://github.com/jenkinsci/docker/blob/master/Dockerfile)
