import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import concurrent.futures

# --- إعدادات البوت ---
TOKEN = "8453581286:AAH208gsL3-fCONSIbwPlOPL6luYLIA6QK4" # ضع توكن البوت الخاص بك هنا
bot = telebot.TeleBot(TOKEN)

# قاموس لتخزين البروكسيات مؤقتاً لكل مستخدم حتى يختار النوع
user_proxies = {}

def check_single_proxy(proxy_str, proxy_type):
    """
    تقوم هذه الدالة بفحص بروكسي واحد بناءً على النوع الذي حدده المستخدم.
    """
    proxies = {
        'http': f"{proxy_type}://{proxy_str}",
        'https': f"{proxy_type}://{proxy_str}"
    }
    
    # استخدام User-Agent لمحاكاة متصفح حقيقي وتجنب الحظر التلقائي
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        # فحص الاتصال بجوجل (مهلة 5 ثوانٍ)
        response = requests.get("https://www.google.com", proxies=proxies, headers=headers, timeout=5)
        
        if response.status_code == 200:
            return f"✅ {proxy_str} | يعمل بكفاءة | غير محظور"
        elif response.status_code in [429, 403]:
            return f"⚠️ {proxy_str} | يعمل | محظور من جوجل (Captcha/Blocked)"
        else:
            return f"❓ {proxy_str} | يعمل | كود استجابة: {response.status_code}"
            
    except Exception:
        return f"❌ {proxy_str} | لا يعمل (Dead)"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في أداة فحص البروكسيات 🕵️‍♂️\n\nأرسل لي البروكسيات بصيغة ip:port (كل بروكسي في سطر)، وسأعطيك خيارات لتحديد نوعها قبل الفحص.", parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_proxies_text(message):
    # استخراج البروكسيات من النص
    lines = message.text.split('\n')
    proxies = [line.strip() for line in lines if ':' in line]
    
    if not proxies:
        bot.reply_to(message, "لم أتمكن من العثور على بروكسيات. يرجى التأكد من إرسالها بصيغة ip:port.")
        return
        
    # حفظ البروكسيات مؤقتاً برقم تعريف المستخدم
    chat_id = message.chat.id
    user_proxies[chat_id] = proxies
    
    # إنشاء أزرار اختيار نوع البروكسي
    markup = InlineKeyboardMarkup()
    markup.row_width = 3
    markup.add(
        InlineKeyboardButton("SOCKS5", callback_data="socks5"),
        InlineKeyboardButton("SOCKS4", callback_data="socks4"),
        InlineKeyboardButton("HTTP/HTTPS", callback_data="http")
    )
    
    bot.reply_to(message, f"تم استلام {len(proxies)} بروكسي. \nالرجاء اختيار نوعها لبدء الفحص:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_proxy_type_selection(call):
    chat_id = call.message.chat.id
    proxy_type = call.data # سيحمل القيمة: socks5, socks4, أو http
    
    # التحقق مما إذا كانت بيانات المستخدم لا تزال موجودة
    if chat_id not in user_proxies:
        bot.answer_callback_query(call.id, "عذراً، انتهت الجلسة. أرسل البروكسيات مجدداً.")
        return
        
    proxies = user_proxies[chat_id]
    
    # تعديل الرسالة لإظهار أن الفحص قد بدأ
    bot.edit_message_text(f"⏳ جاري فحص {len(proxies)} بروكسي كـ {proxy_type.upper()}... يرجى الانتظار.", chat_id=chat_id, message_id=call.message.message_id, parse_mode="Markdown")
    
    results = []
    # فحص متزامن لتسريع العملية
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(check_single_proxy, p, proxy_type) for p in proxies]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            
    # مسح البروكسيات من الذاكرة المؤقتة بعد انتهاء الفحص
    del user_proxies[chat_id]
    
    # تجميع وإرسال التقرير النهائي
    final_report = f"📊 نتائج فحص ({proxy_type.upper()}):\n\n" + "\n".join(results)
    
    if len(final_report) > 4000:
        for i in range(0, len(final_report), 4000):
            bot.send_message(chat_id, final_report[i:i+4000], parse_mode="Markdown")
    else:
        bot.send_message(chat_id, final_report, parse_mode="Markdown")
