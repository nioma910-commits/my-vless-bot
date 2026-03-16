import os, telebot, requests, socket, threading
from flask import Flask, request

# تجاوز حظر DNS لتيليجرام
old_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(*args, **kwargs):
    if args and args[0] == 'api.telegram.org':
        new_args = list(args)
        new_args[0] = '149.154.167.220'
        return old_getaddrinfo(*new_args, **kwargs)
    return old_getaddrinfo(*args, **kwargs)
socket.getaddrinfo = patched_getaddrinfo

# توكن البوت الخاص بك
BOT_TOKEN = "8259260611:AAGQeI886DxrlxdEJH749z5XvS1uvt25Ihs"
bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# استدعاء توكن جيت هاب المخفي من إعدادات Render بشكل آمن
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USERNAME = "nioma910-commits"
GITHUB_REPO = "my-vless-bot" # ⚠️ تذكر تغيير هذه باسم مستودعك فقط
# ==========================================

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running perfectly!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أهلاً بك يا بطل! أرسل رابط المختبر (SSO) وسأرسله فوراً لخوادم GitHub لتبدأ في بناء السيرفر.")

@bot.message_handler(func=lambda m: "google_sso" in m.text)
def handle_link(message):
    sso_url = message.text
    chat_id = message.chat.id
    
    # التأكد من وجود التوكن
    if not GITHUB_TOKEN:
        bot.send_message(chat_id, "❌ خطأ: لم يتم العثور على GITHUB_TOKEN. تأكد من إضافته في إعدادات Render.")
        return

    # رابط الـ API الخاص بـ GitHub لتشغيل الأوامر
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/actions/workflows/deploy.yml/dispatches"
    
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # إرسال الرابط كمدخل (Input) لخوادم GitHub
    data = {
        "ref": "main",  # تأكد أن الفرع الأساسي في مستودعك اسمه main
        "inputs": {"sso_url": sso_url}
    }
    
    try:
        bot.send_message(chat_id, "⏳ تم استلام الرابط، جاري إعطاء الأوامر لخوادم GitHub...")
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 204:
            bot.send_message(chat_id, "✅ وافقت خوادم GitHub على المهمة وبدأت العمل الآن! \nيمكنك إغلاق الهاتف، ستصلك رسالة جديدة قريباً تحتوي على رابط VLESS الجاهز.")
        else:
            bot.send_message(chat_id, f"❌ رفضت GitHub الطلب. كود الخطأ: {response.status_code}\n{response.text}")
    except Exception as e:
        bot.send_message(chat_id, f"❌ حدث خطأ في الاتصال: {str(e)}")

if __name__ == "__main__":
    bot.remove_webhook()
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=7860)).start()
    bot.infinity_polling()
