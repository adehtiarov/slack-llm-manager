import requests
import json
import time

token = "<SLACK_APP_TOKEN>"
channel_id = "<CHANNEL_ID>"

messages_count = 0

def get_channel_history(token, channel_id):
    headers = {"Authorization": "Bearer " + token}
    payload = {"channel": channel_id, "limit": 100}
    messages = []

    while True:
        r = requests.get("https://slack.com/api/conversations.history", headers=headers, params=payload)
        r.raise_for_status()
        data = r.json()

        messages.extend(data["messages"])

        if data["has_more"] == True:
            payload["cursor"] = data["response_metadata"]["next_cursor"]
        else:
            break

    print("Chat threads obtained: " + str(len(messages)))
    with open("threads.json", "w") as f:
        json.dump(messages, f, indent=4)

    return messages

def get_thread_replies(token, channel_id, thread_ts):
    global messages_count
    headers = {"Authorization": "Bearer " + token}
    payload = {"channel": channel_id, "ts": thread_ts}

    while True:
        try:
            r = requests.get("https://slack.com/api/conversations.replies", headers=headers, params=payload)
            r.raise_for_status()
            data = r.json()
            messages_count += len(data["messages"][1:]) # Exclude the first message which is the parent message
            return [message["text"] for message in data["messages"]]
        except requests.exceptions.HTTPError as err:
            if r.status_code == 429:
                retry_after = int(r.headers["Retry-After"])
                time.sleep(retry_after)
                continue
            else:
                raise err

def create_chat_history(token, channel_id):
    global messages_count
    history = get_channel_history(token, channel_id)
    chat_history = []
    last_progress_step = 0

    for message in history:
        messages_count += 1
        if messages_count // 1000 > last_progress_step:
            print("Messages: " + str(messages_count))
            with open("chat-history-processed.json", "w") as f:
                json.dump(chat_history, f, indent=4)
            last_progress_step += messages_count // 1000
        if "thread_ts" in message:
            replies = get_thread_replies(token, channel_id, message["thread_ts"])
            chat_history.append(replies)
        else:
            chat_history.append([message["text"]])

    return chat_history

chat_history = create_chat_history(token, channel_id)
with open("chat-history-processed.json", "w") as f:
    json.dump(chat_history, f, indent=4)

print("Threads: " + str(len(chat_history)))
print("Messages: " + str(messages_count))
