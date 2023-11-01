
# XYBot 微信机器人
基于docker和pywxdll hook注入的微信机器人🤖️

高度可自定义!!!😊



[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-red.svg)](https://opensource.org/licenses/)[![Version](https://img.shields.io/badge/Version-0.0.2-orange.svg)](https://github.com/HenryXiaoYang/XYBot)
[![Blog](https://img.shields.io/badge/Blog-@HenryXiaoYang-yellow.svg)](http://121.5.152.172/)
## 功能列表
用户功能:
- 菜单
- 随机图片
- 随机链接
- 群签到
- 群积分功能
- ChatGPT
- 白名单
- 天气查询
- 新闻查询
管理员功能:
- 修改积分
- 修改白名单
- 重置签到状态
- 获取机器人通讯录
- 获取群成员列表



## 功能演示

用户功能:🧑‍🏫

菜单
![image](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_1_menu.gif?raw=true)


随机图片
![image](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_2_randompic.gif?raw=true)

群签到
![image](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_3_Signin.gif?raw=true)

积分榜
![image](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_4_pointrank.gif?raw=true)

ChatGPT
![image](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_5_gpt.gif?raw=true)

天气查询
![image](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_6_weather.gif?raw=true)

新闻查询
![image](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_7_news.gif?raw=true)

管理员功能:🤔️

管理积分
![image](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_8_managepoint.gif?raw=true)

管理白名单
![image](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_9_manegewhitelist.gif?raw=true)

获取群成员列表
![image](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_10_getgroupmemberlist.gif?raw=true)


## 部署💻

服务器配置要求至少要2核2G✅

2核2G运行这个CPU占用率飙到100%了😭

推荐4核4G✅

注意⚠！ 不支持arm架构️❌

微信版本：3.6.0.18

已知问题: VNC无法正确显示部分中文🙅

⚠️⚠️⚠️不在调试机器人时请把4000端口关掉, 端口被扫到就麻烦了⚠️⚠️⚠️


### 1. 安装Docker

装好了可跳过

链接🔗：

https://docs.docker.com/get-docker/

### 2. 拉取/启动Docker镜像
```bash
#拉取镜像
docker pull henryxiaoyang/xybotwechat
```

```bash
#启动Docker
docker run --name xybotwechat \
    -e HOOK_PROC_NAME=WeChat \
    -e HOOK_DLL=auto.dll \
    -e TARGET_AUTO_RESTART="yes" \
    -e INJ_CONDITION="[ \"\`sudo netstat -tunlp | grep 5555\`\" != '' ] && exit 0 ; sleep 5 ; curl 'http://127.0.0.1:8680/hi' 2>/dev/null | grep -P 'code.:0'" \
    -e TARGET_CMD=wechat-start \
    -p 4000:8080 -p 5555:5555 -p 5900:5900 \
    --add-host=dldir1.qq.com:127.0.0.1 \
    henryxiaoyang/xybotwechat
```

### 3. 打开http://<服务器IP(本地部署是127.0.0.1)>:4000/vnc.html 并登陆微信

然后右键桌面-->Application-->Shells-->Bash

注意⚠️ 已知问题：有些中文不能正常显示，bash无法复制粘贴

![pic11.png](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_11.png?raw=true)

![pic12.png](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_12.png?raw=true)

```bash
#一个一个执行

git clone https://github.com/HenryXiaoYang/XYBot.git
#如果上面的太慢的话可以用这个
git clone https://kkgithub.com/HenryXiaoYang/XYBot.git

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

![pic13.png](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_13.png?raw=true)



### 5. 启动机器人
```bash
#启动机器人
python3 start.py
```
看到机器人口口成功即代表成功启动

之后启动机器人都用这个

![pic14.png](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_14.png?raw=true)

### 6. 关闭，修改管理员
先向机器人发一条消息然后按control+c中断运行

![pic15.png](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/XYBot_15.png?raw=true)

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
看到机器人启动成功即代表成功启动

![pic14.png](https://github.com/HenryXiaoYang/XYBot/blob/main/readmepics/pic14.png?raw=true)

## FAQ❓❓❓

#### ARM架构能不能运行?🤔️

不行😩

#### 用的什么微信版本?🤔️

3.6.0.18😄

#### 使用有没有封号风险?🤔️

我连续用了3个月了，没被封😄



## Credit
https://github.com/HenryXiaoYang/pywxdll

https://github.com/ChisBread/wechat-service/

https://github.com/cixingguangming55555/wechat-bot

https://github.com/chisbread/wechat-box