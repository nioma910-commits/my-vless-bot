try:
            # 1. التوجه للرابط عبر البروكسي
            page.goto(SSO_URL, wait_until="networkidle", timeout=90000)
            time.sleep(10)
            
            # --- إضافة: تخطي شاشة الترحيب الجديدة ---
            try:
                # البحث عن أزرار الترحيب والضغط عليها
                for welcome_btn in ["I understand", "Accept", "Confirm", "موافق", "فهمت"]:
                    if page.locator(f'button:has-text("{welcome_btn}")').is_visible():
                        page.locator(f'button:has-text("{welcome_btn}")').click()
                        time.sleep(5)
            except: pass
            # ---------------------------------------

            page.screenshot(path="after_welcome.png")
            send_tg_photo("after_welcome.png", "📸 تجاوزنا شاشة الترحيب! جاري الدخول للوحة التحكم...")
            
            # 2. القفز لـ Cloud Shell
            page.goto("https://console.cloud.google.com/home/dashboard?cloudshell=true", wait_until="networkidle", timeout=60000)
            time.sleep(20)

            # تخطي نوافذ لوحة التحكم
            for btn in ["Continue", "Start", "Agree", "I agree", "No thanks", "Close"]:
                try: 
                    if page.locator(f'button:has-text("{btn}")').is_visible():
                        page.locator(f'button:has-text("{btn}")').click(timeout=3000)
                except: pass

            # انتظار شاشة الأوامر
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
