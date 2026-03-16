import os, time, re, requests
from playwright.sync_api import sync_playwright

# إعدادات البوت والـ VLESS
SSO_URL = os.environ.get("SSO_URL")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
USER_UUID = "36459fd0-0c89-4733-b20e-067ffc341bd2"
SNI_URL = "yt3.ggpht.com"

# بيانات البروكسي الخاص بك
PROXY_SERVER = "http://43.159.29.144:4950"
PROXY_USER = "Liopasio1AN0205-zone-abc-region-ci"
PROXY_PASS = "URgL1kHS56rN"

DEPLOY_CMD = "rm -rf gcp-v2ray && git clone https://github.com/AnimeHolic/gcp-v2ray.git && cd gcp-v2ray && sed -i 's|/TG-@Not_Ragnar|/|g' config.json && gcloud auth configure-docker -q && docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest . && docker push gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest && gcloud run deploy vless-app --image=gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest --port=8080 --region=us-central1 --allow-unauthenticated"

def send_tg(text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

def send_tg_photo(photo_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(photo_path, "rb") as photo:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": photo})

send_tg("🛡️ [GitHub] بدأت العملية.. جاري التخفي خلف البروكسي السكني!")

try:
    with sync_playwright() as p:
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
            time.sleep(10)
            
            # تخطي شاشة الترحيب
            try:
                for welcome_btn in ["I understand", "Accept", "Confirm", "موافق", "فهمت"]:
                    btn_loc = page.locator(f'button:has-text("{welcome_btn}")')
                    if btn_loc.is_visible():
                        btn_loc.click()
                        time.sleep(5)
            except:
                pass

            page.screenshot(path="after_welcome.png")
            send_tg_photo("after_welcome.png", "📸 تجاوزنا شاشة الترحيب! جاري الدخول للوحة التحكم...")
            
            # 2. الدخول لـ Cloud Shell
            page.goto("https://console.cloud.google.com/home/dashboard?cloudshell=true", wait_until="networkidle", timeout=60000)
            time.sleep(20)

            # تخطي النوافذ المنبثقة
            for btn in ["Continue", "Start", "Agree", "I agree", "No thanks", "Close"]:
                try: 
                    loc = page.locator(f'button:has-text("{btn}")')
                    if loc.is_visible():
                        loc.click(timeout=3000)
                except:
                    pass

            # انتظار شاشة الأوامر وحقن الكود
            page.wait_for_selector('.xterm-helper-textarea', timeout=60000)
            send_tg("🔥 [GitHub] تم كسر كل الحواجز! جاري حقن كود البناء...")
            
            page.locator('.xterm-helper-textarea').fill(DEPLOY_CMD)
            page.keyboard.press("Enter")
            
            time.sleep(200) 
            terminal = page.locator('.xterm-rows').inner_text()
            match = re.search(r'(https://vless-app-[a-zA-Z0-9-]+\.a\.run\.app)', terminal)
            
            if match:
                url_v = match.group(1).replace("https://", "")
                final_link = f"vless://{USER_UUID}@{SNI_URL}:443?encryption=none&security=tls&sni={SNI_URL}&type=ws&host={url_v}&path=%2F#Proxy-Power"
                send_tg(f"✅ انتصرنا! إليك السيرفر:\n\n`{final_link}`")
            else:
                page.screenshot(path="terminal_check.png")
                send_tg_photo("terminal_check.png", "⚠️ لم أجد الرابط في Terminal. انظر للصورة.")
                
        except Exception as inner_e:
            page.screenshot(path="error.png")
            send_tg_photo("error.png", f"❌ توقف المتصفح هنا:\n{str(inner_e)[:100]}")
        finally:
            browser.close()
except Exception as e:
    send_tg(f"❌ خطأ عام:\n{str(e)[:100]}")
