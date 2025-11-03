from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

access_token = os.getenv("ACCESS_TOKEN")
phone_number_id = os.getenv("PHONE_NUMBER_ID")
token = os.getenv("VERIFY_TOKEN")

def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v24.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("📤 Sent message:", response.json())

@app.route('/whatsapp-webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        verify_token = token
        if request.args.get("hub.verify_token") == verify_token:
            return request.args.get("hub.challenge")
        return "Invalid verification token", 403

    elif request.method == 'POST':
        data = request.get_json()
        print("📩 Incoming WhatsApp Message:")
        print(data)

        try:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender = message["from"]
            text = message["text"]["body"]
            print(f"From: {sender}\nMessage: {text}")

            # 🔁 Auto reply
            reply_text = f"You said: {text}"
            send_whatsapp_message(sender, reply_text)

        except Exception as e:
            print("Error parsing incoming message:", e)

        return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(port=5000)
