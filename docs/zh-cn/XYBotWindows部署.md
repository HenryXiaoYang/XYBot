# # XYBot Windows部署

这一页写了在Windows上部署XYBot的方法。

本篇部署教程适用于`XYBot v0.0.6`。

## 前言

相比于在Linux上部署`XYBot`，在Windows上部署`XYBot`简单很多。

配置要求：

能运行PC版微信就行。

## 部署

### 1. 安装Python环境

装好了可跳过

请安装Python3.9：[🔗链接](https://www.python.org/downloads/release/python-3913/)

如果不知道如何安装请查阅：[Python官方文档](https://docs.python.org/3.9/using/windows.html)

看不懂英文的话网上也有很多中文教程

!> 请注意安装`Python`时将`Add Python 3.9 to PATH`环境变量选项勾选上。

### 2. 安装Git

装好了可跳过

官网下载地址：[🔗链接](https://git-scm.com/download/win)

看不懂英文的话网上也有很多中文教程

### 3. 下载并安装PC版微信v3.6.0.18

下载地址：[🔗链接](https://github.com/tom-snow/wechat-windows-versions/releases?q=3.6.0.18)

正常安装微信即可。

### 4. 下载微信DLL注入器，DLL文件，微信低版本提示修复程序

微信DLL注入器：[🔗链接](https://github.com/HenryXiaoYang/XYBot/releases/download/v0.0.6/Wechat-DLL-injector.V1.0.3.exe)

DLL文件：[🔗链接](https://github.com/HenryXiaoYang/XYBot/releases/download/v0.0.6/wechat-bot-dll-for-XYBot.dll)

微信低版本提示修复：[🔗链接](https://github.com/HenryXiaoYang/XYBot/releases/download/v0.0.6/wechat_launcher_bypass_ver_check.exe)

!> 微信低版本提示修复是用易语言编写的，报毒很正常。请放心使用！

### 5. 下载XYBot

按win + r，输入cmd，然后回车打开cmd。

用`cd`切换到合适的目录，比如桌面：

```commandline
cd Desktop
```

然后`git clone`将`XYBot`从Github克隆下来

```commandline
git clone https://github.com/HenryXiaoYang/XYBot.git
```

### 6. 下载XYBot所需要的依赖

切换到`XYBot`的目录

```commandline
cd XYBot
```

然后用`pip`安装依赖

```commandline
pip install -r requirements.txt
```

在内陆太慢的话看眼选择用镜像源。

```commandline
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 7. 运行XYBot

在命令行运行`XYBot`。

```commandline
python start.py
```

### 8. 登陆微信

运行下载的微信低版本提示修复`wechat_launcher_bypass_ver_check.exe`，会弹出一个窗口。

![Wechat Bypass Version Check](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/wiki/xybot_windows_deployment/bypass_ver_check_1.png?raw=true)

如图，请将`原版本号`修改为`3.6.0.18`，然后点击右边的`微信低版本通杀`，即可运行微信。

微信打开后，扫码登陆。

### 9. 注入DLL

微信登陆后，打开微信DLL注入器，选择`wechat-bot-dll-for-XYBot.dll`，然后点击`注入DLL`。

![DLL Injector Screenshot](https://github.com/HenryXiaoYang/HXY_Readme_Images/blob/main/XYBot/wiki/xybot_windows_deployment/dll_injector_1.png?raw=true)

### 10. 测试XYBot

注入XYBot后，XYBot应该会自动启动。

在微信中向XYBot私聊`/菜单`，如果返回菜单则部署成功。

可以开始用XYBot了！

如果失败，可以看看命令行日志。解决不了的话可以开`issue`询问。

