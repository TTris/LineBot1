import json
import requests
import datetime
import os
import pandas as pd

token = os.getenv("TRAVELPAYOUTS_API_TOKEN")

url_cheapest = "https://api.travelpayouts.com/v1/prices/direct"
querystring = {
    "origin": "TPE",
    "destination": "-",
    "currency":"TWD",
    "token":token
}

df = pd.read_csv("airports.csv")
airport_dict = dict(zip(df["IATA"], zip(df["Country (CN)"], df["Airport"])))

response = requests.get(url_cheapest, params=querystring)
data = response.json()
airports = data["data"]
airports_list = airports.keys()

def cheapest_general():
    cheapest_general = {}
    for airport, airport_info in airports.items():
        if not airport_info:
            continue

        if airport not in cheapest_general:
            cheapest_general[airport] = {}

        try:
            cheapest_general[airport]["target_airport"] = airport_dict.get(airport)[0] + "-" + airport_dict.get(airport)[1] +"機場 "+ "("+airport+")"
        except TypeError:
            cheapest_general[airport]["target_airport"] = airport + "機場"
        
        for serial, items in airport_info.items():
            try:
                cheapest_general[airport]["departure"] = items["departure_at"][:10] +"日 "+ items["departure_at"][11:16]
                cheapest_general[airport]["return"] = items["return_at"][:10] + "日 "+ items["return_at"][11:16]
                cheapest_general[airport]["flight_number"] = str(items["airline"])+str(items["flight_number"])
                cheapest_general[airport]["price"] = str(items["price"])
                cheapest_general[airport]["trip_link"] = f"https://tw.trip.com/flights/showfarefirst?dcity=tpe&acity={airport}&ddate={items["departure_at"][:10]}&rdate={items["return_at"][:10]}&triptype=rt&nonstoponly=on&locale=zh-TW&curr=TWD"
            except KeyError:
                continue
            
    return cheapest_general


print(airports_list)