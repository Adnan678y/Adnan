import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
import time
import os
import json

with open('config.json', 'r') as f:
    DATA = json.load(f)

def getenv(var):
    return os.environ.get(var) or DATA.get(var, None)

bot_token = getenv("TOKEN")
api_hash = getenv("HASH")
api_id = getenv("ID")

bot = Client("mybot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

ss = getenv("STRING")
if ss is not None:
    acc = Client("myacc", api_id=api_id, api_hash=api_hash, session_string=ss)
    acc.start()
else:
    acc = None

# Start command
@bot.on_message(filters.command(["start"]))
def send_start(client: pyrogram.client.Client, message: pyrogram.types.messages_and_media.message.Message):
    bot.send_message(message.chat.id, f"__👋 Hi **{message.from_user.mention}**, I can forward content from restricted channels.__")

@bot.on_message(filters.command(["forward"]))
def forward_messages(client, message):
    try:
        msg_text = message.text.split()

        if len(msg_text) < 3:
            raise ValueError("Not enough arguments. Usage: /forward <link> <target_chat_id>")

        link = msg_text[1]  # e.g., https://t.me/xxxx/1-900
        target_chat_id = msg_text[2]  # e.g., -1002264671945

        # Validate target_chat_id
        try:
            target_chat_id = int(target_chat_id)
        except ValueError:
            bot.send_message(chat_id=message.chat.id, text="**Invalid target_chat_id. It should be a numerical ID.**", reply_to_message_id=message.id)
            return

        # Parse the link
        datas = link.split("/")
        if len(datas) < 5:
            bot.send_message(chat_id=message.chat.id, text="**Invalid link format.**", reply_to_message_id=message.id)
            return

        # Extract message ID
        msg_id_part = datas[-1]
        if '-' in msg_id_part:
            fromID, toID = map(int, msg_id_part.split('-'))
        else:
            fromID = toID = int(msg_id_part)

        # Notify user about the start of forwarding
        status_message = bot.send_message(chat_id=message.chat.id, text="⏳ **Starting to forward messages...**", reply_to_message_id=message.id)

        # Iterate over the message IDs and download then upload them
        for msgid in range(fromID, toID + 1):
            try:
                msg = client.get_messages(datas[3], msgid)  # Public chat based on username

                # Prepare custom caption
                custom_caption = "MAKE BY @Im_adnan_khan"
                if msg.caption:
                    custom_caption = f"{msg.caption}\n\n{custom_caption}"

                # Check message type and handle accordingly
                if msg.document:
                    file = client.download_media(msg)
                    bot.send_document(chat_id=target_chat_id, document=file, caption=custom_caption, reply_to_message_id=message.id)
                elif msg.photo:
                    file = client.download_media(msg)
                    bot.send_photo(chat_id=target_chat_id, photo=file, caption=custom_caption, reply_to_message_id=message.id)
                elif msg.video:
                    file = client.download_media(msg)
                    bot.send_video(chat_id=target_chat_id, video=file, caption=custom_caption, reply_to_message_id=message.id)
                elif msg.audio:
                    file = client.download_media(msg)
                    bot.send_audio(chat_id=target_chat_id, audio=file, caption=custom_caption, reply_to_message_id=message.id)
                elif msg.text:
                    bot.send_message(chat_id=target_chat_id, text=f"{msg.text}\n\n{custom_caption}", reply_to_message_id=message.id)
                elif msg.animation:
                    file = client.download_media(msg)
                    bot.send_animation(chat_id=target_chat_id, animation=file, caption=custom_caption, reply_to_message_id=message.id)
                elif msg.sticker:
                    file = client.download_media(msg)
                    bot.send_sticker(chat_id=target_chat_id, sticker=file, reply_to_message_id=message.id)

                time.sleep(1)  # Delay to prevent hitting rate limits
            except Exception as e:
                print(f"Error processing message ID {msgid}: {str(e)}")
                bot.send_message(chat_id=message.chat.id, text=f"**Error processing message ID {msgid}: {str(e)}**", reply_to_message_id=message.id)

        bot.edit_message_text(chat_id=status_message.chat.id, message_id=status_message.id, text="✅ **All messages have been processed!**")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        bot.send_message(chat_id=message.chat.id, text=f"**An error occurred: {str(e)}**", reply_to_message_id=message.id)

# Infinity polling
bot.run()
