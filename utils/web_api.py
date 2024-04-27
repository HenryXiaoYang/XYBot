#  Copyright (c) 2024. Henry Yang
#
#  This program is licensed under the GNU General Public License v3.0.

from fastapi import FastAPI

from utils.web_api_data import WebApiData

app = FastAPI()
web_api_data = WebApiData()


@app.get("/api/received_message_count")
def recieved_message_count():
    return {"count": web_api_data.get_data()['received_message_count']}


@app.get("/api/sent_message_count")
def sent_message_count():
    return {"count": web_api_data.get_data()['sent_message_count']}


@app.get("/api/user_count")
def user_count():
    return {"count": web_api_data.get_data()['user_count']}


@app.get("/api/running_days")
def running_days():
    return {"days": web_api_data.get_data()['running_days']}


@app.get("/api/")
def api_root():
    return web_api_data.get_data()
