import os, time, re, requests
from playwright.sync_api import sync_playwright

SSO_URL = os.environ.get("SSO_URL")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
USER_UUID = "36459fd0-0c89-4733-b20e-067ffc341bd2"
SNI_URL = "yt3.ggpht.com"

DEPLOY_CMD = "rm -rf gcp-v2ray && git clone https://github.com/AnimeHolic/gcp-v2ray.git && cd gcp-v2ray && sed -i 's|/TG-@Not_Ragnar|/|g' config.json && gcloud auth configure-docker -q && docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest . && docker push gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest && gcloud run deploy vless-app --image=gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest --port=8080 --region=us-central1 --allow-unauthenticated"

def send_tg(text):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})

def send_tg_photo(photo_path, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(photo_path, "rb") as photo:
        requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"photo": photo})

send_tg("🚀 [GitHub] استلمت الرابط.. جاري فتح المتصفح والدخول لجوجل...")

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1366, 'height': 768}
        )
        page = context.new_page()
        
        try:
            # 1. التوجه للرابط
            page.goto(SSO_URL, wait_until="networkidle", timeout=60000)
            time.sleep(10) # انتظار التحويلات
            
            # التقاط الصورة الأولى
            page.screenshot(path="sso_step.png")
            send_tg_photo("sso_step.png", "📸 1. حالة المتصفح بعد فتح رابط SSO")
            
            # 2. القفز لـ Cloud Shell
            page.goto("https://console.cloud.google.com/home/dashboard?cloudshell=true", wait_until="networkidle", timeout=60000)
            time.sleep(15)
            
            # التقاط الصورة الثانية
            page.screenshot(path="dashboard_step.png")
            send_tg_photo("dashboard_step.png", "📸 2. حالة المتصفح داخل لوحة التحكم")

            # محاولة تخطي نافذة شروط الاستخدام (الشائعة في المختبرات)
            try: 
                page.locator('mat-checkbox').click(timeout=3000)
                page.locator('button:has-text("Agree and continue")').click(timeout=3000)
            except: pass

            for btn in ["Continue", "Start", "متابعة", "Agree", "I agree", "No thanks", "Got it"]:
                try: page.locator(f'button:has-text("{btn}")').click(timeout=3000)
                except: pass

            # انتظار شاشة الأوامر
            page.wait_for_selector('.xterm-helper-textarea', timeout=40000)
            send_tg("✅ [GitHub] تم التسلل لـ Cloud Shell بنجاح! جاري بناء السيرفر (انتظر 3 دقائق)...")
            
            # حقن الكود
            page.locator('.xterm-helper-textarea').fill(DEPLOY_CMD)
            page.keyboard.press("Enter")
            
            # انتظار البناء واستخراج الرابط
            time.sleep(180)
            terminal = page.locator('.xterm-rows').inner_text()
            match = re.search(r'(https://vless-app-[a-zA-Z0-9-]+\.a\.run\.app)', terminal)
            
            if match:
                url_v = match.group(1).replace("https://", "")
                final_link = f"vless://{USER_UUID}@{SNI_URL}:443?encryption=none&security=tls&sni={SNI_URL}&type=ws&host={url_v}&path=%2F#Auto-GitHub"
                send_tg(f"🎉 تمت المهمة بنجاح! تفضل سيرفرك:\n\n`{final_link}`")
            else:
                page.screenshot(path="fail.png")
                send_tg_photo("fail.png", "⚠️ [GitHub] اكتمل البناء لكن لم أجد الرابط.")
                
        except Exception as inner_e:
            page.screenshot(path="error.png")
            send_tg_photo("error.png", f"❌ [GitHub] توقف المتصفح هنا! انظر للصورة:\n{str(inner_e)[:100]}")
        finally:
            browser.close()
except Exception as e:
    send_tg(f"❌ [GitHub] خطأ عام:\n{str(e)[:100]}")
