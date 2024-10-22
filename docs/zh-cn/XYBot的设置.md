# XYBot的设置

这一页写了如何设置XYBot。

本篇适用于`XYBot v2.0.0`。

## 配置主设置

这是`XYBot v2.0.0`的主设置：

```yaml
#Version v2.0.0
bot_version: "v2.0.0"

# XYBot主设置

#如果不知道自己在干什么请别动这两行
ip: 127.0.0.1
port: 5555

admins: [ ]

command_prefix: "" #如果需要前缀，则必须为一个字符。如果不需要前缀可设置为空，即 ""。

excluded_plugins: [ "" ]

timezone: "Asia/Shanghai"

# ------------------------------------------------------------------------------ #

# 白名单/黑名单设置
mode: "none" # 可以是 黑名单blacklist 白名单whitelist 无none

# 请填入群号或者wxid
blacklist: [ ]
whitelist: [ ]

# ------------------------------------------------------------------------------ #
# 全局chatgpt设置，插件使用到，私聊gpt也使用到

#ChatGPT的API网址
openai_api_base: ""
#ChatGPT API的Key
openai_api_key: ""
```

- `bot_version`是机器人版本号
- `ip` `port` `tcp_server_port` 分别是机器人Hook API的IP地址、端口和接收Hook消息的TCP Server的端口。
- `admins`为管理员的`wxid`，管理员可以有多个，每个管理员的`wxid`用逗号分割。
- `command_prefix`为机器人指令前缀。一般是一个字符，如果不需要前缀可设置为空，即 `""`。
- `excluded_plugins`为你不想启用的插件，可填入插件名。
- `timezone`为机器人所使用的时区，可以查看[时区列表](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)。

- `mode`设置了机器人的白名单或者黑名单。可填入`blacklist`或`whitelist`。
- `blacklist`使用黑名单时，可填入`wxid`或者群ID。
- `whitelist`使用白名单时，可填入`wxid`或者群ID。

- `openai_api_base` OpenAI的API密钥。
- `openai_api_base` OpenAI的API网址。

## 配置插件设置

这里将用`gpt`插件为例，`gpt`插件的配置文件如下：

```yaml
keywords: [ "gpt","GPT","ChatGPT","chatgpt","CHATGPT"]
plugin_name: "gpt"

gpt_point_price: 3

gpt_version: 'gpt-3.5-turbo'
gpt_max_token: 1000
gpt_temperature: 0.5
```

- `keywords`是插件的关键词，当用户发送的指令第一项是任何一个关键词时，机器人会执行插件。
- `plugin_name`**这个千万不要改，程序中是用的这个来实例化插件类的**。
- `gpt_point_price`是ChatGPT插件的对话消耗积分，如果需要变更对话消耗积分，需要在`gpt_point_price`中修改积分数。
- 后面的三个参数是ChatGPT请求模型设置，如果需要变更ChatGPT请求模型设置，需要在`gpt_version`、`gpt_max_token`
  和`gpt_temperature`中修改参数。

再用`weather`插件为例，`weather`插件的配置文件如下：

```yaml
keywords: [ "天气", "获取天气" ]
plugin_name: "weather"

weather_api_key: ""

# 老api改收费了 新的api需要申请，链接：https://dev.qweather.com/
# 项目订阅选免费订阅即可，把获得到的Key (不是Public ID 而是Private KEY) 填到上面引号中
```

实时天气这种插件比较特殊，需要申请一个API Key。一般需要API Key的插件都会写注释说明如何获得到API Key。对于`weather`
插件，需要前往`https://dev.qweather.com/` 申请API Key，然后将获得到的密钥填入`weather_api_key`中。