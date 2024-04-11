# XYBot 微信机器人

<div style="text-align: center;">
    <img alt="XYBot微信机器人logo" width="240" src="https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/logo/xybot_logo.png?raw=true">
</div>

XYBot是一个基于docker和pywxdll hook注入的微信机器人。😊 具有高度可自定义性，支持自我编写插件。🚀

XYBot提供了多种功能，包括获取天气🌤️、获取新闻📰、ChatGPT聊天🗣️、Hypixel玩家查询🎮、随机图片📷、随机链接🔗、随机群成员👥、签到✅、查询积分📊、积分榜🏆、积分转送💰、积分抽奖🎁、积分红包🧧等。🎉

XYBot拥有独立的经济系统，其中基础货币称为”积分“。💰

XYBot还提供了管理员功能，包括修改积分💰、修改白名单📝、重置签到状态🔄、获取机器人通讯录📚、获取群成员列表👥、热加载/卸载/重载插件🔄等。🔒

XYBot详细的部署教程可以在项目的Wiki中找到。📚 同时，XYBot还支持自我编写插件，用户可以根据自己的需求和创造力编写自定义插件，进一步扩展机器人的功能。💡

✅高度可自定义！
✅支持自我编写插件！

<div style="text-align: center;">
    <a href="https://opensource.org/licenses/"><img src="https://img.shields.io/badge/License-GPL%20v3-red.svg" alt="GPLv3 License"></a>
    <a href="https://github.com/HenryXiaoYang/XYBot"><img src="https://img.shields.io/badge/Version-0.0.5-orange.svg" alt="Version"></a>
    <a href="https://yangres.com"><img src="https://img.shields.io/badge/Blog-@HenryXiaoYang-yellow.svg" alt="Blog"></a>
</div>

## 功能列表

用户功能:

- 获取天气🌤️
- 获取新闻📰
- ChatGPT🗣️
- Hypixel玩家查询🎮
- 随机图图📷
- 随机链接🔗
- 随机群成员👥
- 签到✅
- 查询积分📊
- 积分榜🏆
- 积分转送💰
- 积分抽奖🎁
- 积分红包🧧

管理员功能:

- 修改积分💰
- 修改白名单📝
- 重置签到状态🔄
- 获取机器人通讯录📚
- 获取群成员列表👥
- 热加载/卸载/重载插件🔄

## 功能演示

这里只展示了一小部分功能，所有功能请见wiki

**
_[⭐️XYBot用户功能介绍WIKI⭐️](https://github.com/HenryXiaoYang/XYBot/wiki/%E7%94%A8%E6%88%B7%E5%8A%9F%E8%83%BD%E4%BB%8B%E7%BB%8D)_
**

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

## 部署💻

详细教程请查看Wiki

**_[⭐️XYBot部署教程Wiki⭐️](https://github.com/HenryXiaoYang/XYBot/wiki/%E9%83%A8%E7%BD%B2%E6%95%99%E7%A8%8B)_**

## 自我编写插件🧑‍💻

请参考模板插件：

**_[⭐️模板插件仓库⭐️](https://github.com/HenryXiaoYang/XYBot-Plugin-Framework)_**

## FAQ❓❓❓

#### VNC 如何设置密码：

1. 在终端docker ps 找出XYBot的容器的CONTAINER ID
2. 执行docker exec -it (XYBot的容器的CONTAINER ID) /bin/sh
3. 在容器内执行x11vnc --storepasswd
4. 然后跟着提示设置密码
5. 编辑这个文件/etc/supervisord.d/x11vnc.conf
6. 在第二行的command=x11vnc -forever -shared末尾加入-rfbauth /home/app/.vnc/passwd
7. 最后应该是command=x11vnc -forever -shared -rfbauth /home/app/.vnc/passwd
8. exit退出docker然后重启docker
9. 现在用网页连接vnc应该要输入密码

#### ARM架构能不能运行?🤔️

~~不行😩~~

可以是可以是，虚拟层自己套吧

真的不嫌烦吗？

#### 用的什么微信版本?🤔️

3.6.0.18😄

#### 使用有没有封号风险?🤔️

我连续用了~~3 6~~ 9个月了，没被封😄

## XYBot交流群

<div style="text-align: center;">
    <img alt="XYBot交流群二维码" width="360" src="https://file.yangres.com/xybot-wechatgroup.jpeg">
</div>

## Credit

https://github.com/HenryXiaoYang/pywxdll

https://github.com/ChisBread/wechat-service/

https://github.com/cixingguangming55555/wechat-bot

https://github.com/chisbread/wechat-box

## ⭐️Star History⭐️

<div style="text-align: center">
    <picture>
      <source
        media="(prefers-color-scheme: dark)"
        srcset="
          https://api.star-history.com/svg?repos=HenryXiaoYang/XYBot&type=Date&theme=dark
        "
      />
      <source
        media="(prefers-color-scheme: light)"
        srcset="
          https://api.star-history.com/svg?repos=HenryXiaoYang/XYBot&type=Date
        "
      />
      <img
        alt="XYBot Star History"
        width="600"
        src="https://api.star-history.com/svg?repos=HenryXiaoYang/XYBot&type=Date"
      />
    </picture>
</div>

