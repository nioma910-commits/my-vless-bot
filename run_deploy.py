import os, time, re, requests, random
from playwright.sync_api import sync_playwright

# إعدادات البوت والـ VLESS
SSO_URL = os.environ.get("SSO_URL")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
USER_UUID = "36459fd0-0c89-4733-b20e-067ffc341bd2"
SNI_URL = "yt3.ggpht.com"

# بيانات البروكسي الأمريكي (US)
PROXY_SERVER = "http://43.159.29.144:4950"
PROXY_USER = "Liopasio1AN0205-zone-abc-region-us"
PROXY_PASS = "URgL1kHS56rN"

# أمر بناء السيرفر
DEPLOY_CMD = "rm -rf gcp-v2ray && git clone https://github.com/AnimeHolic/gcp-v2ray.git && cd gcp-v2ray && sed -i 's|/TG-@Not_Ragnar|/|g' config.json && gcloud auth configure-docker -q && docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest . && docker push gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest && gcloud run deploy vless-app --image=gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest --port=8080 --region=us-central1 --allow-unauthenticated"

def send_tg(text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

def send_tg_photo(photo_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(photo_path, "rb") as photo:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": photo})

send_tg("🚀 [GitHub] انطلاق العملية النهائية! جاري تجاوز حواجز جوجل بالبروكسي الأمريكي...")

try:
    with sync_playwright() as p:
        # تشغيل المتصفح بنمط Desktop مع البروكسي
        browser = p.firefox.launch(
            headless=True,
            proxy={
                "server": PROXY_SERVER,
                "username": PROXY_USER,
                "password": PROXY_PASS
            }
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            viewport={'width': 1366, 'height': 768}
        )
        page = context.new_page()
        
        try:
            # 1. التوجه للرابط
            page.goto(SSO_URL, wait_until="networkidle", timeout=90000)
            time.sleep(12)
            
            # تخطي شاشة الترحيب الأولية
            try:
                for btn_txt in ["I understand", "Accept", "Confirm", "Agree", "Continue"]:
                    btn = page.locator(f'button:has-text("{btn_txt}")')
                    if btn.is_visible():
                        btn.click()
                        time.sleep(5)
            except: pass

            # 2. الدخول لـ Cloud Shell مباشرة
            page.goto("https://console.cloud.google.com/home/dashboard?cloudshell=true", wait_until="networkidle", timeout=90000)
            time.sleep(25)
            
            page.screenshot(path="bypass_check.png")
            send_tg_photo("bypass_check.png", "📸 جاري محاولة تجاوز نوافذ الموافقة والتخويل...")

            # --- تخطي النوافذ (شروط الخدمة + Authenticator) ---
            try:
                # الضغط على Checkbox الموافقة
                checkboxes = page.locator('mat-checkbox, input[type="checkbox"]')
                for i in range(checkboxes.count()):
                    try: checkboxes.nth(i).click(timeout=3000)
                    except: pass
                
                # الضغط على أزرار الموافقة والتخويل
                for btn_txt in ["Agree and continue", "Agree & Continue", "Authorize", "Authenticate", "Allow", "Start", "Continue"]:
                    buttons = page.locator(f'button:has-text("{btn_txt}"), span:has-text("{btn_txt}")')
                    for i in range(buttons.count()):
                        try:
                            if buttons.nth(i).is_visible():
                                buttons.nth(i).click(timeout=3000)
                                time.sleep(4)
                        except: pass
            except: pass

            # 3. انتظار شاشة الأوامر Terminal
            page.wait_for_selector('.xterm-helper-textarea', timeout=60000)
            send_tg("🔥 [GitHub] تم الوصول للـ Terminal بنجاح! جاري حقن الأوامر...")
            
            page.locator('.xterm-helper-textarea').fill(DEPLOY_CMD)
            page.keyboard.press("Enter")
            
            # انتظار البناء (3 دقائق ونصف)
            time.sleep(210) 
            
            terminal_text = page.locator('.xterm-rows').inner_text()
            match = re.search(r'(https://vless-app-[a-zA-Z0-9-]+\.a\.run\.app)', terminal_text)
            
            if match:
                url_v = match.group(1).replace("https://", "")
                final_link = f"vless://{USER_UUID}@{SNI_URL}:443?encryption=none&security=tls&sni={SNI_URL}&type=ws&host={url_v}&path=%2F#Full-Auto-Success"
                send_tg(f"✅ مبروك! العملية تمت بنجاح تام:\n\n`{final_link}`")
            else:
                page.screenshot(path="terminal_final.png")
                send_tg_photo("terminal_final.png", "⚠️ انتهى الوقت ولم أجد الرابط. تفحص صورة الشاشة.")
                
        except Exception as inner_e:
            page.screenshot(path="error_log.png")
            send_tg_photo("error_log.png", f"❌ توقف البوت هنا:\n{str(inner_e)[:100]}")
        finally:
            browser.close()
except Exception as e:
    send_tg(f"❌ خطأ عام:\n{str(e)[:100]}")
