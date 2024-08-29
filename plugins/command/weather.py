#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

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

        self.weather_api_key = config["weather_api_key"]

        main_config_path = "main_config.yml"
        with open(main_config_path, "r", encoding="utf-8") as f:  # 读取设置
            main_config = yaml.safe_load(f.read())

        self.ip = main_config["ip"]  # 机器人ip
        self.port = main_config["port"]  # 机器人端口
        self.bot = pywxdll.Pywxdll(self.ip, self.port)  # 机器人api

    async def run(self, recv):
        error = ''
        if len(recv['content']) != 2:
            error = '指令格式错误！'

        if not error:
            # 首先请求geoapi，查询城市的id
            request_city = recv['content'][1]
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
                self.send_friend_or_group(recv, out_message)

            elif geoapi_json['code'] == '404':
                error = '-----XYBot-----\n⚠️城市不存在！'
                self.send_friend_or_group(recv, error)
            else:
                error = f'-----XYBot-----\n⚠️请求失败！\n{geoapi_json}'
                self.send_friend_or_group(recv, error)


        else:
            self.send_friend_or_group(recv, error)

    def send_friend_or_group(self, recv, out_message="null"):
        if recv["fromType"] == "chatroom":  # 判断是群还是私聊
            logger.info(f'[发送@信息]{out_message}| [发送到] {recv["from"]}')
            self.bot.send_at_msg(recv["from"], "\n" + out_message, [recv["sender"]])

        else:
            logger.info(f'[发送信息]{out_message}| [发送到] {recv["from"]}')
            self.bot.send_text_msg(recv["from"], out_message)  # 发送

    def compose_weather_message(self, city_name, now_weather_api_json, weather_forecast_api_json):
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
