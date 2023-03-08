from flask import Flask, request, render_template
from datetime import datetime

app = Flask(__name__, static_folder="./client", template_folder="./client")  # Настройки приложения

msg_id = 1
all_messages = []
all_senders = []


def add_message(sender, text):
    global msg_id
    new_message = {
        "msg_id": msg_id,
        "sender": sender,
        "text": text,
        "time": datetime.now().strftime("%H:%M")
    }
    msg_id += 1
    with open("messages.txt", "a") as file:
        file.write(f"{new_message}")
        file.write("\n")

    all_messages.append(new_message)


def add_sender(sender):
    if sender in all_senders:
        pass
    else:
        all_senders.append(sender)


@app.route("/chat")
def chat_page():
    return render_template("chat.html")


# API для получения списка сообщений
@app.route("/get_messages")
def get_messages():
    after = int(request.args["after"])
    new_messages = []
    if after is not None:
        for message in all_messages:
            if message["msg_id"] > after:
                new_messages.append(message)
        return {"messages": new_messages}
    else:
        return {"messages": all_messages}


@app.route("/get_senders")
def get_senders():
    return {"senders": all_senders}


# HTTP-GET
# API для получения отправки сообщения  /send_message?sender=Mike&text=Hello
@app.route("/send_message")
def send_message():
    sender = request.args["sender"]
    text = request.args["text"]
    add_message(sender, text)
    add_sender(sender)
    return {"result": True}


# Главная страница
@app.route("/")
def hello_page():
    return "New text goes here"


app.run()
