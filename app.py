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
    DatetimePickerAction
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent, 
    PostbackContent,
    FollowEvent
)

app = Flask(__name__)

configuration = Configuration(access_token='vmfBnaQfcwTwVVrYUbbSOoOvI6P0+3PJQw9PpQAhvjmZJ3doZsVc1JVVnMnuc2U6Ldpl4gGQdx61mUoA4lozUKmbrquS7DZ8Jir700Rf/84k4ZxYEb7yR7ZbMXpVbu3yxkX4geBrXNluclbpovLxngdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('12934ee7f824bd04f046fc1fa2d2838f')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

#add friend event
@handler.add(FollowEvent)
def handle_follow(event):
    print(f"Got {event.type} event")

#message event
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # Confirm Template
        if text == "Confirm":
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


if __name__ == "__main__":
    app.run()