from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    TemplateMessage,
    ButtonsTemplate,
    PostbackAction, 
    PushMessageRequest,
    BroadcastRequest,
    MulticastRequest,
    Emoji,
    VideoMessage,
    LocationMessage,
    StickerMessage,
    ImageMessage,
    ConfirmTemplate, 
    CarouselColumn,
    CarouselTemplate, 
    ImageCarouselTemplate,
    ImageCarouselColumn, 
    MessageAction,
    URIAction,
    DatetimePickerAction,
    FlexMessage,
    FlexBubble,
    FlexImage,
    FlexBox,
    FlexText,
    FlexIcon,
    FlexButton,
    FlexSeparator,
    FlexContainer,
    QuickReply,
    QuickReplyItem,
    CameraAction,
    CameraRollAction,
    LocationAction,
    MessagingApiBlob,
    RichMenuSize,
    RichMenuArea,
    RichMenuRequest,
    RichMenuBounds
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent, 
    PostbackContent,
    FollowEvent,
    PostbackEvent
)
import json
import os
import requests
import hashlib
import datetime

from flyticket import cheapest_general

app = Flask(__name__)

configuration = Configuration(access_token=os.getenv("CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("CHANNEL_SECRET"))

user_status = {}


# get weather data
def get_weather(city):
    weather_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWA-01B95BFF-98D9-488C-8FEA-E1157A21162D"
    weather_json = requests.get(weather_url).json()

    weather_data = weather_json["records"]["location"]
    weather_pair = {}

    for i in range(22):
        cities = weather_data[i]["locationName"]
        weather_pair[cities] = i
    
    weekday_list=["一","二","三","四","五","六","日"]

    city_data = weather_data[weather_pair[city]]
    time1_begin = city_data["weatherElement"][0]["time"][0]["startTime"]
    time1_end = city_data["weatherElement"][0]["time"][0]["endTime"]
    time1_begin_week = weekday_list[datetime.datetime(year=int(time1_begin[:4]),month=int(time1_begin[5:7]),day=int(time1_begin[8:10])).weekday()]
    time1_end_week = weekday_list[datetime.datetime(year=int(time1_end[:4]), month=int(time1_end[5:7]), day=int(time1_end[8:10])).weekday()]

    time2_begin = city_data["weatherElement"][0]["time"][1]["startTime"]
    time2_end = city_data["weatherElement"][0]["time"][1]["endTime"]
    time2_begin_week = weekday_list[datetime.datetime(year=int(time2_begin[:4]),month=int(time2_begin[5:7]),day=int(time2_begin[8:10])).weekday()]
    time2_end_week = weekday_list[datetime.datetime(year=int(time2_end[:4]), month=int(time2_end[5:7]), day=int(time2_end[8:10])).weekday()]

    time3_begin = city_data["weatherElement"][0]["time"][2]["startTime"]
    time3_end = city_data["weatherElement"][0]["time"][2]["endTime"]
    time3_begin_week = weekday_list[datetime.datetime(year=int(time3_begin[:4]),month=int(time3_begin[5:7]),day=int(time3_begin[8:10])).weekday()]
    time3_end_week = weekday_list[datetime.datetime(year=int(time3_end[:4]), month=int(time3_end[5:7]), day=int(time3_end[8:10])).weekday()]

    wxs = []
    pops = []
    cis = []
    maxts = []
    mints = []

    for i in range(3):
        wxs.append(city_data["weatherElement"][0]["time"][i]["parameter"]["parameterName"])
        pops.append(city_data["weatherElement"][1]["time"][i]["parameter"]["parameterName"])
        mints.append(city_data["weatherElement"][2]["time"][i]["parameter"]["parameterName"])
        cis.append(city_data["weatherElement"][3]["time"][i]["parameter"]["parameterName"])
        maxts.append(city_data["weatherElement"][4]["time"][i]["parameter"]["parameterName"])
    
    omit_time_year1 = 5 if time1_begin[:4]==time1_end[:4] else 0
    omit_time_year2 = 5 if time1_begin[:4]==time2_end[:4] else 0
    omit_time_year3 = 5 if time1_begin[:4]==time3_end[:4] else 0

    city_weather_report = f"""{city}天氣：

{time1_begin[5:10]}({time1_begin_week}) {time1_begin[11:16]} ~ 
{time1_end[omit_time_year1:10]}({time1_end_week}) {time1_end[11:16]} 
天氣：{wxs[0]}
體感：{cis[0]}
溫度：{mints[0]}°C ~ {maxts[0]}°C
降雨機率：{pops[0]}%

{time2_begin[5:10]}({time2_begin_week}) {time2_begin[11:16]} ~ 
{time2_end[omit_time_year2:10]}({time2_end_week}) {time2_end[11:16]} 
天氣：{wxs[1]}
體感：{cis[1]}
溫度：{mints[1]}°C ~ {maxts[1]}°C
降雨機率：{pops[1]}%

{time3_begin[5:10]}({time3_begin_week}) {time3_begin[11:16]} ~ 
{time3_end[omit_time_year3:10]}({time3_end_week}) {time3_end[11:16]} 
天氣：{wxs[2]}
體感：{cis[2]}
溫度：{mints[2]}°C ~ {maxts[2]}°C
降雨機率：{pops[2]}%"""
    

    return(city_weather_report)

# hash for lucky status
def color_hash(userID, color):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    input_str = f"{userID}-{today}-{color}"
    hash_str = hashlib.sha256(input_str.encode()).hexdigest()
    hash_val = int(hash_str, 16) % 100

    if hash_val < 15:
        return "大吉"
    elif hash_val < 50:
        return "吉"
    elif hash_val < 85:
        return "凶"
    else:
        return "大凶"

# create carousle bubbles for all flight results
def create_fight_carousel_bubbles():
    flight_data = cheapest_general()
    carousel_bubbles = []

    for airport, details in flight_data.items():
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "從桃園機場(TPE)出發",
                    "size": "xxs",
                    "color": "#aaaaaa"
                },
                {
                    "type": "text",
                    "text": details["target_airport"],
                    "weight": "bold",
                    "size": "md",
                    "wrap":True
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "text",
                            "text": "出發時間",
                            "color": "#aaaaaa",
                            "size": "sm",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": details["departure"][:10],
                            "wrap": True,
                            "color": "#666666",
                            "size": "sm",
                            "flex": 5
                        }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "text",
                            "text": "返程時間",
                            "color": "#aaaaaa",
                            "size": "sm",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": details["return"][:10],
                            "wrap": True,
                            "color": "#666666",
                            "size": "sm",
                            "flex": 5
                        }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                        {
                            "type": "text",
                            "text": "參考票價",
                            "color": "#aaaaaa",
                            "size": "sm",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": f"約NTD {details["price"]}元",
                            "size": "sm",
                            "flex": 5,
                            "color": "#666666"
                        }
                        ],
                        "spacing": "sm"
                    },
                    {
                        "type": "text",
                        "text": "真實票價請參考購票頁面",
                        "size": "xxs",
                        "color": "#B0C4DE"
                    }
                    ]
                }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                    "type": "uri",
                    "label": "Trip.com 比價頁面",
                    "uri": details["trip_link"]
                    },
                    "color": "#6495ED"
                }
                ]
            }
        }
        
        carousel_bubbles.append(bubble)

    return carousel_bubbles

# creat a list for all flight results
def creat_flight_list():
    flight_data = cheapest_general()
    list_len = len(flight_data)
    flight_count = 0
    current_page = 0
    flight_list_str = ""

    for airport, details in flight_data.items():
        if (flight_count//12)+1 != current_page:
            current_page += 1
            flight_list_str += f"共{list_len}筆資料｜第{current_page}頁/共{(list_len//12)+(1 if (list_len%12)!=0 else 0)}頁\n\n"
        flight_count += 1
        flight_list_str += f"{flight_count}. {details["target_airport"]}\n"
        flight_list_str += f"    時間：{(details["departure"][:10].replace("-","/"))} - {(details["return"][(5 if details["return"][:5]==details["departure"][:5]else 0):10]).replace("-","/")}\n"
        flight_list_str += f"    價錢：約 NTD {details["price"]}元\n"
        flight_list_str += "-"*30
        flight_list_str += "\n"

    return flight_list_str



@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

#add friend event
@line_handler.add(FollowEvent)
def handle_follow(event):
    print(f"Got {event.type} event")

#message event
@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        guide_list = ["介紹", "說明", "guide"]
        meow_list = ["Hi 可愛小貓咪", "小貓咪", "貓咪", "喵", "嗨", "Hi", "可愛小貓咪"]

        if user_id not in user_status:
            user_status[user_id] = {
                "weatherstep" : 0,
                "luckystep" : 0,
                "flightstep" : 0
            }
        
        weatherstep = user_status[user_id]["weatherstep"]
        luckystep = user_status[user_id]["luckystep"]
        flightstep = user_status[user_id]["flightstep"]

        # guide information
        if text.lower() in guide_list:
            guide_text="本喵學會找天氣、找機票、占卜\n其他還在學\n\n輸入「天氣」可以找36小時內天氣\n輸入「機票」可以找便宜機票\n輸入「今日運勢」本喵會占卜！"
            send_quick_reply(line_bot_api, event, guide_text, ["天氣","機票","今日運勢"])

        #天氣
        elif text == "天氣" and weatherstep == 0 and luckystep == 0 and flightstep == 0:
            user_status[user_id]["weatherstep"] = 1
            send_quick_reply(line_bot_api, event, "喵～請選地區", ["北部", "中部", "南部", "東部", "外島地區"])
        
        elif weatherstep == 1 and luckystep == 0 and flightstep == 0:
            region_list = ["北部", "中部", "南部", "東部", "外島地區"]
            if text not in region_list:
                send_quick_reply(line_bot_api, event, "請選擇有效地區", ["北部", "中部", "南部", "東部", "外島地區"])
            
            else:
                user_status[user_id]["region"] = text
                user_status[user_id]["weatherstep"] = 2

                if text == "北部":
                    send_quick_reply(line_bot_api, event, "請選城市", ["基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣", "宜蘭縣"])
                elif text == "中部":
                    send_quick_reply(line_bot_api, event, "請選城市", ["苗栗縣", "臺中市", "彰化縣", "雲林縣", "南投縣"])
                elif text == "南部":
                    send_quick_reply(line_bot_api, event, "請選城市", ["嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣"])
                elif text == "東部":
                    send_quick_reply(line_bot_api, event, "請選城市", ["花蓮縣", "臺東縣"])
                elif text == "外島地區":
                    send_quick_reply(line_bot_api, event, "請選城市", ["澎湖縣", "連江縣", "金門縣"])

                else:
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            replyToken=event.reply_token,
                            messages=[TextMessage(text="亂回！重來")]
                        )
                    )
                    user_status[user_id]["weatherstep"] = 0
            
        elif weatherstep == 2 and luckystep == 0 and flightstep == 0:
            city_list = ["基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣", "宜蘭縣", "苗栗縣", "臺中市", "彰化縣", "雲林縣", "南投縣", "嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣", "花蓮縣", "臺東縣", "澎湖縣", "連江縣", "金門縣"]
            if text not in city_list:
                line_bot_api.reply_message(
                        ReplyMessageRequest(
                            replyToken=event.reply_token,
                            messages=[TextMessage(text="亂回！重來")]
                        )
                    )
                user_status[user_id]["weatherstep"] = 0
            
            else: 
                city = text
                weatherinfo = get_weather(city)
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        replyToken=event.reply_token,
                        messages=[TextMessage(text=weatherinfo)]
                    )
                )
                user_status[user_id]["weatherstep"] = 0
        
        # 機票概述
        elif text == "機票" and weatherstep ==0 and luckystep ==0:
            explain_text = "喵～說明：\n\n輸入「機票清單」可以看到各地便宜機票列表（含目的地、時間、票價）\n方便快速滑閱想去的地方\n\n輸入「機票連結」可點選Trip.com購票連結\n但是一次只能顯示12筆資料，需輸入「機票第二頁」可以看到第13~24筆資料，依此類推"
            send_quick_reply(line_bot_api, event, explain_text, ["機票清單", "機票連結"])

        # 便宜機票清單
        elif text == "機票清單" and weatherstep ==0 and luckystep ==0:
            flight_list = creat_flight_list()[:5000]
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text=flight_list)]
                )
            )

        # 便宜機票連結
        elif text == "機票連結" and weatherstep == 0 and luckystep ==0:
            carousel_bubbles = create_fight_carousel_bubbles()

            carousel_dict = {
                "type":"carousel",
                "contents":carousel_bubbles[:12]
            }

            carousel_container = FlexContainer.from_json(json.dumps(carousel_dict))

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[FlexMessage(
                        altText="機票清單第一頁",
                        contents=carousel_container
                    )]
                )
            )

        elif text == "機票第二頁" and weatherstep == 0 and luckystep == 0:
            carousel_bubbles = create_fight_carousel_bubbles()

            carousel_dict = {
                "type":"carousel",
                "contents": carousel_bubbles[12:24]
            }

            carousel_container = FlexContainer.from_json(json.dumps(carousel_dict))

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[FlexMessage(
                        altText="機票清單第二頁",
                        contents=carousel_container
                    )]
                )
            )
       
        elif text == "機票第三頁" and weatherstep == 0 and luckystep == 0:
            carousel_bubbles = create_fight_carousel_bubbles()
            carousel_dict = {
                "type":"carousel",
                "contents": carousel_bubbles[24:]
            }

            carousel_container = FlexContainer.from_json(json.dumps(carousel_dict))

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[FlexMessage(
                        altText="機票清單第三頁",
                        contents=carousel_container
                    )]
                )
            )

        # 今日運勢
        elif text == "今日運勢" and luckystep == 0 and weatherstep == 0:
            user_status[user_id]["luckystep"] = 1
            send_quick_reply(line_bot_api, event, "喵～選顏色", ["紅", "橘", "黃", "綠", "藍", "紫", "黑", "白"])

        elif luckystep == 1 and weatherstep == 0:
            text_list = ["紅", "橘", "黃", "綠", "藍", "紫", "黑", "白","取消"]
            if text not in text_list:
                send_quick_reply(line_bot_api, event, "不想選可以打取消", ["紅", "橘", "黃", "綠", "藍", "紫", "黑", "白"])
            else:
                if text == "取消":
                    user_status[user_id]["luckystep"] = 0
                else:
                    lucky_result = color_hash(user_status[user_id], text)
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            replyToken=event.reply_token,
                            messages=[TextMessage(text=f"本喵掐指一算：{lucky_result}")]
                        )
                    )
                    user_status[user_id]["luckystep"] = 0


        #below are practice functions
        # Quick Reply
        elif text == "Quick reply":
            quick_reply = QuickReply(
                items=[
                    QuickReplyItem(
                        action=PostbackAction(
                            label="postback",
                            data="postback",
                            displayText="postback"
                        )
                    ),
                    QuickReplyItem(
                        action=MessageAction(
                            label="Message",
                            text="message"
                        )
                    ),
                    QuickReplyItem(
                        action=DatetimePickerAction(
                            label="Date",
                            data="date",
                            mode="date"
                        )
                    ),
                    QuickReplyItem(
                        action=DatetimePickerAction(
                            label="Time",
                            data="time",
                            mode="time"
                        )
                    ),
                    QuickReplyItem(
                        action=DatetimePickerAction(
                            label="Datetime",
                            data="datetime",
                            mode="datetime",
                            initial="2025-01-01T00:00",
                            max="2026-01-01T00:00",
                            min="2024-01-01T00:00"
                        )
                    ),
                    QuickReplyItem(
                        action=CameraAction(label="Camera")
                    ),
                    QuickReplyItem(
                        action=CameraRollAction(label="Camera Roll")
                    ),
                    QuickReplyItem(
                        action=LocationAction(label="Location")
                    )
                ]
            )

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(
                        text="請選擇項目",
                        quickReply=quick_reply
                    )]
                )
            )

        elif text == "flex":
            url = request.url_root + "/static/IMG_5975.jpg"
            url = url.replace("http", "https")
            line_flex_json = {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": url,
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "cover",
                    "action": {
                    "type": "uri",
                    "uri": "https://line.me/"
                    }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "Brown Cafe",
                        "weight": "bold",
                        "size": "xl",
                        "contents": [
                        {
                            "type": "span",
                            "text": "你好！"
                        },
                        {
                            "type": "span",
                            "text": "hello, world",
                            "weight": "bold"
                        }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": [
                        {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                        },
                        {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                        },
                        {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                        },
                        {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                        },
                        {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"
                        },
                        {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://developers-resource.landpress.line.me/fx/img/review_gray_star_28.png"
                        },
                        {
                            "type": "text",
                            "text": "5.0",
                            "size": "sm",
                            "color": "#999999",
                            "margin": "md",
                            "flex": 0
                        }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                            {
                                "type": "text",
                                "text": "Address",
                                "color": "#aaaaaa",
                                "size": "sm",
                                "flex": 3
                            },
                            {
                                "type": "text",
                                "text": "Flex Tower, 7-7-4 Midori-ku, Tokyo",
                                "wrap": True,
                                "color": "#666666",
                                "size": "sm",
                                "flex": 7
                            }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                            {
                                "type": "text",
                                "text": "Time",
                                "color": "#aaaaaa",
                                "size": "sm",
                                "flex": 1
                            },
                            {
                                "type": "text",
                                "text": "10:00 - 23:00",
                                "wrap": True,
                                "color": "#666666",
                                "size": "sm",
                                "flex": 5
                            }
                            ]
                        }
                        ]
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "uri",
                        "label": "Facebook",
                        "uri": "http://linecorp.com/"
                        },
                        "style": "primary",
                        "margin": "xs"
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "action": {
                        "type": "uri",
                        "label": "Instagram",
                        "uri": "http://linecorp.com/"
                        },
                        "margin": "xs"
                    }
                    ],
                    "margin": "none"
                }
                }
            line_flex_str = json.dumps(line_flex_json)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[FlexMessage(altText="詳細說明", contents=FlexContainer.from_json(line_flex_str))]
                )
            )

        # Confirm Template
        elif text == "Confirm":
            confirm_template = ConfirmTemplate(
                text = "今天學程式了嗎？",
                actions = [
                    MessageAction(label="是", text="是！"),
                    MessageAction(label="否", text="否！")
                ]
            )
            template_message = TemplateMessage(
                alt_text = "Confirm alt text",
                template = confirm_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken = event.reply_token,
                    messages=[template_message]
                )
            )

        # Buttons Template
        elif text == "Buttons":
            url = request.url_root + "/static/S__108437507.jpg"
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            buttons_template = ButtonsTemplate(
                thumbnailImageUrl = url,
                title = "示範",
                text = "這是一塊雞排",
                actions=[
                    URIAction(label="連結", uri="https://youtu.be/Mw3cODdkaFM?si=x7-LdpCpeVcBu7r2"),
                    PostbackAction(label="回傳值", data="ping", displayText="傳了"),
                    MessageAction(label="傳'哈囉'", text="哈囉"),
                    DatetimePickerAction(label="選擇時間", data="時間", mode="datetime")
                ])
            template_message = TemplateMessage(
                alt_text = "This is a buttons template.",
                template=buttons_template
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[template_message]
                )
            )
        
        # Carousel Template
        elif text == "Carousel":
            url = request.url_root + "/static/S__1563025412.jpg"
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            carousel_template = CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnailImageUrl=url,
                        title="第一項",
                        text="這是第一項的描述",
                        actions=[
                            URIAction(
                                label="點我前往Google",
                                uri="https://www.google.com"
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnailImageUrl=url,
                        title="第二項",
                        text="這是第二項的敘述",
                        actions=[
                            URIAction(
                                label="點我前往Youtube",
                                uri="https://www.youtube.com"
                            )
                        ]
                    )                         
                ]
            )
            carousel_message = TemplateMessage(
                altText="這是Carousel Template",
                template=carousel_template
            )

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[carousel_message]
                )
            )
        
        # ImageCarousel Template
        elif text == "Image Carousel":
            url = request.url_root + "/static"
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            image_carousel_template = ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        imageUrl= url + "/IMG_5575.jpg",
                        action=URIAction(
                            label="維基小貓咪",
                            uri="https://en.wikipedia.org/wiki/Cat"
                        )
                    ),
                    ImageCarouselColumn(
                        imageUrl= url + "/IMG_5975.jpg",
                        action=URIAction(
                            label="YT小貓咪",
                            uri="https://www.youtube.com/results?search_query=cat"
                        )
                    ),
                    ImageCarouselColumn(
                        imageUrl= url + "/S__112836713.jpg",
                        action=URIAction(
                            label="貓屎咖啡",
                            uri="https://en.wikipedia.org/wiki/Kopi_luwak"
                            
                        )
                    )
                ]
            )

            image_carousel_message = TemplateMessage(
                altText="圖片輪播範本",
                template=image_carousel_template
            )

            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[image_carousel_message]
                )
            )

        elif text == "文字":
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken = event.reply_token,
                    messages = [TextMessage(text = "這是文字訊息")]
                )
            )
        elif text == "表情符號":
            emojis = [
                Emoji(index=0, productId="670e0cce840a8236ddd4ee4c", emojiId= "004"),
                Emoji(index=12, productId="670e0cce840a8236ddd4ee4c", emojiId="007")
            ]
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken = event.reply_token,
                    messages = [TextMessage(text = "$ LINE 表情符號 $", emojis=emojis)]
                )
            )
        elif text == "貼圖":
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken = event.reply_token,
                    messages = [StickerMessage(packageId="446", stickerId="1990")]
                )
            )
        elif text == "圖片":
            url = request.url_root + "static/S__112836713.jpg"
            url = url.replace("http", "https")
            print(url)
            app.logger.info("url=" + url)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken = event.reply_token,
                    messages=[
                        ImageMessage(originalContentUrl=url, previewImageUrl=url)
                    ]
                )
            )
        elif text == "影片":
            url = request.url_root + "static/763812363.633727.mp4"
            url = url.replace("http", "https")
            app.logger.info("url=" + url)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken = event.reply_token,
                    messages = [
                        VideoMessage(originalContentUrl=url, previewImageUrl=url)
                    ]
                )
            )

        # easter eggs
        elif text in meow_list:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text="喵")]
                )
            )
        elif text == "耶":
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text="耶")]
                )
            )

        # else
        else:
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text="?")]
                )
            )

        # Reply message
        # line_bot_api.reply_message(
        #     ReplyMessageRequest(
        #         replyToken=event.reply_token,
        #         messages=[TextMessage(text = "reply message")]
        #     )
        # )

        # line_bot_api.reply_message_with_http_info(
        #     ReplyMessageRequest(
        #         reply_token=event.reply_token,
        #         messages=[TextMessage(text= "reply message with http info")]
        #     )
        # )

        # Push message
        # line_bot_api.push_message_with_http_info(
        #     PushMessageRequest(
        #         to = event.source.user_id,
        #         messages = [TextMessage(text = "Push!")]
        #     )
        # )

        #Broadcast message
        # line_bot_api.broadcast_with_http_info(
        #     BroadcastRequest(
        #         messages = [TextMessage(text = "Broadcast!")]
        #     )
        # )

        #Multicast message
        # line_bot_api.multicast_with_http_info(
        #     MulticastRequest(
        #         to = ["U3e29857aed4e5919c02429d45a21c910"],
        #         messages = [TextMessage(text = "Multicast!")],
        #         notificationDisabled = True
        #     )
        # )
        

# Build Quick Reply function
def send_quick_reply(line_bot_api, event, title, options=list):
    quick_reply_items = [QuickReplyItem(action=MessageAction(label=opt, text=opt)) for opt in options]
    message = TextMessage(text=title, quickReply=QuickReply(items=quick_reply_items))
    line_bot_api.reply_message(
        ReplyMessageRequest(
            replyToken=event.reply_token,
            messages= [message]
        )
    )



@line_handler.add(PostbackEvent)
def handle_postback(event):
    with ApiClient(configuration) as aip_client:
        line_bot_api = MessagingApi(aip_client)
        postback_data = event.postback.data
        
   
        if postback_data == "postback":
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text="Postback")]
                )
            )
        elif postback_data == "date":
            date = event.postback.params["date"]
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text=date)]
                )
            )
        elif postback_data == "time":
            time = event.postback.params["time"]
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text=time)]
                )
            )
        elif postback_data == "datetime":
            datetime = event.postback.params["datetime"]
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text=datetime)]
                )
            )

if __name__ == "__main__":
    app.run()


print(user_status)