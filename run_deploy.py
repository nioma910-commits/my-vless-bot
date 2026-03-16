import os, time, re, requests
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# إعدادات البوت
SSO_URL = os.environ.get("SSO_URL")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
USER_UUID = "36459fd0-0c89-4733-b20e-067ffc341bd2"
SNI_URL = "yt3.ggpht.com"

# البروكسي الأمريكي السكني
PROXY_SERVER = "http://43.159.29.144:4950"
PROXY_USER = "Liopasio1AN0205-zone-abc-region-us"
PROXY_PASS = "URgL1kHS56rN"

DEPLOY_CMD = "rm -rf gcp-v2ray && git clone https://github.com/AnimeHolic/gcp-v2ray.git && cd gcp-v2ray && sed -i 's|/TG-@Not_Ragnar|/|g' config.json && gcloud auth configure-docker -q && docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest . && docker push gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest && gcloud run deploy vless-app --image=gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest --port=8080 --region=us-central1 --allow-unauthenticated"

# 🛠️ دالة الإرسال المعدلة (لإيقاف الـ Markdown وقت الأخطاء)
def send_tg(text, markdown=True):
    payload = {"chat_id": CHAT_ID, "text": text}
    if markdown:
        payload["parse_mode"] = "Markdown"
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)
    except: pass

def send_tg_photo(photo_path, caption):
    if os.path.exists(photo_path):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(photo_path, "rb") as photo:
            requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": photo})

def safe_screenshot(page, path, caption):
    try:
        page.screenshot(path=path, timeout=8000)
        send_tg_photo(path, caption)
    except Exception:
        send_tg(f"⚠️ تجاوزت التقاط الصورة ({caption}) لأجل إكمال المهمة بسرعة.")

send_tg("🥷 [GitHub] انطلاق المتصفح الشبح (تم إصلاح نظام الاتصال)...")

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            proxy={
                "server": PROXY_SERVER,
                "username": PROXY_USER,
                "password": PROXY_PASS
            },
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1366, 'height': 768}
        )
        
        page = context.new_page()
        stealth_sync(page) 
        
        try:
            page.goto(SSO_URL, wait_until="networkidle", timeout=90000)
            time.sleep(10)
            
            try:
                for btn_txt in ["I understand", "Accept", "Agree"]:
                    if page.locator(f'button:has-text("{btn_txt}")').is_visible():
                        page.locator(f'button:has-text("{btn_txt}")').click()
                        time.sleep(5)
            except: pass

            safe_screenshot(page, "stealth_step1.png", "📸 تجاوز المرحلة الأولى")
            
            page.goto("https://console.cloud.google.com/home/dashboard?cloudshell=true", wait_until="networkidle", timeout=90000)
            time.sleep(20)

            try:
                checkboxes = page.locator('mat-checkbox, input[type="checkbox"]')
                for i in range(checkboxes.count()):
                    try: checkboxes.nth(i).click(timeout=3000)
                    except: pass
                
                for btn_txt in ["Agree and continue", "Agree & Continue", "Authorize", "Start Cloud Shell", "Continue"]:
                    buttons = page.locator(f'button:has-text("{btn_txt}"), span:has-text("{btn_txt}")')
                    for i in range(buttons.count()):
                        try:
                            if buttons.nth(i).is_visible():
                                buttons.nth(i).click(timeout=3000)
                                time.sleep(4)
                        except: pass
            except: pass

            page.wait_for_selector('.xterm-helper-textarea', timeout=60000)
            send_tg("🔥 تم الاختراق بنجاح! جاري بناء السيرفر (انتظر 3 دقائق)...")
            
            page.locator('.xterm-helper-textarea').fill(DEPLOY_CMD)
            page.keyboard.press("Enter")
            
            time.sleep(210) 
            
            terminal_text = page.locator('.xterm-rows').inner_text()
            match = re.search(r'(https://vless-app-[a-zA-Z0-9-]+\.a\.run\.app)', terminal_text)
            
            if match:
                url_v = match.group(1).replace("https://", "")
                final_link = f"vless://{USER_UUID}@{SNI_URL}:443?encryption=none&security=tls&sni={SNI_URL}&type=ws&host={url_v}&path=%2F#Stealth-Bot"
                send_tg(f"✅ تمت المهمة بنجاح أسطوري:\n\n`{final_link}`")
            else:
                safe_screenshot(page, "fail.png", "⚠️ لم أجد الرابط.")
                
        except Exception as inner_e:
            safe_screenshot(page, "error.png", "❌ توقف البوت")
            # 🌟 هنا أوقفنا الماركداون لتصلك الرسالة رغماً عن تيليجرام
            send_tg(f"❌ تفاصيل الخطأ:\n{str(inner_e)[:200]}", markdown=False)
        finally:
            browser.close()
except Exception as e:
    send_tg(f"❌ خطأ عام:\n{str(e)[:200]}", markdown=False)
