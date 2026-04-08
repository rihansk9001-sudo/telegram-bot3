import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import string
from flask import Flask
import threading
import os
import time

# Aapki Details
TOKEN = "8677737410:AAE5JXHtiuQE5c1iWuJmx5AUysB5CdbueL4"
ADMIN_ID = 1484173564

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

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

# ================== BOSS ADMIN PANEL ================== #

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("➕ Add Channel", callback_data="panel_add"),
        InlineKeyboardButton("➖ Remove Channel", callback_data="panel_rem"),
        InlineKeyboardButton("📋 View Channels", callback_data="panel_view"),
        InlineKeyboardButton("📊 Stats", callback_data="panel_stats"),
        InlineKeyboardButton("📢 Broadcast", callback_data="panel_broad"),
        InlineKeyboardButton("🚫 Ban User", callback_data="panel_ban")
    )
    
    bot.reply_to(message, "🧑‍💻 **Boss Admin Panel**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('panel_'))
def handle_admin_panel(call):
    if call.from_user.id != ADMIN_ID: return
    action = call.data.split('_')[1]
    
    if action == "add":
        msg = bot.send_message(call.message.chat.id, "Channel ID send karein (Example: -100123456789):")
        bot.register_next_step_handler(msg, process_channel_id)
        
    elif action == "rem":
        if not CHANNELS:
            bot.answer_callback_query(call.id, "Koi channel add nahi hai!", show_alert=True)
            return
        markup = InlineKeyboardMarkup()
        for ch_id, data in CHANNELS.items():
            markup.add(InlineKeyboardButton(f"❌ Remove {data['name']}", callback_data=f"del_{ch_id}"))
        bot.send_message(call.message.chat.id, "Kis channel ko remove karna hai?", reply_markup=markup)
        
    elif action == "view":
        if not CHANNELS:
            bot.send_message(call.message.chat.id, "List khali hai.")
            return
        text = "📋 **Added Channels:**\n\n"
        for ch_id, data in CHANNELS.items():
            text += f"ID: `{ch_id}` | Style: {data['color']} | Name: {data['name']}\n"
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
        
    elif action == "stats":
        bot.send_message(call.message.chat.id, "📊 **Bot Stats:**\n\nAbhi database feature connect nahi hai, isliye exact users count available nahi hai. (Temporary: 0 Users)")
        
    elif action == "broad":
        msg = bot.send_message(call.message.chat.id, "Broadcast karne ke liye message send karein:")
        bot.register_next_step_handler(msg, process_broadcast)
        
    bot.answer_callback_query(call.id)

# --- ADD CHANNEL LOGIC ---
def process_channel_id(message):
    try:
        ch_id = int(message.text)
        member = bot.get_chat_member(ch_id, bot.user.id)
        if member.status != 'administrator':
            bot.reply_to(message, "❌ Bot is channel me Admin nahi hai. Pehle admin banayein.")
            return
        
        chat = bot.get_chat(ch_id)
        link = chat.invite_link
        if not link:
            link = bot.export_chat_invite_link(ch_id)
            
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🔵 Primary", callback_data=f"color_{ch_id}_primary"),
            InlineKeyboardButton("🟢 Success", callback_data=f"color_{ch_id}_success"),
            InlineKeyboardButton("🔴 Danger", callback_data=f"color_{ch_id}_danger")
        )
            
        bot.reply_to(message, f"✅ Channel '{chat.title}' joined!\nAb color select karein:", reply_markup=markup)
        CHANNELS[ch_id] = {"url": link, "name": chat.title, "color": "primary"} 
    except Exception as e:
        bot.reply_to(message, f"❌ Error: ID galat hai ya bot admin nahi hai.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('color_'))
def save_color(call):
    if call.from_user.id != ADMIN_ID: return
    parts = call.data.split('_')
    ch_id, color_style = int(parts[1]), parts[2]
    if ch_id in CHANNELS:
        CHANNELS[ch_id]['color'] = color_style
        bot.edit_message_text(f"✅ Channel Added with {color_style} style!", call.message.chat.id, call.message.message_id)

# --- REMOVE CHANNEL LOGIC ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('del_'))
def delete_channel(call):
    if call.from_user.id != ADMIN_ID: return
    ch_id = int(call.data.split('_')[1])
    if ch_id in CHANNELS:
        del CHANNELS[ch_id]
        bot.edit_message_text("✅ Channel successfully removed!", call.message.chat.id, call.message.message_id)

# --- BROADCAST LOGIC (Mock) ---
def process_broadcast(message):
    bot.reply_to(message, "✅ Broadcast message received (Database connected nahi hai isliye send nahi hua).")

# ================== GETLINK FUNCTION ================== #

@bot.message_handler(commands=['getlink'])
def getlink_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    msg = bot.reply_to(message, "Send A Message For To Get Your Shareable Link 🔇")
    bot.register_next_step_handler(msg, process_getlink)

def process_getlink(message):
    # Video jaisa "processing..." effect
    proc_msg = bot.reply_to(message, "processing...")
    time.sleep(1)
    
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    GEN_LINKS[code] = {"message_id": message.message_id, "chat_id": message.chat.id}
    
    bot_info = bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={code}"
    
    # Share URL button jaise video me hai
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("↗️ SHARE URL", url=f"https://t.me/share/url?url={link}"))
    
    bot.delete_message(message.chat.id, proc_msg.message_id)
    bot.reply_to(message, f"Here is your link:\n\n{link}", reply_markup=markup, disable_web_page_preview=True)

# ================== USER FLOW ================== #

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
        markup.add(InlineKeyboardButton(text=f"Join {data['name']}", url=data['url'], style=data['color']))
    markup.add(InlineKeyboardButton("✅ Done !!", callback_data="check_join", style="success"))
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    payload = message.text.replace('/start', '').strip()
    if payload:
        USER_STATES[message.from_user.id] = payload

    caption = CAPTION_TEMPLATE.format(name=message.from_user.first_name)
    not_joined = check_user_joined(message.from_user.id)
    
    if len(not_joined) == 0:
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

# ================== FLASK SETUP ================== #
@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_bot():
    print("🤖 Bot Started Super Fast...")
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
