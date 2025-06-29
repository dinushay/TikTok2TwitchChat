import asyncio
import requests
from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, CommentEvent, GiftEvent, ShareEvent

# ======= Config =======

tiktok_username = "TikTok name"

twitch_access_token = "token from token generator" # https://twitchtokengenerator.com/quick/CovjkGKZkF
twitch_client_id = "id from token generator"
twitch_broadcaster_id = "broadcaster account id" # https://www.streamweasels.com/tools/convert-twitch-username-to-user-id
twitch_sender_id = "sender account id"

show_twitch_debug = False

track_comments = True
message_comments = "[%name%]: %message%"

track_gifts = True
message_gifts = "🎁 [%name%]: %count%x %giftname%"

# ======= Code =======

client: TikTokLiveClient = TikTokLiveClient(unique_id=tiktok_username)

def send_twitch_message(message: str):
    url = "https://api.twitch.tv/helix/chat/messages"
    headers = {
        "Authorization": f"Bearer {twitch_access_token}",
        "Client-Id": twitch_client_id,
        "Content-Type": "application/json"
    }
    data = {
        "broadcaster_id": twitch_broadcaster_id,
        "sender_id": twitch_sender_id,
        "message": message
    }
    response = requests.post(url, json=data, headers=headers)
    if show_twitch_debug:
        print(f"[Twitch API Debug] {response.status_code}: {response.text}")

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    client.logger.info(f"Connected to @{event.unique_id}!")

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    if track_comments:
        msg = message_comments.replace("%name%", event.user.nickname).replace("%message%", event.comment)
        print(f"[Comment] {msg}")
        send_twitch_message(msg)

@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    if track_gifts and (not event.gift.streakable or not event.streaking):
        msg = message_gifts.replace("%name%", event.user.nickname)\
                           .replace("%count%", str(event.repeat_count))\
                           .replace("%giftname%", event.gift.name)
        print(f"[Gift] {msg}")
        send_twitch_message(msg)

async def check_loop():
    while True:
        while not await client.is_live():
            client.logger.info("Not live. Checking again in 60 seconds.")
            await asyncio.sleep(60)
        client.logger.info("Streamer is live! Connecting...")
        await client.connect()

if __name__ == '__main__':
    client.logger.setLevel(LogLevel.INFO.value)
    asyncio.run(check_loop())
