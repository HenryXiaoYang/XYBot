#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

import aiohttp
import yaml
from loguru import logger
from wcferry import client

from utils.database import BotDatabase
from utils.plugin_interface import PluginInterface
from wcferry_helper import XYBotWxMsg


class weather(PluginInterface):
    def __init__(self):
        config_path = "plugins/command/weather.yml"
        with open(config_path, "r", encoding="utf-8") as f:  # 读取设置
            config = yaml.safe_load(f.read())

        self.weather_api_key = config["weather_api_key"]

        self.db = BotDatabase()

    async def run(self, bot: client.Wcf, recv: XYBotWxMsg):
        recv.content = recv.content.split(" |\u2005")  # 拆分消息

        error = ''
        if len(recv.content) != 2:
            error = '指令格式错误！'

        if not error:
            # 首先请求geoapi，查询城市的id
            request_city = recv.content[1]
            geo_api_url = f'https://geoapi.qweather.com/v2/city/lookup?key={self.weather_api_key}&number=1&location={request_city}'

            conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
            async with aiohttp.request('GET', url=geo_api_url, connector=conn_ssl) as response:
                geoapi_json = await response.json()
                await conn_ssl.close()

            if geoapi_json['code'] == '200':  # 如果城市存在
                request_city_id = geoapi_json['location'][0]['id']
                request_city_name = geoapi_json['location'][0]['name']

                # 请求现在天气api
                conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
                now_weather_api_url = f'https://devapi.qweather.com/v7/weather/now?key={self.weather_api_key}&location={request_city_id}'
                async with aiohttp.request('GET', url=now_weather_api_url, connector=conn_ssl) as response:
                    now_weather_api_json = await response.json()
                    await conn_ssl.close()

                # 请求预报天气api
                conn_ssl = aiohttp.TCPConnector(verify_ssl=False)
                weather_forecast_api_url = f'https://devapi.qweather.com/v7/weather/7d?key={self.weather_api_key}&location={request_city_id}'
                async with aiohttp.request('GET', url=weather_forecast_api_url, connector=conn_ssl) as response:
                    weather_forecast_api_json = await response.json()
                    await conn_ssl.close()

                out_message = self.compose_weather_message(request_city_name, now_weather_api_json,
                                                           weather_forecast_api_json)
                await self.send_friend_or_group(bot, recv, out_message)

            elif geoapi_json['code'] == '404':
                error = '-----XYBot-----\n⚠️城市不存在！'
                await self.send_friend_or_group(bot, recv, error)
            else:
                error = f'-----XYBot-----\n⚠️请求失败！\n{geoapi_json}'
                await self.send_friend_or_group(bot, recv, error)


        else:
            await self.send_friend_or_group(bot, recv, error)

    async def send_friend_or_group(self, bot: client.Wcf, recv: XYBotWxMsg, out_message="null"):
        if recv.from_group():  # 判断是群还是私聊
            out_message = f"@{self.db.get_nickname(recv.sender)}\n{out_message}"
            logger.info(f'[发送@信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid, recv.sender)  # 发送@信息
        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv.roomid}')
            bot.send_text(out_message, recv.roomid)  # 发送

    @staticmethod
    def compose_weather_message(city_name, now_weather_api_json, weather_forecast_api_json):
        update_time = now_weather_api_json['updateTime']
        now_temperature = now_weather_api_json['now']['temp']
        now_feelslike = now_weather_api_json['now']['feelsLike']
        now_weather = now_weather_api_json['now']['text']
        now_wind_direction = now_weather_api_json['now']['windDir']
        now_wind_scale = now_weather_api_json['now']['windScale']
        now_humidity = now_weather_api_json['now']['humidity']
        now_precip = now_weather_api_json['now']['precip']
        now_visibility = now_weather_api_json['now']['vis']
        now_uvindex = weather_forecast_api_json['daily'][0]['uvIndex']

        message = f'-----XYBot-----\n{city_name} 实时天气☁️\n更新时间：{update_time}⏰\n\n🌡️当前温度：{now_temperature}℃\n🌡️体感温度：{now_feelslike}℃\n☁️天气：{now_weather}\n☀️紫外线指数：{now_uvindex}\n🌬️风向：{now_wind_direction}\n🌬️风力：{now_wind_scale}级\n💦湿度：{now_humidity}%\n🌧️降水量：{now_precip}mm/h\n👀能见度：{now_visibility}km\n\n☁️未来3天 {city_name} 天气：\n'
        for day in weather_forecast_api_json['daily'][1:4]:
            date = '.'.join([i.lstrip('0') for i in day['fxDate'].split('-')[1:]])
            weather = day['textDay']
            max_temp = day['tempMax']
            min_temp = day['tempMin']
            uv_index = day['uvIndex']
            message += f'{date} {weather} 最高🌡️{max_temp}℃ 最低🌡️{min_temp}℃ ☀️紫外线:{uv_index}\n'

        return message
