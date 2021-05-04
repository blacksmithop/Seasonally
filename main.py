from pytz import country_timezones, timezone
from aiohttp import ClientSession
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from os import getenv
from fastapi.templating import Jinja2Templates


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

API_KEY = getenv('API_KEY')

weekdays = {
    0: "Sun",
    1: "Mon",
    2: "Tue",
    3: "Wed",
    4: "Thurs",
    5: "Fri",
    6: "Sat"
}

icons = {
    "Clouds": "cloud",
    "Rain": "cloud-rain",
    "Snow": "cloud-snow"
}


async def _request(city: str) -> dict:
    URL = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}"
    async with ClientSession() as cs:
        async with cs.get(URL) as r:
            res = await r.json()
        return res


async def get_data(_data: dict) -> dict:
    data = dict()
    data['country'] = _data['city']['country']
    _timezone = country_timezones[data['country']][0]
    _timezone = timezone(_timezone)
    day = datetime.now(_timezone).weekday()
    current = _data['list'][0]
    data['today'] = {
        'temp': current['main']['temp'],
        'day': weekdays[day],
        'pressure': current['main']['pressure'],
        'humidity': current['main']['humidity'],
        'wind': current['wind']['speed'],
        'weather': current['weather'][0]['main']
    }
    data['today']['icon'] = icons[data['today']['weather']]

    data['city'] = _data['city']['name']
    data['days'] = [
        _data['list'][1]['main']['temp'], _data['list'][2]['main']['temp'],
        _data['list'][3]['main']['temp'], _data['list'][4]['main']['temp']
    ]
    data['climates'] = [
        _data['list'][1]['weather'][0]['main'], _data['list'][2]['weather'][0]['main'],
        _data['list'][3]['weather'][0]['main'], _data['list'][4]['weather'][0]['main']
    ]

    data['climates'][:] = (icons[i] for i in data['climates'])
    days = list(weekdays.keys())
    i = days.index(day)
    days = days[i+1:] + days[:i+1]
    data['daynames'] = days[:4]
    data['daynames'][:] = (weekdays[i] for i in data['daynames'])
    return data


@app.get("/")
async def index(request: Request):
    data = await _request(city="Kannur")
    data = await get_data(_data=data)
    context = {"request": request, 'data': data}
    return templates.TemplateResponse("weather.html", context=context)
