# XYBot功能介绍

这一页介绍了所有官方XYBot微信机器人用户可使用的功能、命令。

本介绍对应v0.0.6版本的XYBot。

功能分为了4类：

- 实用功能⚙️
- 娱乐功能🔥
- 积分功能💰
- 管理员功能🔧

?> 所有功能都可用菜单查询。

大部分管理员功能需要管理员权限，可以在位于项目根目录的主设置`main_config.yml`中设置管理员`wxid`。

## 实用功能⚙️

### 1.0 菜单

一个微信机器人怎么能没有菜单？XYBot的菜单功能可以让你更方便地查看所有功能。

<!-- chat:start -->

#### **HenryXiaoYang**

/菜单

#### **XYBot**

-----XYBot菜单------
实用功能⚙️
1.1 获取天气
1.2 获取新闻
1.3 ChatGPT
1.4 Hypixel玩家查询

娱乐功能🔥
2.1 随机图图
2.2 随机链接
2.3 随机群成员
2.4 五子棋

积分功能💰
3.1 签到
3.2 查询积分
3.3 积分榜
3.4 积分转送
3.5 积分抽奖
3.6 积分红包

🔧管理员功能
4.1 管理员菜单

帮助指令格式/菜单 (编号)
例如/菜单 1.1
指令参数的()不用打

#### **HenryXiaoYang**

/菜单 1.2

#### **XYBot**

-----XYBot菜单------
1.2: 获取最新头条新闻📰
指令: /新闻

<!-- chat:end -->

### 1.1 获取天气

XYBot可以帮你查询全球任意城市的天气情况。

<!-- chat:start -->

#### **HenryXiaoYang**

/天气 北京

#### **XYBot**

-----XYBot-----
北京 实时天气☁️
更新时间：2024-04-26T22:43+08:00⏰

🌡️当前温度：22℃
🌡️体感温度：23℃
☁️天气：阴
☀️紫外线指数：3
🌬️风向：东风
🌬️风力：2级
💦湿度：57%
🌧️降水量：0.0mm/h
👀能见度：7km

☁️未来3天 北京 天气：
4.27 小雨 最高🌡️23℃ 最低🌡️14℃ ☀️紫外线:8
4.28 多云 最高🌡️24℃ 最低🌡️13℃ ☀️紫外线:4
4.29 小雨 最高🌡️23℃ 最低🌡️13℃ ☀️紫外线:9

<!-- chat:end -->

### 1.2 获取新闻

XYBot可以帮你获取最新的头条新闻。

<!-- chat:start -->

#### **HenryXiaoYang**

/获取新闻

#### **XYBot**

-----XYBot新闻-----

📰 xxxx“xx”，xxxxxxxxx，xxxxxxxxx
ℹ️xxxx-xx-xx xx:xx发布于xxxx新闻官方账号 xxxxxxxxxxxxxxxxxxxxxxx......
📺xx新闻 xxxx-xx-xx xx:xx:xx
🔗https://new.xxx.com/xxxxxxxxxxxxxx

📰 xxxxxxxxxxx，xxxxxxxxxxxxxxx
ℹ️xxxx-xx-xx xx:xx发布于xxxx新闻官方账号 xxxxxxxxxxxxxxxxxxxxxxxxxxxx......
📺xx新闻 xx-xx-xx xx:xx:xx
🔗https://new.xxx.com/xxxxxxxxxxxxxx

📰 xxxxxxxxxxxx xxxx：xxxxxxx xxxxxxx
ℹ️xxxx-xx-xx xx:xx发布于xxxx官方账号 xxxxxxxxxxxxxxxxxxxxxxxxxxxx......
📺xx晨报 xxxx-xx-xx xx:xx:xx
🔗https://new.xxx.com/xxxxxxxxxxxxxx
<!-- chat:end -->

### 1.3 ChatGPT

XYBot可以调用ChatGPT，让你和机器人聊天。

?> 在设置中开启私聊ChatGPT后，可以在机器人私信直接问问题，不需要指令，还支持上下文关联！🎉

<!-- chat:start -->

#### **HenryXiaoYang**

/gpt3 用简短的语言介绍一下Github

#### **XYBot**

@HenryXiaoYang
-----XYBot-----
已收到指令，处理中，请勿重复发送指令！👍

#### **XYBot**

@HenryXiaoYang
-----XYBot-----
因为你在白名单内，所以没扣除积分！👍
ChatGPT回答：
Github是一个基于云端的代码托管平台，它允许开发者存储、管理和共享代码。它提供了一个集中的位置，使团队成员可以协同开发项目，并追踪每个人的贡献。Github还提供了版本控制功能，允许开发者轻松地管理代码的变化和修复bug。此外，Github还是一个社交平台，开发者可以在上面发现其他人的项目，参与讨论和分享经验。总的来说，Github是一个强大的工具，为开发者提供了一个优秀的协作和学习平台。

⚙️ChatGPT版本：gpt-3.5-turbo
<!-- chat:end -->

<!-- chat:start -->

#### **HenryXiaoYang**

清除对话

#### **XYBot(好友私聊)**

对话记录已清除！✅

#### **HenryXiaoYang**

后面用英文回答我

#### **XYBot(好友私聊)**

Sure, please go ahead and ask your question in English.

#### **HenryXiaoYang**

1除以3等于几

#### **XYBot(好友私聊)**

1 divided by 3 equals 0.3333 (repeating).
<!-- chat:end -->

### 1.4 Hypixel玩家查询

XYBot可以帮你查询在我的世界服务器Hypixel中玩家的信息，数据等等。

<!-- chat:start -->

#### **HenryXiaoYang**

/hypixel Technoblade

#### **XYBot**

-----XYBot-----
查询玩家 Technoblade 中，请稍候！🙂

#### **XYBot**

-----XYBot-----
🎮玩家：
[PIG+++] Technoblade [NERD]

--------

⚙️基础信息：
Multiplier: Level 296 (x8)
Level: 296.02
Karma: 151,277,505
Achievement Points: 11,450
Quests Completed: 3,057
Ranks Gifted: 0
First login:  2013-09-13 21:03 EDT

--------

🏹公会信息：
Name: technoclan
Members: 87
Rank: Guild Master
Joined: 2015/06/30 21:27:41

--------

ℹ️当前状态：
Status: Offline

#### **HenryXiaoYang**

/hypixel bw Technoblade

#### **XYBot**

-----XYBot-----
查询玩家 Technoblade 中，请稍候！🙂

#### **XYBot**

-----XYBot-----
🎮玩家：
[PIG+++] Technoblade [NERD]

--------

🛏️起床战争信息：
⚔️模式：Solo
击杀：52
死亡：28
K/D：1.86
最终击杀：47
最终死亡：5
最终K/D：9.4
胜利：12
失败：9
W/L：1.33
破坏床数：51

⚔️模式：Doubles
击杀：3,519
死亡：2,318
K/D：1.52
最终击杀：5,451
最终死亡：204
最终K/D：26.72
胜利：813
失败：213
W/L：3.82
破坏床数：2,901
...省略...
<!-- chat:end -->

## 娱乐功能🔥

### 2.1 随机图图

XYBot可以帮你随机获取一张二次元图片。

!> Wiki中图片都是固定的，不随机

<!-- chat:start -->

#### **HenryXiaoYang**

/随机图图

#### **XYBot**

![Random Picture](https://gitcode.net/qq_44112897/images/-/raw/master/comic/11.jpg)
<!-- chat:end -->

### 2.2 随机链接

XYBot可以帮你随机获取一个链接，可以说是更隐蔽的随机图图。

<!-- chat:start -->

#### **HenryXiaoYang**

/随机链接

#### **XYBot**

-----XYBot-----
❓❓❓
❓: https://gitcode.net/qq_44112897/images/-/raw/master/comic/11.jpg
❓: https://gitcode.net/qq_44112897/images/-/raw/master/comic/12.jpg
❓: https://gitcode.net/qq_44112897/images/-/raw/master/comic/13.jpg
<!-- chat:end -->

### 2.3 随机群成员

想要在群里随机抽个人？XYBot可以帮你随机获取一个群成员。

!> 本功能仅可在群聊中使用

<!-- chat:start -->

#### **HenryXiaoYang**

/随机成员

#### **XYBot**

@HenryXiaoYang
-----XYBot-----
随机群成员❓：
APerson
<!-- chat:end -->

### 2.4 五子棋

想要在群里和朋友玩五子棋？XYBot可以帮你创建并管理一场五子棋游戏。

!> 本功能仅可在群聊中使用

<!-- chat:start -->

#### **HenryXiaoYang**

/五子棋 邀请 @JoshuaZ

#### **XYBot**

@JoshuaZ
-----XYBot-----
🎉您收到了一份来自 HenryXiaoYang 的五子棋比赛邀请！

⚙️请在60秒内发送下面的指令来接受邀请：
/五子棋 接受 ABC123

#### **JoshuaZ**

/五子棋 接受 ABC123

#### **XYBot**

@JoshuaZ
-----XYBot-----
🎉五子棋游戏 ABC123 开始！

⚫️黑方：HenryXiaoYang
⚪️白方：JoshuaZ

⚫️黑方先手！

⏰每回合限时：60秒

⚙️请发送下面指令落子:
/五子棋 下棋 横坐标纵坐标

⚙️例如: /五子棋 下棋 C5

#### **XYBot**

![Gomoku Board 1](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/wiki/function_introduction/gomoku_board_1.png?raw=true)

#### **HenryXiaoYang**

/五子棋 下棋 i8

#### **XYBot**

@HenryXiaoYang
-----XYBot-----
⚫HenryXiaoYang 把棋子落在了 I8！
轮到 ⚪JoshuaZ 下子了！
⏰限时：60秒

⚙️请发送下面指令落子:
/五子棋 下棋 横坐标纵坐标

⚙️例如: /五子棋 下棋 C5

#### **XYBot**

![Gomoku Board 2](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/wiki/function_introduction/gomoku_board_2.png?raw=true)

#### **JoshuaZ**

/五子棋 下棋 I7

#### **XYBot**

@JoshuaZ
-----XYBot-----
⚪JoshuaZ 把棋子落在了 I7！
轮到 ⚫HenryXiaoYang 下子了！
⏰限时：60秒

⚙️请发送下面指令落子:
/五子棋 下棋 横坐标纵坐标

⚙️例如: /五子棋 下棋 C5

#### **XYBot**

![Gomoku Board 3](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/wiki/function_introduction/gomoku_board_3.png?raw=true)

#### **Omitted**

此处省略一些聊天

#### **HenryXiaoYang**

/五子棋 下棋 F9

#### **XYBot**

@HenryXiaoYang
-----XYBot-----
🎉五子棋游戏 ABC123 结束！🥳

⚫️黑方：HenryXiaoYang 获胜！🏆

#### **XYBot**

![Gomoku Board 4](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/wiki/function_introduction/gomoku_board_4.png?raw=true)
<!-- chat:end -->

## 积分功能💰

### 3.1 签到

在微信群中加入XYBot后，群成员可以每天签到领取积分。积分可以用来使用ChatGPT、抽奖等、发积分红包等等。

!> 默认每天签到可以领取到随机3-20积分，范围可在签到设置中修改。

<!-- chat:start -->

#### **HenryXiaoYang**

/签到

#### **XYBot**

@HenryXiaoYang
-----XYBot-----
签到成功！你领到了20个积分！✅

#### **JoshuaZ**

/签到

#### **XYBot**

@JoshuaZ
-----XYBot-----
签到成功！你领到了3个积分！✅
<!-- chat:end -->

### 3.2 查询积分

有了积分系统，怎么能没有查询自己积分的功能呢？

<!-- chat:start -->

#### **HenryXiaoYang**

/查询积分

#### **XYBot**

@HenryXiaoYang
-----XYBot-----
你有67点积分！👍
<!-- chat:end -->

### 3.3 积分榜

想要看看谁的积分最多？使用XYBot可以查看积分榜。

<!-- chat:start -->

#### **HenryXiaoYang**

/积分榜

#### **XYBot**

-----XYBot积分排行榜-----

1. xxxxxxx 7956分 👍
2. xxxx 5773分 👍
3. xxxxxx 4886分 👍
4. xxx 3840分 👍
5. xxxxx xxx 2899分 👍
6. xxxxx 2608分 👍
7. xxx 2595分 👍
8. xxxxxxxxxx 2291分 👍
9. xxxx 2043分 👍
10. xx 1992分 👍
11. xxxxx 1968分 👍
12. xxxxx 1913分 👍
13. xxxxx xx 1897分 👍
14. xxxxxxxxx 1896分 👍
15. xxxxxxxx 1889分 👍
16. xxx 1879分 👍
17. xxxxx 1767分 👍
18. xxx 1757分 👍
19. xxxx xxxxxxx xx xxxxxxx 1734分 👍
20. xxxxx 1679分 👍
21. xxxx 1650分 👍
22. x 1587分 👍
23. xxxx 1441分 👍
24. xxx 1430分 👍
25. xx 1352分 👍
26. xxxxx 1330分 👍
27. xxxxxxx 1327分 👍
28. xxxxxxx 1224分 👍
29. xx 1219分 👍
30. xxxxxxxx x 1202分 👍

<!-- chat:end -->

### 3.4 积分转送

一个积分体系怎么能没有交易系统？XYBot的积分转送功能可以让你把你的积分转给其他人。

<!-- chat:start -->

#### **HenryXiaoYang**

/转送积分 20 @JoshuaZ

#### **XYBot**

@HenryXiaoYang
-----XYBot-----
转帐成功✅! 你现在有66点积分 JoshuaZ现在有26点积分

#### **JoshuaZ**

/查询积分

#### **XYBot**

@JoshuaZ
-----XYBot-----
你有26点积分！👍
<!-- chat:end -->

### 3.5 积分抽奖

XYBot的积分抽奖功能可以让你用积分参与抽奖，赢取更多积分。

?> 抽奖的奖品和概率可以在抽奖设置中修改。

<!-- chat:start -->

#### **HenryXiaoYang**

/抽奖 小

#### **XYBot**

@HenryXiaoYang
----XYBot抽奖----
🥳恭喜你在 1次 小抽奖 中抽到了：

🟩
绿
🟩

🎉总计赢取积分: 15🎉
🎉共计消耗积分：20🎉

概率请自行查询菜单⚙️

#### **HenryXiaoYang**

/抽奖 中 5

#### **XYBot**

@HenryXiaoYang
----XYBot抽奖----
🥳恭喜你在 5次 中抽奖 中抽到了：

🟪🟩🟪🟩🟦
紫绿紫绿蓝
🟪🟩🟪🟩🟦

🎉总计赢取积分: 221🎉
🎉共计消耗积分：200🎉

概率请自行查询菜单⚙️
<!-- chat:end -->

### 3.6 积分红包

想发红包但没钱？XYBot的积分红包功能可以让你用积分发红包给群里的其他人。

?> 红包的最高金额和最多数量可以在红包设置中修改。

<!-- chat:start -->

#### **HenryXiaoYang**

/发红包 15 2

#### **XYBot**

-----XYBot-----
HenryXiaoYang 发送了一个红包！

🧧红包金额：15点积分
🧧红包数量：2个

🧧红包口令请见下图！

快输入指令来抢红包！/抢红包 (口令)

#### **XYBot**

![Red Packet Code](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/wiki/function_introduction/red_packet_1.jpg?raw=true)

#### **JoshuaZ**

/抢红包 9bvx2

#### **XYBot**

@JoshuaZ
-----XYBot-----
❌口令错误或无效！

#### **JoshuaZ**

/抢红包 qbvx2

#### **XYBot**

@JoshuaZ
-----XYBot-----
🧧恭喜 JoshuaZ 抢到了 4 点积分！
<!-- chat:end -->

## 管理员功能🔧

大部分管理员功能需要管理员权限，可以在位于项目根目录的主设置`main_config.yml`中设置管理员`wxid`。

!> `wxid`不是微信号！`wxid`是一个在微信内部使用的ID，用于识别用户。`wxid`一般以 `wxid_` 开头，例如 `wxid_0123456789abc`
，但是也有例外情况：一些老的微信账号的`wxid`不一定是以`wxid_`开头，可能是自定义的。

### 检查机器人状态

!> 本功能不是管理员也可以用

<!-- chat:start -->

#### **HenryXiaoYang**

/机器人状态

#### **XYBot**

-----XYBot-----
Bot Running😊
Bot version: v0.0.6
Github: https://github.com/HenryXiaoYang/XYBot

#### **JoshuaZ**

/机器人状态

#### **XYBot**

Bot Running😊
Bot version: v0.0.6
Github: https://github.com/HenryXiaoYang/XYBot
<!-- chat:end -->

### 获取群成员列表

!> 本功能仅管理员可用

?> 管理员功能广泛使用`wxid`来识别用户，可以用这个功能查询到群成员的`wxid`。

<!-- chat:start -->

#### **HenryXiaoYang**

/获取群成员列表

#### **XYBot**

-----XYBot-----
🤖️本群聊的群员列表：
https://easychuan.cn/r/xxxxx
过期时间：xxxx-xx-xxTxx:xx:xx.xxxx
<!-- chat:end -->

由于`pywxdll`库的发送文件功能疑似被微信官方封禁，没法发Excel表格，所以机器人将表格上传至了一个在线文本传输网站，可以访问该网站获得到表格。

![Get Chatroom Member Example](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/wiki/function_introduction/get_chatroom_member_1.png?raw=true)

### 获取机器人通讯录

!> 本功能仅管理员可用

与获取群成员列表一样，可以用这个功能查询到用户的`wxid`

<!-- chat:start -->

#### **HenryXiaoYang**

/获取机器人通讯录

#### **XYBot**

-----XYBot-----
🤖️机器人的通讯录：
https://easychuan.cn/r/xxxxx
过期时间：xxxx-xx-xxTxx:xx:xx.xxxx
<!-- chat:end -->

### 管理积分

!> 本功能仅管理员可用

管理员可以通过这个修改用户的积分。

<!-- chat:start -->

#### **HenryXiaoYang**

/管理积分 wxid_0123456789abcde 加 10

#### **XYBot**

-----XYBot-----
😊成功给wxid_0123456789abcde加了10点积分！他现在有15点积分！

#### **HenryXiaoYang**

/管理积分 wxid_0123456789abcde 减 10

#### **XYBot**

-----XYBot-----
😊成功给wxid_0123456789abcde减了10点积分！他现在有5点积分！

#### **HenryXiaoYang**

/管理积分 wxid_0123456789abcde 10

#### **XYBot**

-----XYBot-----
😊成功将wxid_0123456789abcde的积分设置为10！
<!-- chat:end -->

### 管理白名单

!> 本功能仅管理员可用

管理员可以通过这个功能管理白名单，有白名单者使用ChatGPT功能不扣积分。

<!-- chat:start -->

#### **HenryXiaoYang**

/管理白名单 wxid_0123456789abcde 加入

#### **XYBot**

-----XYBot-----
成功修改wxid_0123456789abcde的白名单！😊

#### **HenryXiaoYang**

/管理白名单 wxid_0123456789abcde 删除

#### **XYBot**

-----XYBot-----
成功修改wxid_0123456789abcde的白名单！😊
<!-- chat:end -->

### 查看已加载插件列表

!> 本功能仅管理员可用

管理员可以通过这个功能查看已加载的插件列表。

<!-- chat:start -->

#### **HenryXiaoYang**

/管理插件 列表

#### **XYBot**

-----XYBot-----
已加载插件列表：
admin_signin_reset
points_trade
random_group_member
manage_plugins
bot_status
hypixel_info
red_packet
weather
sign_in
get_chatroom_memberlist
query_points
gpt4
get_contact_list
admin_points
random_picture
lucky_draw
random_picture_link
admin_whitelist
points_leaderboard
gpt
menu
news
gomoku
<!-- chat:end -->

### 热加载/卸载/重载插件

!> 本功能仅管理员可用

管理员可以通过这个功能在不重启机器人的情况下加载，重载，卸载插件。

<!-- chat:start -->

#### **HenryXiaoYang**

/管理插件 卸载 lucky_draw

#### **XYBot**

-----XYBot-----
卸载插件lucky_draw成功！✅

#### **HenryXiaoYang**

/管理插件 加载 lucky_draw

#### **XYBot**

-----XYBot-----
加载插件lucky_draw成功！✅

#### **HenryXiaoYang**

/管理插件 重载 lucky_draw

#### **XYBot**

-----XYBot-----
重载插件lucky_draw成功！✅
<!-- chat:end -->

### 重置签到冷却

!> 本功能仅管理员可用

机器人出错而崩溃了，导致群友没签到而闹事？管理员可以通过这个功能重置签到冷却时间。

<!-- chat:start -->

#### **HenryXiaoYang**

/重置签到冷却

#### **XYBot**

-----XYBot-----
😊成功重置签到状态！
<!-- chat:end -->


