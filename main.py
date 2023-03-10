from flask import Flask, request, render_template, redirect
from datetime import datetime

app = Flask(__name__, static_folder="./client", template_folder="./client")  # Настройки приложения

msg_id = 1
user_id = 1
all_messages = []
all_users = []


def add_message(user, text):
    global msg_id
    new_message = {
        "msg_id": msg_id,
        "user": user,
        "text": text,
        "time": datetime.now()
    }
    msg_id += 1
    with open("messages.txt", "a") as file:
        file.write(f'{new_message["msg_id"]}. {new_message["time"]} - {new_message["user"]}: {new_message["text"]}')
        file.write("\n")

    all_messages.append(new_message)


@app.route("/delete_message")
def delete_message():
    message_id = int(request.args["id"])
    for message in all_messages:
        if message["msg_id"] == message_id:
            all_messages.remove(message)
    return {"result": True}


@app.route("/add_user")
def add_user():
    global user_id
    user = request.args["user"]
    new_user = {
        "msg_id": user_id,
        "name": user,
        "time": datetime.now()
    }
    user_id += 1

    all_users.append(new_user)
    return {"result": True}


@app.route("/chat")
def chat_page():
    return render_template("chat.html")


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


@app.route("/get_users")
def get_users():
    return {"users": all_users}


@app.route("/send_message")
def send_message():
    user = request.args["user"]
    text = request.args["text"]
    add_message(user, text)
    return {"result": True}


@app.route("/")
def start_page():
    return redirect("/chat", code=302)


app.run()
