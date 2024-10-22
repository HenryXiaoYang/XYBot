# XYBot 微信机器人

<p align="center">
    <img alt="XYBot微信机器人logo" width="240" src="https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/logo/xybot_logo.png?raw=true">
</p>

XYBot是一个可运行于Linux和Windows的基于Hook的微信机器人。😊 具有高度可自定义性，支持自我编写插件。🚀

XYBot提供了多种功能，包括获取天气🌤️、获取新闻📰、Hypixel玩家查询🎮、战争雷霆玩家查询🎮、随机图片📷、随机链接🔗、五子棋♟️、签到✅、查询积分📊、积分榜🏆、积分转送💰、积分抽奖🎁、积分红包🧧等。🎉

XYBot还提供了AI相关的功能，包括ChatGPT🗣️，Dalle🎨。🤖

XYBot拥有独立的经济系统，其中基础货币称为”积分“。💰

XYBot还提供了管理员功能，包括修改积分💰、修改白名单📝、重置签到状态🔄、获取机器人通讯录📚、热加载/卸载/重载插件🔄等。🔒

XYBot详细的部署教程可以在项目的Wiki中找到。📚 同时，XYBot还支持自我编写插件，用户可以根据自己的需求和创造力编写自定义插件，进一步扩展机器人的功能。💡

✅高度可自定义！
✅支持自我编写插件！

<p align="center">
    <a href="https://opensource.org/licenses/"><img src="https://img.shields.io/badge/License-GPL%20v3-red.svg" alt="GPLv3 License"></a>
    <a href="https://github.com/HenryXiaoYang/XYBot"><img src="https://img.shields.io/badge/Version-2.0.0-orange.svg" alt="Version"></a>
    <a href="https://yangres.com"><img src="https://img.shields.io/badge/Blog-@HenryXiaoYang-yellow.svg" alt="Blog"></a>
</p>

## 公告

由于需要频繁的更新维护，XYBot版本号格式将会发生变化，v0.0.7后面的版本号将会按照以下格式进行更新：

v大版本(hook/微信版本变动时更改).功能版本.Bug修复版本

例如：

- v1.0.1是v1.0.0的Bug修复版本
- v1.1.0是v1.0.0的功能版本
- v1.1.1是v1.1.0的Bug修复版本

## 功能列表

用户功能:

- 获取天气🌤️
- 获取新闻📰
- ChatGPT🗣️
- Dalle🎨
- Hypixel玩家查询🎮
- 战争雷霆玩家信息查询💣
- 随机图图📷
- 随机链接🔗
- 五子棋♟️
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
- 热加载/卸载/重载插件🔄
- 查看已加载插件ℹ️

## XYBot 文档 📄

文档中有完整的功能介绍，部署教程，配置教程，插件编写教程。

**[🔗XYBot 文档](https://henryxiaoyang.github.io/XYBot)**

## 功能演示

菜单
![Menu Example](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/menu.png?raw=true)

随机图片
![Random Picture Example](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/random_picture.png?raw=true)

ChatGPT
![ChatGPT Example 1](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/gpt3.png?raw=true)
![ChatGPT Example 2](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/gpt4.png?raw=true)

私聊ChatGPT
![Private ChatGPT Example](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/private_gpt.png?raw=true)

天气查询
![Weather Example](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/weather.png?raw=true)

五子棋
![Gomoku Example](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/gomoku.png?raw=true)

## 快速开始🚀

### Linux/Docker
```shell
docker pull henryxiaoyang/xybot:v2.0.0

docker run -d --name XYBot \
  -e WC_AUTO_RESTART=yes \
  -p 4000:8080 \
  --add-host dldir1.qq.com:127.0.0.1 \
  -v XYBot:/home/app/XYBot/ \
  -v XYBot-wechatfiles:/home/app/WeChat\ Files/ \
  --tty \
  henryxiaoyang/xybot:v2.0.0
```

### Windows

需要 Git 与 [Python3](https://www.python.org/downloads/release/python-3127/) 与 [微信3.9.10.27](https://github.com/lich0821/WeChatFerry/releases/download/v39.2.4/WeChatSetup-3.9.10.27.exe)

```shell
git clone https://github.com/HenryXiaoYang/XYBot.git
cd XYBot
pip install -r requirements.txt

# 请手动启动微信

# 启动微信后执行
python start.py
```

## 自我编写插件🧑‍💻

请参考模板插件：

**[🔗模板插件仓库️](https://github.com/HenryXiaoYang/XYBot-Plugin-Framework)**

## XYBot交流群

<p align="center">
    <img alt="XYBot二维码" width="360" src="https://file.yangres.com/xybot-wechatgroup.jpeg">
</p>

[**🔗图片会被缓存，点我查看最新二维码**](https://file.yangres.com/xybot-wechatgroup.jpeg)

## 捐赠

<p align="center"><img alt="爱发电二维码" width="360" src="https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/README/aifadian.jpg?raw=true"></p>
<p align="center">你的赞助是我创作的动力！🙏</p>

## FAQ❓❓❓

#### ARM架构能不能运行?🤔️

不行

#### 用的什么微信版本?🤔️

3.9.10.27😄

#### 最长能运行多久？🤔️

XYBot内置了防微信自动退出登录功能，可以保持长时间运行。

## 特别感谢

https://github.com/ChisBread 感谢提供了Docker容器相关的信息！

https://github.com/lich0821 感谢这个项目的作者写的wcferry！

## ⭐️Star History⭐️

<p align="center">
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
</p>

