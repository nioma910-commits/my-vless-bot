import os, time, re, requests
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# إعدادات ثابتة
SSO_URL = os.environ.get("SSO_URL")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
USER_UUID = "36459fd0-0c89-4733-b20e-067ffc341bd2"
SNI_URL = "yt3.ggpht.com"

# أمر الحقن والبناء
DEPLOY_CMD = "rm -rf gcp-v2ray && git clone https://github.com/AnimeHolic/gcp-v2ray.git && cd gcp-v2ray && sed -i 's|/TG-@Not_Ragnar|/|g' config.json && gcloud auth configure-docker -q && docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest . && docker push gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest && gcloud run deploy vless-app --image=gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest --port=8080 --region=us-central1 --allow-unauthenticated"

def send_tg(text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": text})

send_tg("🚀 وضع الصبر الأقصى: سننتظر الشاشة السوداء لمدة 220 ثانية...")

try:
    with sync_playwright() as p:
        # تشغيل مباشر بدون بروكسي لضمان السرعة وتجنب الـ Timeout
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        page = context.new_page()
        stealth_sync(page) 
        
        try:
            # دخول سريع
            page.goto(SSO_URL, wait_until="domcontentloaded", timeout=60000)
            time.sleep(10)
            
            # محاولة تخطي أزرار الموافقة الأولية
            for btn_txt in ["I understand", "Accept", "Agree", "Continue"]:
                try:
                    target = page.locator(f'button:has-text("{btn_txt}")').first
                    if target.is_visible(): target.click(); time.sleep(4)
                except: pass

            # التوجه للوحة التحكم والـ Cloud Shell
            page.goto("https://console.cloud.google.com/home/dashboard?cloudshell=true", wait_until="domcontentloaded", timeout=60000)
            time.sleep(15)

            # الموافقة على شروط الخدمة (Checkbox)
            try:
                page.locator('mat-checkbox, input[type="checkbox"]').first.click(timeout=5000)
                time.sleep(2)
            except: pass

            # ضغط متكرر على أزرار التأكيد لفتح الـ Terminal
            for _ in range(3):
                for btn_txt in ["Agree and continue", "Authorize", "Start Cloud Shell", "Start", "Continue", "Allow", "Confirm"]:
                    try:
                        target = page.locator(f"text={btn_txt}").first
                        if target.is_visible(): target.click(); time.sleep(4)
                    except: pass
                time.sleep(5)

            # ⏳ الانتظار الأسطوري: 220 ثانية لظهور منطقة الأوامر
            page.wait_for_selector('.xterm-helper-textarea', timeout=220000)
            send_tg("🔥 تم فتح الـ Terminal بنجاح! جاري البناء النهائي...")
            
            # حقن الأمر
            page.locator('.xterm-helper-textarea').fill(DEPLOY_CMD)
            page.keyboard.press("Enter")
            
            # وقت البناء (4 دقائق)
            time.sleep(240) 
            
            # قراءة المخرجات واستخراج الرابط
            terminal_text = page.locator('.xterm-rows').inner_text()
            match = re.search(r'(https://vless-app-[a-zA-Z0-9-]+\.a\.run\.app)', terminal_text)
            
            if match:
                url_v = match.group(1).replace("https://", "")
                final_link = f"vless://{USER_UUID}@{SNI_URL}:443?encryption=none&security=tls&sni={SNI_URL}&type=ws&host={url_v}&path=%2F#Patient-Bot-Success"
                send_tg(f"✅ مبروك يا بطل! السيرفر جاهز أخيراً:\n\n`{final_link}`")
            else:
                send_tg("⚠️ انتهى البناء لكن لم أجد الرابط. ربما حدث خطأ في gcloud.")
                
        except Exception as inner_e:
            send_tg(f"❌ توقف البوت عند مرحلة الانتظار: {str(inner_e)[:150]}")
        finally:
            browser.close()
except Exception as e:
    send_tg(f"❌ خطأ عام: {str(e)[:150]}")
