# # XYBot Windows部署

这一页写了在Windows上部署XYBot的方法。

本篇部署教程适用于`XYBot v0.0.7`。

## 前言

相比于在Linux上部署`XYBot`，在Windows上部署`XYBot`简单很多。

配置要求：

- 64位
- 能运行PC版微信

## 部署

### 1. 安装Python环境

请安装Python3.8.10 **64位版本**：[🔗链接](https://www.python.org/downloads/release/python-3810/)

装好了可跳过

如果不知道如何安装请查阅：[Python官方文档](https://docs.python.org/3.9/using/windows.html)

看不懂英文的话网上也有很多中文教程

!> 请注意安装`Python`时将`Add Python 3.9 to PATH`环境变量选项勾选上。

### 2. 安装Git

装好了可跳过

官网下载地址：[🔗链接](https://git-scm.com/download/win)

看不懂英文的话网上也有很多中文教程

### 3. 下载并安装PC版微信v3.9.5.81

下载地址：[🔗链接](https://github.com/tom-snow/wechat-windows-versions/releases?q=3.9.5.81)

正常安装微信即可。

### 4. 从Github克隆XYBot项目

按win + r，输入cmd，然后回车打开cmd。

用`cd`切换到合适的目录，比如桌面：

```commandline
cd Desktop
```

然后`git clone`将`XYBot`从Github克隆下来

```commandline
git clone https://github.com/HenryXiaoYang/XYBot.git
```

### 5. 下载XYBot所需要的依赖

切换到`XYBot`的目录

```commandline
cd XYBot
```

然后用`pip`安装依赖

```commandline
pip install -r requirements.txt
```

在国内太慢的话看眼选择用镜像源。

```commandline
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 6. 运行XYBot

在命令行运行`XYBot`。

```commandline
python start.py
```

!> 如果遇到下图的错误，请检查`pywxdll/StartWxAndInject_Windows.exe`这个文件是否被安全软件误删（如Windows安全就会把这个文件误删）。

![StartWxAndInject_Windows.exe Deleted By Safety Software](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/v0.0.7/wiki/windows_deployment/Deleted_By_Safe_Soft_StartWxAndInject.png?raw=true)

### 7. 登陆微信

微信应自动启动，扫描二维码登陆账号。

### 8. 测试XYBot

注入XYBot后，XYBot应该会自动启动。

在微信中向XYBot私聊`菜单`，如果返回菜单则部署成功。

<!-- chat:start -->

#### **HenryXiaoYang**

菜单

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

获取菜单指令格式: 菜单 编号

例如：菜单 1.1
<!-- chat:end -->

可以开始用XYBot了！

如果失败，可以看看命令行日志。解决不了的话可以开`issue`询问。

