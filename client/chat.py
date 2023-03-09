import asyncio
import datetime

from pyodide.http import pyfetch
import json
import js

users_list = []
message_list = []
last_seen_id = 0
send_message = js.document.getElementById("send_message")
join_conversation = js.document.getElementById("join_conversation")
users = js.document.getElementById("users")
user = js.document.getElementById("user")
user_label = js.document.getElementById("user_label")
message_text = js.document.getElementById("message_text")
chat_window = js.document.getElementById("chat_window")


async def fetch(url, method, payload=None):
    kwargs = {
        "method": method
    }
    if method == "POST":
        kwargs["body"] = json.dumps(payload)
        kwargs["headers"] = {"Content-Type": "application/json"}
    return await pyfetch(url, **kwargs)


def set_timeout(delay, callback):
    def sync():
        asyncio.get_running_loop().run_until_complete(callback())
    asyncio.get_running_loop().call_later(delay, sync)


def append_message(message):
    message_list.append(message)
    item = js.document.createElement("li")
    item.className = "list-group-item"
    item.id = f'message_{message["msg_id"]}'
    item.innerHTML = f'[<b>{message["user"]}</b>]: <span>{message["text"]}</span>' \
                     f'<span class="badge text-bg-light text-secondary">{message["time"]}</span>'

    if message['user'] == user.value:
        delete_button = js.document.createElement("a")
        delete_button.className = "btn btn-primary"
        delete_button.id = message["msg_id"]
        delete_button.innerHTML = "Удалить"
        delete_button.onclick = delete_message_click
        item.append(delete_button)

    chat_window.prepend(item)


async def delete_message_click(e):
    message_id = e.target.id
    await fetch(f"/delete_message?id={message_id}", method="GET")


async def send_message_click(e):
    await fetch(f"/send_message?user={user.value}&text={message_text.value}", method="GET")
    message_text.value = ""


async def load_fresh_messages():
    global last_seen_id
    result_messages = await fetch(f"/get_messages?after={last_seen_id}", method="GET")
    result_users = await fetch(f"/get_users", method="GET")

    users_data = await result_users.json()
    connected_users = users_data["users"]
    for connected_user in connected_users:
        if connected_user["name"] not in users_list:
            item = js.document.createElement("span")
            if connected_user["name"] == user.value:
                item.className = "input-group-text fw-bold"
            else:
                item.className = "input-group-text"
            item.innerHTML = f'{connected_user["name"]}'
            users.append(item)
            users_list.append(connected_user["name"])

    data = await result_messages.json()
    all_messages = data["messages"]

    for message in all_messages:
        for user_now in connected_users:
            if (user_now["name"] == user.value) and (message["time"] > user_now["time"]):
                last_seen_id = message["msg_id"]
                append_message(message)

    result_messages = await fetch(f"/get_messages?after={0}", method="GET")
    data = await result_messages.json()
    all_messages = data["messages"]

    for message in message_list:
        if message not in all_messages:
            message_list.remove(message)
            message_block = js.document.getElementById(f'message_{message["msg_id"]}')
            message_block.remove()
    set_timeout(1, load_fresh_messages)


async def join_conversation_click(e):
    join_conversation.hidden = True
    user.hidden = True
    user_label.hidden = True
    message_text.hidden = False
    chat_window.hidden = False
    send_message.hidden = False
    users.hidden = False
    await fetch(f"/add_user?user={user.value}", method="GET")
    await load_fresh_messages()


send_message.onclick = send_message_click
join_conversation.onclick = join_conversation_click
