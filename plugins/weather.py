import aiohttp
import yaml
from loguru import logger

import pywxdll
from utils.plugin_interface import PluginInterface


class weather(PluginInterface):
    def __init__(self):
        config_path = "plugins/weather.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.weather_api = config["weather_api"]
        self.weather_appid = config["weather_appid"]
        self.weather_appsecret = config["weather_appsecret"]

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    async def run(self, recv):
        if len(recv["content"]) == 2:
            city = recv["content"][1]  # 获取要查询的天气
            url = f"{self.weather_api}?appid={self.weather_appid}&appsecret={self.weather_appsecret}&unescape=1&city={city}"  # 从设置中获取链接，密钥，并构成url
            try:

                conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
                async with aiohttp.request("GET", url=url, connector=conn_ssl) as req:
                    res = await req.json()

                if "city" in res.keys():
                    out_message = f"-----XYBot-----\n城市🌆：{res['city']}\n天气☁️：{res['wea']}\n实时温度🌡️：{res['tem']}°\n白天温度🌡：{res['tem_day']}°\n夜晚温度🌡：{res['tem_night']}°\n空气质量🌬：{res['air']}\n空气湿度💦：{res['humidity']}\n风向🌬：{res['win_speed']}{res['win']}\n更新时间⌚：{res['update_time']}"  # 创建信息
                    logger.info(f"[发送信息]{out_message}| [发送到] {recv['wxid']}")
                    self.bot.send_txt_msg(recv["wxid"], out_message)

                else:
                    out_message = f"-----XYBot-----\n未知的城市：{city}❌"
                    logger.info(f"[发送信息]{out_message}| [发送到] {recv['wxid']}")
                    self.bot.send_txt_msg(recv["wxid"], out_message)

            except KeyError as error:
                error_args = error.args[0]
                if error_args == "city":
                    out_message = (
                        f"-----XYBot-----\n未知的城市⚠️:{error_args}\n(仅支持国内城市！)"
                    )
                    logger.info(f"[发送信息]{out_message}| [发送到] {recv['wxid']}")
                    self.bot.send_txt_msg(recv["wxid"], out_message)

                else:
                    out_message = f"-----XYBot-----\n出现错误！⚠️{error}"
                    logger.info(f"[发送信息]{out_message}| [发送到] {recv['wxid']}")
                    self.bot.send_txt_msg(recv["wxid"], out_message)


            except Exception as error:  # 报错处理
                out_message = f"-----XYBot-----\n出现错误！⚠️{error}"
                logger.info(f'[发送信息]{out_message}| [发送到] {recv["wxid"]}')
                self.bot.send_txt_msg(recv["wxid"], out_message)

        else:
            out_message = "-----XYBot-----\n参数错误！⚠️"
            logger.info(f"[发送信息]{out_message}| [发送到] {recv['wxid']}")
            self.bot.send_txt_msg(recv["wxid"], out_message)
