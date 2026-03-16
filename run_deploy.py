import os, time, re, requests, random
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

send_tg("📱 [GitHub] جاري بدء العملية بمحاكاة متصفح أندرويد لتمويه جوجل...")

try:
    with sync_playwright() as p:
        # تشغيل المتصفح مع البروكسي
        browser = p.firefox.launch(
            headless=True,
            proxy={
                "server": PROXY_SERVER,
                "username": PROXY_USER,
                "password": PROXY_PASS
            }
        )
        
        # محاكاة هاتف أندرويد (تغيير الهوية لتقليل الحظر)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
            viewport={'width': 360, 'height': 800},
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()
        
        try:
            # 1. التوجه للرابط
            page.goto(SSO_URL, wait_until="networkidle", timeout=90000)
            time.sleep(random.uniform(7.0, 12.0)) # انتظار عشوائي
            
            # تخطي شاشة الترحيب (I understand)
            try:
                for welcome_btn in ["I understand", "Accept", "Confirm", "موافق", "فهمت", "Continue"]:
                    btn_loc = page.locator(f'button:has-text("{welcome_btn}")')
                    if btn_loc.is_visible():
                        btn_loc.click()
                        time.sleep(random.uniform(4.0, 6.0))
            except:
                pass

            page.screenshot(path="step_1.png")
            send_tg_photo("step_1.png", "📸 تجاوزنا المرحلة الأولى.. جاري التوجه للوحة التحكم")
            
            # 2. الدخول لـ Cloud Shell مباشرة
            page.goto("https://console.cloud.google.com/home/dashboard?cloudshell=true", wait_until="networkidle", timeout=90000)
            time.sleep(random.uniform(15.0, 25.0))

            # تخطي النوافذ المنبثقة في لوحة التحكم
            for btn in ["Continue", "Start", "Agree", "I agree", "No thanks", "Close"]:
                try: 
                    loc = page.locator(f'button:has-text("{btn}")')
                    if loc.is_visible():
                        loc.click(timeout=3000)
                        time.sleep(3)
                except:
                    pass

            # انتظار شاشة الأوامر (Terminal)
            page.wait_for_selector('.xterm-helper-textarea', timeout=60000)
            send_tg("🔥 [GitHub] تم فتح الـ Terminal بنجاح! جاري البدء بالبناء...")
            
            # حقن كود البناء
            page.locator('.xterm-helper-textarea').fill(DEPLOY_CMD)
            page.keyboard.press("Enter")
            
            # انتظار انتهاء العملية (3 دقائق ونصف)
            time.sleep(210) 
            
            terminal_text = page.locator('.xterm-rows').inner_text()
            match = re.search(r'(https://vless-app-[a-zA-Z0-9-]+\.a\.run\.app)', terminal_text)
            
            if match:
                url_v = match.group(1).replace("https://", "")
                final_link = f"vless://{USER_UUID}@{SNI_URL}:443?encryption=none&security=tls&sni={SNI_URL}&type=ws&host={url_v}&path=%2F#Android-Spoof-Success"
                send_tg(f"✅ تم الاختراق بنجاح! إليك الرابط:\n\n`{final_link}`")
            else:
                page.screenshot(path="terminal_fail.png")
                send_tg_photo("terminal_fail.png", "⚠️ اكتمل الوقت ولم أجد الرابط. ربما فشل البناء أو الـ IP محظور.")
                
        except Exception as inner_e:
            page.screenshot(path="error.png")
            send_tg_photo("error.png", f"❌ توقف البوت:\n{str(inner_e)[:100]}")
        finally:
            browser.close()
except Exception as e:
    send_tg(f"❌ خطأ تقني:\n{str(e)[:100]}")
