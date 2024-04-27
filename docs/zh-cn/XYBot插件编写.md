# XYBot插件编写

这一页讲述了如何编写一个XYBot插件

本篇适用于`XYBot v0.0.6`。

## 插件模板

[🔗插件模版仓库](https://github.com/HenryXiaoYang/XYBot-Plugin-Framework)

## 编写你的第一个XYBot插件

一个XYBot插件由2个文件组成：

- 一个`.py`结尾的Python脚本文件
- 一个`.yml`结尾的配置文件

我们将编写一个名为`hello_world`的插件。当用户输入`/hello`，XYBot会回复`world!`。

### Python脚本文件

这是从`XYBot-Plugin-Framework`仓库中的`plugins/my_plugin.py`文件中复制的插件脚本模板：

```python
# my_plugin.py
import pywxdll
import yaml
from loguru import logger

from plugin_interface import PluginInterface


# 这里的类名得与插件设置文件中 plugin_name 一样。建议也与文件名一样
class my_plugin(PluginInterface):
    def __init__(self):
        config_path = 'plugins/my_plugin.yml'
        with open(config_path, 'r', encoding='utf-8') as f:  # 读取插件设置
            config = yaml.safe_load(f.read())

        # 这里从.yml文件中读取设置
        self.plugin_setting = config['plugin_setting']

        # 这里从主设置中读取微信机器人api的ip地址、端口，并启动
        main_config_path = 'main_config.yml'  # 主设置文件路径
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.safe_load(f.read())  # 读取设置

        self.ip = main_config['ip']  # ip
        self.port = main_config['port']  # 端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    async def run(self, recv):  # 当用户指令与插件设置中关键词相同，执行对应插件的run函数
        out_message = 'hello,world! \n plugin_setting:{plugin_setting}'.format(
            plugin_setting=self.plugin_setting)  # 组建消息
        logger.info('[发送信息]{out_message}| [发送到] {wxid}'.format(out_message=out_message, wxid=recv['wxid']))
        self.bot.send_txt_msg(recv['wxid'],
                              out_message)  # 发送消息，更多微信机器人api函数请看 https://github.com/HenryXiaoYang/pywxdll 中的文档
```

由于XYBot加载插件时，是用设置中的类名实例化插件的，所以我们将这个文件保存为`hello_world.py`
，并在这里第9行的类名需要改成`hello_world`。

对于这个简单的插件，我们不需要从设置中读取任何设置，所以我们可以删除第11-16行用于读取插件设置的代码。我们还是得保留第18-25行的代码，因为我们需要读取主设置中机器人ip与端口，并实例化`pywxdll`
提供的类。

我们先删除第28-32行的代码，后面重新编写。

当这个`hello_world`插件的`run`函数被调用时，我们需要向用户发送`world!`。我们可以使用`self.bot.send_txt_msg`
函数来发送消息。这个函数需要两个参数：`wxid`与`message`。`wxid`是用户的`wxid`，`message`是要发送的消息。

!> `wxid`不是微信号！`wxid`是一个在微信内部使用的ID，用于识别用户。`wxid`一般以 `wxid_` 开头，例如 `wxid_0123456789abc`
，但是也有例外情况：一些老的微信账号的`wxid`不一定是以`wxid_`开头，可能是自定义的。

我们已经知道要发什么了（`world!`)，但是我们不知道要发给谁。

从`run`函数的`recv`参数中，我们可以获取到用户的`wxid`。`recv`
是一个字典，包含了用户的消息的所有信息。我们可以通过`recv['wxid']`来获取调用指令的用户的`wxid`。

所以我们可以将`run`函数改为：

```python
async def run(self, recv):  # 当用户指令与插件设置中关键词相同，执行对应插件的run函数
    wxid = recv['wxid']
```

好的，我们现在知道要发给谁了。现在就可以发送消息了！

```python
async def run(self, recv):  # 当用户指令与插件设置中关键词相同，执行对应插件的run函数
    wxid = recv['wxid']
    self.bot.send_txt_msg(wxid, 'world!')  # 发送消息
```

最后的代码是：

```python
# hello_world.py
import pywxdll
import yaml
from loguru import logger

from plugin_interface import PluginInterface


# 这里的类名得与插件设置文件中 plugin_name 一样。建议也与文件名一样
class hello_world(PluginInterface):
    def __init__(self):
        # 这里从主设置中读取微信机器人api的ip地址、端口，并启动
        main_config_path = 'main_config.yml'  # 主设置文件路径
        with open(main_config_path, 'r', encoding='utf-8') as f:  # 读取设置
            main_config = yaml.safe_load(f.read())  # 读取设置

        self.ip = main_config['ip']  # ip
        self.port = main_config['port']  # 端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api


async def run(self, recv):  # 当用户指令与插件设置中关键词相同，执行对应插件的run函数
    wxid = recv['wxid']
    self.bot.send_txt_msg(wxid, 'world!')  # 发送消息
```

请注意，一个插件由两个文件组成，我们还需要一个配置文件。

### 配置文件

这是从`XYBot-Plugin-Framework`仓库中的`plugins/my_plugin.yml`文件中复制的一个插件设置模板：

```yaml
# my_plugin.yml
keywords: [ "我的插件","myplugin" ] # 指令关键词 /我的插件 和 /myplugin 都会运行插件 my_plugin
plugin_name: "my_plugin" # 插件名

plugin_setting: "This is my setting!" # 插件设置，在my_plugin.py被读取
```

养成好习惯，为了后面维护方便，我们将这个文件保存为`hello_world.yml`。

首先我们把第2行的`my_plugin`改成`hello_world`，因为我们的插件名是`hello_world`，*
*XYBot加载插件时是从这里获得到类名的，所以设置中的`plugin_name`必须与Python脚本文件中的类名保持一致！**

?> 这样写加载插件的原因是考虑到一个脚本文件可以有多个设置文件

对于这个插件，我们不需要`plugin_setting`，所以我们可以删除第4行。

将第一行的`keywords`改为`[ "hello" ]`。这样用户在微信输入`/hello`时，XYBot就会运行Python脚本中的`run`函数。

最后的配置文件是：

```yaml
# hello_world.yml
keywords: [ "hello" ]
plugin_name: "hello_world" # 插件名
```

### 将插件添加到XYBot

将`hello_world.py`与`hello_world.yml`文件放到`plugins`目录下。

### 热加载插件

!> 这里微信账号需要是XYBot管理员，没有的话只能重启XYBot了

在微信向XYBot发送`/管理插件 加载 hello_world`，XYBot就会加载`hello_world`插件。

<!-- chat:start -->

#### **HenryXiaoYang**

/管理插件 加载 hello_world

#### **XYBot**

-----XYBot-----
加载插件hello_world成功！✅
<!-- chat:end -->

### 测试插件

现在，当你在微信中输入`/hello`，XYBot会回复`world!`。

<!-- chat:start -->

#### **HenryXiaoYang**

/hello

#### **XYBot**

world!
<!-- chat:end -->

## 进阶

这只是一个简单的插件，你可以在这个基础上添加更多功能。

更多微信机器人api函数请看[🔗文档](https://henryxiaoyang.github.io/pywxdll)。

更多机器人插件例子可在[🔗这里](https://github.com/HenryXiaoYang/XYBot/tree/main/plugins)看到。
