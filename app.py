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
    
    city_data = weather_data[weather_pair[city]]
    time1_begin = city_data["weatherElement"][0]["time"][0]["startTime"]
    time1_end = city_data["weatherElement"][0]["time"][0]["endTime"]

    time2_begin = city_data["weatherElement"][0]["time"][1]["startTime"]
    time2_end = city_data["weatherElement"][0]["time"][1]["endTime"]

    time3_begin = city_data["weatherElement"][0]["time"][2]["startTime"]
    time3_end = city_data["weatherElement"][0]["time"][2]["endTime"]

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

    city_weather_report = f"""{time1_begin[5:16]} ~ 
{time1_end[omit_time_year1:16]} 
天氣：{wxs[0]}
體感：{cis[0]}
溫度：{mints[0]}°C ~ {maxts[0]}°C
降雨機率：{pops[0]}%

{time2_begin[5:16]} ~ 
{time2_end[omit_time_year2:16]} 
天氣：{wxs[1]}
體感：{cis[1]}
溫度：{mints[1]}°C ~ {maxts[1]}°C
降雨機率：{pops[1]}%

{time3_begin[5:16]} ~ 
{time3_end[omit_time_year3:16]}
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

        if user_id not in user_status:
            user_status[user_id] = {
                "weatherstep" : 0,
                "luckystep" : 0
            }
        
        weatherstep = user_status[user_id]["weatherstep"]
        luckystep = user_status[user_id]["luckystep"]

        if text == "天氣" and weatherstep == 0:
            user_status[user_id]["weatherstep"] = 1
            send_quick_reply(line_bot_api, event, "請選擇地區", ["北部", "中部", "南部", "東部", "外島地區"])
        
        elif weatherstep == 1:
            user_status[user_id]["region"] = text
            user_status[user_id]["weatherstep"] = 2

            if text == "北部":
                send_quick_reply(line_bot_api, event, "請選擇城市", ["基隆市", "臺北市", "新北市", "桃園市", "新竹市", "新竹縣", "宜蘭縣"])
            elif text == "中部":
                send_quick_reply(line_bot_api, event, "請選擇城市", ["苗栗縣", "臺中市", "彰化縣", "雲林縣", "南投縣"])
            elif text == "南部":
                send_quick_reply(line_bot_api, event, "請選擇城市", ["嘉義縣", "嘉義市", "臺南市", "高雄市", "屏東縣"])
            elif text == "東部":
                send_quick_reply(line_bot_api, event, "請選擇城市", ["花蓮縣", "臺東縣"])
            elif text == "外島地區":
                send_quick_reply(line_bot_api, event, "請選擇城市", ["澎湖縣", "連江縣", "金門縣"])

            else:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        replyToken=event.reply_token,
                        messages=[TemplateMessage(text="請選擇有效地區")]
                    )
                )
        
        elif weatherstep == 2:
            city = text
            weatherinfo = get_weather(city)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text=weatherinfo)]
                )
            )
            user_status[user_id]["weatherstep"] = 0
            



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

        # 今日運勢
        elif text == "今日運勢" and luckystep == 0:
            user_status[user_id]["luckystep"] = 1
            send_quick_reply(line_bot_api, event, "請選擇顏色", ["紅", "橙", "黃", "綠", "藍", "紫", "黑", "白"])

        elif luckystep == 1:
            lucky_result = color_hash(user_status[user_id], text)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text=f"您的運勢：{lucky_result}")]
                )
            )

            user_status[user_id]["luckystep"] = 0


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
        
        # if postback_data == "weather":
        #     user_city = event.message.text
        #     line_bot_api.reply_message(
        #         ReplyMessageRequest(
        #             replyToken=event.reply_token,
        #             messages=[TextMessage(text=get_weather(user_city))]
        #         )
        #     )

        
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