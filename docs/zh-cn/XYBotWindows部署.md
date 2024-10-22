# XYBot Windows部署

这一页写了在Windows上部署XYBot的方法。

本篇部署教程适用于`XYBot v2.0.0`。

## 前言

相比于在Linux上部署`XYBot`，在Windows上部署`XYBot`简单很多。

配置要求：

- 64位
- 能运行PC版微信

## 部署

### 1. 安装Python环境

请安装`Python3.12`：[🔗链接](https://www.python.org/downloads/release/python-3127/)

装好了可跳过

如果不知道如何安装请查阅：[Python官方文档](https://docs.python.org/3.9/using/windows.html)

看不懂英文的话网上也有很多中文教程

!> 请注意安装`Python`时将`Add Python 3.12 to PATH`环境变量选项勾选上。

### 2. 安装Git

装好了可跳过

官网下载地址：[🔗链接](https://git-scm.com/download/win)

看不懂英文的话网上也有很多中文教程

### 3. 下载并安装PC版微信v3.9.10.27

下载地址：[🔗链接](https://github.com/tom-snow/wechat-windows-versions/releases/tag/v3.9.10.27)

正常安装微信即可。

### 4. 从Github克隆XYBot项目

`git clone`将`XYBot`从Github克隆下来

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
### 6. 启动微信

请手动启动微信。

### 7. 运行XYBot

在命令行运行`XYBot`。

```commandline
python start.py
```

### 8. 登陆微信

当终端里有提示让你登陆微信时，请在微信中扫描二维码登陆。

### 9. 测试是否部署成功

可以开始用XYBot了！

如果失败，可以看看命令行日志。解决不了的话可以开`issue`询问。

