# استخدام النسخة الرسمية الجاهزة التي تحتوي على المتصفح وكل ملفاته
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# تشغيل البوت
CMD ["python", "app.py"]
