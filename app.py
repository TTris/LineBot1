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
    ImageMessage
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

        if text == "文字":
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