import os, time, re
import telebot
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# --- إعدادات البوت ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ضع_توكن_البوت_هنا") # يمكنك وضع التوكن هنا مباشرة بين علامتي التنصيص
USER_UUID = "36459fd0-0c89-4733-b20e-067ffc341bd2"
SNI_URL = "yt3.ggpht.com"

# أمر البناء السريع والاختصار الذي جلبته
DEPLOY_CMD = "bash <(curl -Ls https://raw.githubusercontent.com/nyeinkokoaung404/gcp-v2ray/refs/heads/main/cloud-run.sh)"

# 🌐 البروكسي الذي اخترته
PROXY_SERVER = "http://35.183.64.191:10043"

bot = telebot.TeleBot(BOT_TOKEN)

print("🤖 البوت متصل ومستعد لاستقبال رابط SSO...")

@bot.message_handler(func=lambda message: "skills.google/google_sso" in message.text)
def handle_sso_link(message):
    sso_url = message.text.strip()
    chat_id = message.chat.id
    
    bot.send_message(chat_id, "🚀 استلمت الرابط. جاري التنفيذ بطريقة الحقن السريع لتخطي الواجهة...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                proxy={"server": PROXY_SERVER},
                args=["--disable-blink-features=AutomationControlled", "--ignore-certificate-errors", "--no-sandbox"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                ignore_https_errors=True
            )
            page = context.new_page()
            stealth_sync(page) 
            
            # 1. الدخول السريع للرابط
            page.goto(sso_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(6)
            
            # حقن جافا سكربت لتخطي أي شاشة موافقة أولية فوراً
            page.evaluate('''() => {
                const btns = Array.from(document.querySelectorAll('button'));
                const target = btns.find(b => b.innerText.includes('understand') || b.innerText.includes('Accept'));
                if(target) target.click();
            }''')
            time.sleep(3)

            # 2. القفز مباشرة إلى رابط التيرمينال
            page.goto("https://console.cloud.google.com/home/dashboard?cloudshell=true", wait_until="domcontentloaded", timeout=60000)
            time.sleep(10)

            # حقن جافا سكربت للموافقة على شروط جوجل كلاود وتشغيل الشاشة
            page.evaluate('''() => {
                const checkbox = document.querySelector('mat-checkbox, input[type="checkbox"]');
                if(checkbox) checkbox.click();
                setTimeout(() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const agreeBtn = btns.find(b => b.innerText.includes('Agree') || b.innerText.includes('Start'));
                    if(agreeBtn) agreeBtn.click();
                }, 1000);
            }''')

            # 3. انتظار الشاشة السوداء وحقن الأمر
            page.wait_for_selector('.xterm-helper-textarea', timeout=90000)
            bot.send_message(chat_id, "🔥 تم تخطي حماية الواجهة بنجاح! جاري حقن كود البناء السريع (انتظر 4 دقائق)...")
            
            page.locator('.xterm-helper-textarea').fill(DEPLOY_CMD)
            page.keyboard.press("Enter")
            
            # انتظار انتهاء السكربت من العمل
            time.sleep(220) 
            terminal_text = page.locator('.xterm-rows').inner_text()
            match = re.search(r'(https://vless-app-[a-zA-Z0-9-]+\.a\.run\.app)', terminal_text)
            
            if match:
                url_v = match.group(1).replace("https://", "")
                final_link = f"vless://{USER_UUID}@{SNI_URL}:443?encryption=none&security=tls&sni={SNI_URL}&type=ws&host={url_v}&path=%2F"
                bot.send_message(chat_id, f"✅ السيرفر جاهز للعمل مع تطبيق Dark Tunnel:\n\n`{final_link}`", parse_mode="Markdown")
            else:
                bot.send_message(chat_id, "⚠️ اكتمل البناء لكن لم أتمكن من استخراج الرابط من الشاشة.")
            
            browser.close()
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ حدث خطأ أو انتهى وقت البروكسي:\n{str(e)[:150]}")

bot.polling(none_stop=True)
