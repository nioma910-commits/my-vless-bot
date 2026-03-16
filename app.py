import socket, telebot, time, re
from playwright.sync_api import sync_playwright
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

BOT_TOKEN = "8259260611:AAGQeI886DxrlxdEJH749z5XvS1uvt25Ihs"
bot = telebot.TeleBot(BOT_TOKEN)
USER_UUID = "36459fd0-0c89-4733-b20e-067ffc341bd2"
SNI_URL = "yt3.ggpht.com"

# أمر الحقن في us-central1
DEPLOY_CMD = "rm -rf gcp-v2ray && git clone https://github.com/AnimeHolic/gcp-v2ray.git && cd gcp-v2ray && sed -i 's|/TG-@Not_Ragnar|/|g' config.json && gcloud auth configure-docker -q && docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest . && docker push gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest && gcloud run deploy vless-app --image=gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest --port=8080 --region=us-central1 --allow-unauthenticated"

app = Flask(__name__)

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode("utf-8"))])
    return "OK", 200

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "أرسل رابط المختبر (SSO) وسأحاول الدخول كبشري لتجاوز الحماية!")

@bot.message_handler(func=lambda m: "google_sso" in m.text)
def handle_link(message):
    url = message.text
    cid = message.chat.id
    bot.send_message(cid, "⏳ جاري التسلل لداخل جوجل... راقب الصور.")

    try:
        with sync_playwright() as p:
            # محاكاة متصفح حقيقي 100%
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={'width': 1366, 'height': 768},
                device_scale_factor=1,
                is_mobile=False,
                has_touch=False,
                locale="en-US",
                timezone_id="America/New_York"
            )
            page = context.new_page()
            
            # الدخول الهادئ
            page.goto(url, wait_until="networkidle", timeout=60000)
            time.sleep(5)
            
            # التوجه لـ Cloud Shell
            page.goto("https://console.cloud.google.com/home/dashboard?cloudshell=true")
            time.sleep(15)
            
            # تخطي النوافذ (استخدام evaluate ليكون الضغط "بشرياً")
            for btn in ["Continue", "Start", "متابعة", "Agree"]:
                try: page.locator(f'button:has-text("{btn}")').evaluate("node => node.click()")
                except: pass

            try:
                page.wait_for_selector('.xterm-helper-textarea', timeout=90000)
                bot.send_message(cid, "🚀 نجحت في العبور! جاري بناء السيرفر...")
                
                page.locator('.xterm-helper-textarea').fill(DEPLOY_CMD)
                page.keyboard.press("Enter")
                
                time.sleep(170)
                terminal = page.locator('.xterm-rows').inner_text()
                match = re.search(r'(https://vless-app-[a-zA-Z0-9-]+\.a\.run\.app)', terminal)
                
                if match:
                    url_v = match.group(1).replace("https://", "")
                    bot.send_message(cid, f"🎉 تفضل سيرفرك:\n`vless://{USER_UUID}@{SNI_URL}:443?encryption=none&security=tls&sni={SNI_URL}&type=ws&host={url_v}&path=%2F#Auto`", parse_mode='Markdown')
                else:
                    page.screenshot(path="fail.png")
                    with open("fail.png", "rb") as f: bot.send_photo(cid, f, caption="⚠️ لم أجد الرابط في الشاشة.")
            except:
                page.screenshot(path="err.png")
                with open("err.png", "rb") as f: bot.send_photo(cid, f, caption="❌ توقفت عند هذه النقطة.")
            
            browser.close()
    except Exception as e:
        bot.send_message(cid, f"❌ حدث خطأ: {str(e)[:50]}")

if __name__ == "__main__":
    # هذا التعديل يسمح للبوت بالعمل بنظام Polling في حال لم تفعل الـ Webhook
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=7860)).start()
    bot.infinity_polling()
