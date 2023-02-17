from flask import Flask, request
from webexteamssdk import WebexTeamsAPI, Webhook
from google.cloud import translate_v2 as translate
import os

app = Flask(__name__)
api = WebexTeamsAPI(access_token=os.environ.get("WEBEX_TEAMS_ACCESS_TOKEN"))
client = translate.Client.from_service_account_json('PATH_TO_GCP_SERVICE_ACCOUNT_KEY')
domain = os.environ.get("FLASK_DOMAIN")

def translate_message(message):
    result = client.translate(message.text, target_language='en')
    translation = result['translatedText']
    api.messages.create(roomId=message.roomId, text=translation)

# Create a Webhook to receive message events
webhook = api.webhooks.create(
    name="My Translation Bot Webhook",
    targetUrl=f"https://{domain}/translate",
    resource="messages",
    event="created"
)

# Define the Flask endpoint to receive Webex Teams webhook events
@app.route('/translate', methods=['GET', 'POST'])
def handle_webhook():
    data = request.json
    event = api.webhooks.construct_event(data, request.headers.get('X-Spark-Signature'))
    if event.resource == 'messages' and event.data.personId != api.people.me().id:
        message = api.messages.get(event.data.id)
        translate_message(message)
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)
