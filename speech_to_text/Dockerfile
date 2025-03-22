# استفاده از یک تصویر پایه Python
FROM python:3.10

# تعیین دایرکتوری کاری داخل کانتینر
WORKDIR /speech_to_text

# کپی کردن تمام فایل‌ها از دایرکتوری محلی به داخل کانتینر
COPY . /speech_to_text

# نصب وابستگی‌ها از فایل requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# دستور اجرای ربات (به جای bot.py نام فایل خودتون رو وارد کنید)
CMD ["python", "main.py"]
