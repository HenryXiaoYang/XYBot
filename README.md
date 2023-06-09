# XYBot
基于docker和pywxdll hook注入的微信机器人

高度可自定义！

## 功能列表

1. 菜单
2. 随机图片
3. 签到
4. 查询积分
5. 积分榜
6. ChatGPT
7. 管理员功能(修改积分啥的)

## 功能演示
### 1. 菜单

![pic1.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic1.png)

![pic2.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic2.png)

### 2. 随机图片

![pic3.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic3.png)

### 3. 签到

随机1-20点积分

![pic4.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic4.png)

### 4. 查询积分

![pic5.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic5.png)

### 5. 积分榜

![pic6.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic6.png)

### 6. ChatGPT

无白名单

![pic7.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic7.png)

有白名单

![pic8.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic8.png)

### 7. 管理员功能

![pic9.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic9.png)

![pic10.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic10.png)

## 如何使用

### 0. 写在前面
服务器配置要求至少要2核2G

2核2G运行这个CPU占用率飙到100%了

推荐4核4G

注意⚠！ 不支持arm架构️

注意⚠！ 不支持arm架构️

注意⚠！ 不支持arm架构️


### 1. 安装Docker

装好了可跳过

链接🔗：

https://docs.docker.com/get-docker/

### 2. 拉取/启动Docker镜像
```bash
#拉取镜像
sudo docker pull henryxiaoyang/xybotwechat
```
```bash
#启动Docker
sudo docker run --name xybotwechat \
    -e HOOK_PROC_NAME=WeChat \
    -e HOOK_DLL=auto.dll \
    -e TARGET_AUTO_RESTART="yes" \
    -e INJ_CONDITION="[ \"\`sudo netstat -tunlp | grep 5555\`\" != '' ] && exit 0 ; sleep 5 ; curl 'http://127.0.0.1:8680/hi' 2>/dev/null | grep -P 'code.:0'" \
    -e TARGET_CMD=wechat-start \
    -p 8080:8080 -p 5555:5555 -p 5900:5900 \
    --add-host=dldir1.qq.com:127.0.0.1 \
    henryxiaoyang/xybotwechat
```

### 3. 打开http://<服务器IP(本地部署是127.0.0.1)>:8080/vnc.html 并登陆微信

然后右键桌面-->Application-->Shells-->Bash

注意⚠️ 已知问题：有些中文不能正常显示，bash无法复制粘贴

![pic11.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic11.png)

![pic12.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic12.png)

```bash
#一个一个执行

git clone https://github.com/HenryXiaoYang/XYBot.git
#如果上面的太慢的话可以用这个
git clone https://kgithub.com/HenryXiaoYang/XYBot.git

cd XYBot

pip install -r requirements.txt
```

### 4. 配置机器人
```bash
#修改配置
vim config.yml
```
按i修改，esc退出修改

要修改openai_api_base为ChatGPT的API网址 openai_api_key为ChatGPT API的Key

修改完esc后依次按 :wq 然后回车保存退出

![pic13.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic13.png)



### 5. 启动机器人
```bash
#启动机器人
python3 start.py
```
看到机器人口口成功即代表成功启动

之后启动机器人都用这个

![pic14.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic14.png)

### 6. 关闭，修改管理员
先向机器人发一条消息然后按control+c中断运行

![pic15.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic15.png)

可以从图中看到，收到的消息中有键叫'id1'和'wxid'。如果你是私信了机器人，应该在admins中填入'wxid'的值；如果你是群发了机器人，那么应该在admins中填入'id1'的值

```bash
#修改配置
vim config.yml
```
按i修改，esc退出修改

在admins中填入'wxid'的值或'id1'的值

修改完esc后依次按 :wq 然后回车保存退出

### 7. 再次启动机器人
还是这个命令
```bash
#启动机器人
python3 start.py
```
看到机器人口口成功即代表成功启动

![pic14.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic14.png)

## Credits
https://kgithub.com/HenryXiaoYang/pywxdll

https://kgithub.com/ChisBread/wechat-service/

https://kgithub.com/cixingguangming55555/wechat-bot

https://kgithub.com/chisbread/wechat-box