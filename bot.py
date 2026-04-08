import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import string
from flask import Flask
import threading
import os

# Aapki Details
TOKEN = "8677737410:AAE5JXHtiuQE5c1iWuJmx5AUysB5CdbueL4"
ADMIN_ID = 1484173564

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__) # Render ke liye Dummy Web Server

# Memory Storage
CHANNELS = {} 
GEN_LINKS = {} 
USER_STATES = {} 

VIDEO_URL = "https://files.catbox.moe/4hbu2q.mp4"
CAPTION_TEMPLATE = """💎 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 {name} 
 𝗧𝗢 ZX 𝗠𝗢𝗗𝗦 𝗗𝗥𝗜𝗣 𝗞𝗘𝗬 

🎮 𝗬𝗼𝘂𝗿 𝗙𝗥𝗘𝗘 𝗙𝗜𝗥𝗘 𝗔𝗣𝗞𝗠𝗢𝗗 𝗞𝗘𝗬 𝗶𝘀 𝗷𝘂𝘀𝘁 𝗼𝗻𝗲 𝘀𝘁𝗲𝗽 𝗮𝘄𝗮𝘆! 🔥
━━━━━━━━━━━━━━━

🛠️ 𝗠𝗢𝗗 𝗙𝗘𝗔𝗧𝗨𝗥𝗘𝗦:
✅ 𝗦𝗶𝗹𝗲𝗻𝘁 𝗞𝗶𝗹𝗹 / 𝗦𝗶𝗹𝗲𝗻𝘁 𝗔𝗶𝗺
✅ 𝗠𝗮𝗴𝗻𝗲𝘁𝗶𝗰 𝗔𝗶𝗺
✅ 𝗔𝗻𝘁𝗶-𝗧𝗮𝘁𝘂
✅ 𝗚𝗵𝗼𝘀𝘁 𝗛𝗮𝗰𝗸 / 𝗦𝗽𝗲𝗲𝗱 𝗛𝗮𝗰𝗸
✅ 𝗘𝗦𝗣 (𝗡𝗮𝗺𝗲, 𝗟𝗶𝗻𝗲, 𝗕𝗼𝘅)

━━━━━━━━━━━━━━━
🚨 𝗔𝗖𝗖𝗘𝗦𝗦 𝗚𝗘𝗧 𝗞𝗔𝗥𝗡𝗘 𝗞𝗘 𝗟𝗜𝗬𝗘

📢 𝗡𝗶𝗰𝗵𝗲 𝗱𝗶𝘆𝗲 𝗴𝗮𝘆𝗲 𝘀𝗮𝗿𝗲 𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀 𝗝𝗢𝗜𝗡 𝗸𝗮𝗿𝗻𝗮 𝗭𝗔𝗥𝗨𝗥𝗜 𝗵𝗮𝗶
━━━━━━━━━━━━━━━
1️⃣ 𝗦𝗮𝗯𝗵𝗶 𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀 𝗝𝗼𝗶𝗻 𝗸𝗮𝗿𝗲𝗶𝗻
2️⃣ 𝗝𝗼𝗶𝗻 𝗸𝗲 𝗯𝗮𝗮𝗱 “✅ 𝗗𝗼𝗻𝗲 !!” 𝗯𝘂𝘁𝘁𝗼𝗻 𝗽𝗮𝗿 𝗰𝗹𝗶𝗰𝗸 𝗸𝗮𝗿𝗲𝗶𝗻
━━━━━━━━━━━━━━━"""

# ----------------- ADMIN COMMANDS ----------------- #

@bot.message_handler(commands=['addchannel'])
def add_channel_start(message):
    if message.from_user.id != ADMIN_ID: return
    msg = bot.reply_to(message, "Pehle mujhe channel me Admin banayein aur fir yahan uski ID send karein (Example: -100123456789):")
    bot.register_next_step_handler(msg, process_channel_id)

def process_channel_id(message):
    try:
        ch_id = int(message.text)
        member = bot.get_chat_member(ch_id, bot.user.id)
        if member.status != 'administrator':
            bot.reply_to(message, "❌ Bot is channel me Admin nahi hai. Pehle admin banayein aur /addchannel dobara karein.")
            return
        
        chat = bot.get_chat(ch_id)
        link = chat.invite_link
        if not link:
            link = bot.export_chat_invite_link(ch_id)
            
        # REALITY: Telegram Bot API 9.4 Official styles are applied here!
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🔵 Primary (Blue)", callback_data=f"color_{ch_id}_primary"),
            InlineKeyboardButton("🟢 Success (Green)", callback_data=f"color_{ch_id}_success"),
            InlineKeyboardButton("🔴 Danger (Red)", callback_data=f"color_{ch_id}_danger")
        )
            
        bot.reply_to(message, f"✅ Channel '{chat.title}' joined!\nAb is channel ke button ka Color select karein:", reply_markup=markup)
        CHANNELS[ch_id] = {"url": link, "name": chat.title, "color": "primary"} 
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}\nShayad ID galat hai ya bot admin nahi hai.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('color_'))
def save_color(call):
    if call.from_user.id != ADMIN_ID: return
    parts = call.data.split('_')
    ch_id = int(parts[1])
    color_style = parts[2]
    
    if ch_id in CHANNELS:
        CHANNELS[ch_id]['color'] = color_style
        # Mapping for a friendly reply message
        color_name = {"primary": "Blue", "success": "Green", "danger": "Red"}
        bot.edit_message_text(f"✅ Button color '{color_name.get(color_style, color_style)}' set ho gaya hai!", call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['genlink'])
def genlink_start(message):
    if message.from_user.id != ADMIN_ID: return
    msg = bot.reply_to(message, "Koi message, file ya photo send/forward karein jiska Link banana hai:")
    bot.register_next_step_handler(msg, process_genlink)

def process_genlink(message):
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    GEN_LINKS[code] = {"message_id": message.message_id, "chat_id": message.chat.id}
    
    bot_info = bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={code}"
    
    bot.reply_to(message, f"✅ **Aapka Link Ready Hai:**\n`{link}`\n\nIs link ko apne users ke sath share karein.", parse_mode="Markdown")

# ----------------- USER FLOW ----------------- #

def check_user_joined(user_id):
    not_joined = []
    for ch_id in CHANNELS:
        try:
            status = bot.get_chat_member(ch_id, user_id).status
            if status not in ['member', 'administrator', 'creator']:
                not_joined.append(ch_id)
        except:
            not_joined.append(ch_id)
    return not_joined

def get_sub_keyboard(not_joined_channels):
    markup = InlineKeyboardMarkup(row_width=1)
    for ch_id in not_joined_channels:
        data = CHANNELS[ch_id]
        # Yahan Official Telegram Button Colors (API 9.4) add kiye gaye hain
        markup.add(InlineKeyboardButton(text=f"Join {data['name']}", url=data['url'], style=data['color']))
    
    # Try Again button ko bhi green success style de diya hai
    markup.add(InlineKeyboardButton("✅ Try Again / Done ♻️", callback_data="check_join", style="success"))
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    payload = message.text.replace('/start', '').strip()
    if payload:
        USER_STATES[message.from_user.id] = payload

    caption = CAPTION_TEMPLATE.format(name=message.from_user.first_name)
    not_joined = check_user_joined(message.from_user.id)
    
    if len(not_joined) == 0:
        bot.send_message(message.chat.id, "🎉 Aapne sabhi channels pehle se join kiye hue hain!")
        send_hidden_file(message.from_user.id, message.chat.id)
        return

    bot.send_video(message.chat.id, video=VIDEO_URL, caption=caption, reply_markup=get_sub_keyboard(not_joined))

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def verify_join(call):
    user_id = call.from_user.id
    not_joined = check_user_joined(user_id)
    
    if len(not_joined) > 0:
        bot.answer_callback_query(call.id, "❌ Aapne abhi tak saare channels join nahi kiye hain!", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "✅ Verification Successful!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_hidden_file(user_id, call.message.chat.id)

def send_hidden_file(user_id, chat_id):
    if user_id in USER_STATES:
        code = USER_STATES[user_id]
        if code in GEN_LINKS:
            data = GEN_LINKS[code]
            bot.copy_message(chat_id=chat_id, from_chat_id=data['chat_id'], message_id=data['message_id'])
        del USER_STATES[user_id]
    else:
        bot.send_message(chat_id, "🎉 **Access Granted!** Aap verified hain.")

# ----------------- FLASK & RENDER SETUP ----------------- #
@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_bot():
    print("🤖 Bot Started Super Fast...")
    # Timeout hata diya taaki fast response mile
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    # Bot ko alag background thread me chalayenge taaki Web Service band na ho
    threading.Thread(target=run_bot).start()
    # Flask app ko port par run karenge (Render ke liye zaroori)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
