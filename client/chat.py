import asyncio
from pyodide.http import pyfetch
import json
import js

last_seen_id = 0
send_message = js.document.getElementById("send_message")
sender = js.document.getElementById("sender")
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


# Добавляет новое сообщение в список сообщений
def append_message(message):
    item = js.document.createElement("li")
    item.className = "list-group-item"
    item.innerHTML = f'[<b>{message["sender"]}</b>]: <span>{message["text"]}</span><span class="badge text-bg-light text-secondary">{message["time"]}</span>'
    chat_window.prepend(item)


# Вызывается при клике на send_message
async def send_message_click(e):
    await fetch(f"/send_message?sender={sender.value}&text={message_text.value}", method="GET")
    message_text.value = ""


# Загружает новые сообщения с сервера и отображает их
async def load_fresh_messages():
    global last_seen_id
    # 2. Загружать только новые сообщения
    result = await fetch(f"/get_messages?after={last_seen_id}", method="GET")  # Делаем запрос
    data = await result.json()
    all_messages = data["messages"]  # Берем список сообщений из ответа сервера
    for msg in all_messages:
        last_seen_id = msg["msg_id"]  # msg_id Последнего сообщение
        append_message(msg)
    set_timeout(1, load_fresh_messages)  # Запускаем загрузку заново через секунду



send_message.onclick = send_message_click
# append_message({"sender":"Елена Борисовна", "text":"Присылаем в чат только рабочие сообщения!!!", "time": "00:01"})
load_fresh_messages()
