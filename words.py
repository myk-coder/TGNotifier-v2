from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError
import asyncio
import sys
import argparse
from googletrans import Translator, LANGUAGES

# Ensure UTF-8 encoding is used
sys.stdout.reconfigure(encoding='utf-8')

api_id = 23049739
api_hash = 'ee6820282b04e3713870f75104475782'
phone_number = '+17029887500'
bot_token = '7329028440:AAFwo_gWggwQJ4MwIN8hWoVxtSNvdjl9HQ4'

user_messages = []
ban_list = []
link_domains = ["x.com", "youtube.com", "youtu.be", "fintop.io", "vxtwitter.com", "twitter.com", "claim-lavanetwork.xyz", "t.me"]  # Add more domains as needed
start_char = ["/", "_", "🛜" , "👽" , "🚀", "✴️", "🚨", "📣", "💫", "✅", "🐱", "✈️", "⏰", "💊", "🎁", "🦊", "🔥", "✨", "🟢", "💥", "😏", "➡️", "💲", "#" , "1️⃣" , "Next", "Sex"]
word_list = ["sex", "nude"]  # Add more words as needed
keywords = [
    "phrase", "stak", "wallet", "cant", "can't", "eth", "unstake", "delegat", "undelegate", "error", "revert", "fail", "claim", "meta", "help me", "help", "where", "0x", "execution", "fix", "bug", "issue", "unable", "status", "load", "not", "migrat", "rpc", "can i", "can we", "kyc", "register", "days", "hours", "when", "why", "what", "who", "stop", "work", "broken", "lp", "reward", "point", "txn", "eligib", "network", "convert", "any", "key", "problem", "pool", "liquid", "add", "my", "new", "want", "how", "valid", "invalid", "node", "support", "withdraw", "token", "allocat", "quest", "farm", "unable", "ledger", "keplr", "stuck", "approv", "happen", "lock" , "unlock" , "exchange" , "link", "mainnet", "testnet", "mine", "mismatch", "opcode", "reason", "limit", "broadcast", "rate", "pars", "timeout", "block", "exceed", "congest", "authoriz", "server", "internal", "unknown", "expire", "sync", "parameter", "resource", "fee", "estimat", "contract", "deploy", "execution", "decrypt", "access", "transact", "insufficient", "permission", "required", "initializ", "import", "export", "generat" , "hardware " , "outdate" , "storage" , "corrupt" , "unsupported" , "version" , "balance" , "sale" , "private" , "whitelist" , "allocat" , "crowdsale" , "subscription" , "round" , "invest" , "offering" , "period" , "vest" , "minimum" , "maximum" , "partiicpat" , "contribut" , "fund" , "reserve" , "fcfs" , "join" , "app" , "submi" , "deposit" , "profit" , "transfer" , "distribut" , "ROI" , "yield" , "swap" , "validat" , "APY" , "earn" , "bond" , "harvest" , "apr" , "compound" , "vault" , "credit" , "coin" , "hash" , "simulation" "?"
]

chat_id = -1002234552300  # Target chat ID
message_buffer = []
buffer_lock = asyncio.Lock()
translator = Translator()

def is_excluded_message(text):
    text_lower = text.lower()
    if any(domain in text_lower for domain in link_domains):
        return True
    if any(text.startswith(char) for char in start_char):
        return True
    if any(word in text_lower for word in word_list):
        return True
    return False

def contains_keywords(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)

async def save_message(message, chat):
    try:
        chat_title = chat.title
        message_info = {
            "sender_name": chat_title,
            "text": message.text
        }
        print(f"> {chat_title}: {message.text}")
    except ValueError as e:
        chat_title = "Unnamed"
        message_info = {
            "sender_name": chat_title,
            "text": message.text
        }
        print(e)
        print(f"> {message.sender_id}: {message.text}")
    
    user_messages.append(message_info)

    if chat.username:
        message_link = f"https://t.me/{chat.username}/{message.id}"
    else:
        message_link = f"https://t.me/c/{chat.id}/{message.id}"
    
    formatted_message = f"**{chat_title}**\n\n🦊>{message.text}<🦊\n\n{message_link}"

    async with buffer_lock:
        message_buffer.append(formatted_message)

async def send_buffered_messages(client):
    while True:
        await asyncio.sleep(5)
        async with buffer_lock:
            if message_buffer:
                messages_to_send = message_buffer.copy()
                message_buffer.clear()
                for message in messages_to_send:
                    max_retries = 5
                    for attempt in range(max_retries):
                        try:
                            await client.send_message(chat_id, message)
                            break
                        except FloodWaitError as e:
                            print(f"Flood wait error: {e}")
                            await asyncio.sleep(e.seconds)
                        except Exception as e:
                            print(f"Error sending message: {e}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            else:
                                print(f"Failed to send message after {max_retries} attempts")
                                raise

async def main(use_bot):
    client = TelegramClient('session_name', api_id, api_hash)
    sender_client = TelegramClient('sender', api_id, api_hash)

    if use_bot:
        await sender_client.start(bot_token=bot_token)
    else:
        await client.start()
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            await client.sign_in(phone_number, input('Enter the code: '))
            if client.is_user_authorized() and client.session.save():
                print("Client authorized and session saved.")
            if not await client.is_user_authorized():
                raise SessionPasswordNeededError()
        
    async with client, sender_client:
        @client.on(events.NewMessage(incoming=True))
        async def handle_new_message(event):
            sender = await event.get_sender()
            chat = await event.get_chat()
            if event.is_group and chat.title not in ban_list:
                if hasattr(sender, 'bot') and not sender.bot:
                    if not event.message.media and not is_excluded_message(event.message.text):
                        try:
                            translated = translator.translate(event.message.text, dest='en')
                            translated_text = translated.text
                        except Exception as e:
                            print(f"Translation error: {e}")
                            translated_text = event.message.text
                        if contains_keywords(translated_text):
                            await save_message(event.message, chat)

        @client.on(events.NewMessage(pattern=r'/ban (.+)'))
        async def ban_chat(event):
            ban_list.append(event.pattern_match.group(1))
            await event.respond(f"{event.pattern_match.group(1)} has been banned.")
            print(ban_list)

        @client.on(events.NewMessage(pattern='/messages'))
        async def send_saved_messages(event):
            if user_messages:
                for msg in user_messages:
                    await event.respond(f"{msg['sender_name']}: {msg['text']}")
            else:
                await event.respond("No messages saved.")

        # Start the buffered message sender
        asyncio.create_task(send_buffered_messages(sender_client))

        await client.run_until_disconnected()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Telegram bot or user account for message processing.')
    parser.add_argument('--use-bot', action='store_true', help='Use bot token for sending messages.')
    args = parser.parse_args()

    asyncio.run(main(args.use_bot))
