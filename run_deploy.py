import os, time, re, requests
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# إعدادات
SSO_URL = os.environ.get("SSO_URL")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
USER_UUID = "36459fd0-0c89-4733-b20e-067ffc341bd2"
SNI_URL = "yt3.ggpht.com"

PROXY_SERVER = "http://43.159.29.144:4950"
PROXY_USER = "Liopasio1AN0205-zone-abc-region-fr"
PROXY_PASS = "URgL1kHS56rN"

DEPLOY_CMD = "rm -rf gcp-v2ray && git clone https://github.com/AnimeHolic/gcp-v2ray.git && cd gcp-v2ray && sed -i 's|/TG-@Not_Ragnar|/|g' config.json && gcloud auth configure-docker -q && docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest . && docker push gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest && gcloud run deploy vless-app --image=gcr.io/$GOOGLE_CLOUD_PROJECT/anime-vless:latest --port=8080 --region=us-central1 --allow-unauthenticated"

def send_tg(text, markdown=False):
    payload = {"chat_id": CHAT_ID, "text": text}
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json=payload)
    except: pass

# 🛡️ منع تحميل الصور والملفات الثقيلة لتسريع البروكسي
def block_heavy_resources(route):
    if route.request.resource_type in ["image", "font", "media", "stylesheet"]:
        route.abort()
    else:
        route.continue_()

send_tg("⚠️ وضع الطوارئ: تم تعطيل الصور والخطوط لتسريع التحميل...")

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            proxy={"server": PROXY_SERVER, "username": PROXY_USER, "password": PROXY_PASS},
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()
        
        # تفعيل منع الموارد الثقيلة
        page.route("**/*", block_heavy_resources)
        stealth_sync(page) 
        
        try:
            # الانتقال فور بدء الاستجابة (wait_until="commit")
            page.goto(SSO_URL, wait_until="commit", timeout=120000)
            time.sleep(15) # انتظار يدوي بسيط بدلاً من انتظار الشبكة
            
            # محاولة الضغط على الأزرار حتى لو الصفحة لم تكتمل
            for btn_txt in ["I understand", "Accept", "Agree", "Continue"]:
                try:
                    btn = page.get_by_role("button", name=btn_txt, exact=False)
                    if btn.is_visible(): btn.click(); time.sleep(5)
                except: pass

            # القفز للوحة التحكم
            page.goto("https://console.cloud.google.com/home/dashboard?cloudshell=true", wait_until="commit", timeout=120000)
            time.sleep(20)

            # تخطي النوافذ
            for btn_txt in ["Agree and continue", "Authorize", "Start Cloud Shell", "Continue", "Allow"]:
                try:
                    target = page.locator(f"text={btn_txt}")
                    if target.is_visible(): target.click(); time.sleep(4)
                except: pass

            # انتظار الشاشة السوداء
            page.wait_for_selector('.xterm-helper-textarea', timeout=60000)
            send_tg("🔥 تم الوصول للـ Terminal! جاري البناء...")
            
            page.locator('.xterm-helper-textarea').fill(DEPLOY_CMD)
            page.keyboard.press("Enter")
            
            time.sleep(210) 
            terminal_text = page.locator('.xterm-rows').inner_text()
            match = re.search(r'(https://vless-app-[a-zA-Z0-9-]+\.a\.run\.app)', terminal_text)
            
            if match:
                url_v = match.group(1).replace("https://", "")
                send_tg(f"✅ تمت المهمة بنجاح:\n\n vless://{USER_UUID}@yt3.ggpht.com:443?encryption=none&security=tls&sni=yt3.ggpht.com&type=ws&host={url_v}&path=%2F#Stealth-US")
            else:
                send_tg("⚠️ لم يتم العثور على الرابط في المخرجات.")
                
        except Exception as inner_e:
            send_tg(f"❌ خطأ داخلي: {str(inner_e)[:150]}")
        finally:
            browser.close()
except Exception as e:
    send_tg(f"❌ خطأ عام: {str(e)[:150]}")
