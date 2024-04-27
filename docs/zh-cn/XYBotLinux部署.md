# XYBot Linux部署

这一页写了在Linux上部署XYBot的方法。

本篇部署教程适用于`XYBot v0.0.6`。

## 前言

在Linux上部署`XYBot`需要用到`Docker`，`Docker`容器中运用了`wine`，它对环境要求**极高**。

[已知可以部署的发行版：](https://github.com/ChisBread/wechat-service/issues/1#issuecomment-1252083579)

- `Ubuntu`
- `Arch`
- `Debian`
- `DSM6.2.3`
- `DSM7.0`

不可部署的发行版：

- `CentOS`

欢迎各位开`issue`或者`pull request`来反馈！

[CentOS部署失败](https://github.com/ChisBread/wechat-service/issues/1)

由于运行PC版微信将消耗很多资源，请确认服务器配置。

服务器配置要求：

- 2核2G以上

## 部署

### 1. 安装Docker

装好了可跳过

官方教程链接🔗：

https://docs.docker.com/get-docker/

### 2. 安装Docker Compose

一样，已装好可跳过

https://docs.docker.com/compose/install/

### 3. 拉取Docker镜像

这一步以及后面遇到权限问题请在前面加个`sudo`。

```bash
docker pull henryxiaoyang/wechat-service-xybot:latest
```

### 4. 启动容器

```bash
docker run -it --name wechat-service-xybot  \
    -e HOOK_PROC_NAME=WeChat \
    -e HOOK_DLL=auto.dll \
    -e TARGET_AUTO_RESTART="yes" \
    -e INJ_CONDITION="[ \"\`sudo netstat -tunlp | grep 5555\`\" != '' ] && exit 0 ; sleep 5 ; curl 'http://127.0.0.1:8680/hi' 2>/dev/null | grep -P 'code.:0'" \
    -e TARGET_CMD=wechat-start \
    -p 4001:8080 -p 5556:5555 -p 5901:5900 \
    --add-host=dldir1.qq.com:127.0.0.1 \
    -v XYBot:/home/app/XYBot \
    henryxiaoyang/wechat-service-xybot:latest
```

### 5. 登陆微信

在浏览器中打开`http://<你的ip地址>:4000/vnc.html`访问VNC。

扫描微信二维码并登录。

### 6. 配置XYBot设置

如果使用的步骤4的启动指令，XYBot的文件已被持久化到`/var/lib/docker/volumes/XYBot-vol`，也就是`XYBot-vol`卷。

```bash
cd /var/lib/docker/volumes/XYBot-vol/_data
```

在这个目录下可以看到`main_config.yml`，修改这个文件即可。

### 7. 重启容器

```bash
docker restart wechat-service-xybot
```

修改主设置后需要重启容器。重启后需要访问VNC重新扫码并登陆微信！

### 8. 测试是否部署成功

在微信中向XYBot私聊`/菜单`，如果返回菜单则部署成功。

可以开始用XYBot了！

如果失败，可以看看容器日志并发`issue`询问。

```bash
docker logs wechat-service-xybot -f --tail 100
```

### 9. 设置VNC密码

VNC默认是没有密码的，强烈推荐设置密码。万一被人连上了，那个人干了什么可就说不清咯。😭

不信？懒？那我放一张图警告一下大家：

![VNC Set Password Warning](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/wiki/xybot_linux_deployment/vnc_set_password_1.png?raw=true)

~~你看！死亡回放！~~

你设置不设置吧？

#### 1. 进入容器bash

```bash
docker exec -it wechat-service-xybot /bin/bash
```

#### 2. 设置密码

请设置一个强密码避免暴力破解

```bash
# 跟提示设置密码
x11vnc --storepasswd
```

#### 3. 编辑文件

将第二行改成：

```command=x11vnc -forever -shared -rfbauth /home/app/.vnc/passwd```

```bash
# 修改这个文件
vi /etc/supervisord.d/x11vnc.conf
```

现在第二行应该是：

```command=x11vnc -forever -shared -rfbauth /home/app/.vnc/passwd```

#### 4. 退出容器bash

```bash
exit
```

#### 5. 重启容器

```bash
docker restart wechat-service-xybot
```

现在用网页连接vnc应该要输入密码

#### 6. 登陆VNC后重新扫描二维码登陆微信

登陆后，XYBot会自动启动


