# قائمة التحقق قبل الرفع على Render

## 1️⃣ قبل الرفع (Local Testing)

### اختبر في جهازك أولاً:
```bash
# 1. جرب الـ endpoints
python test_endpoints.py

# 2. تحقق من Django configuration
python manage.py check

# 3. شغّل السيرفر محلياً
python manage.py runserver 127.0.0.1:8000
```

### في المتصفح:
- [ ] افتح `http://127.0.0.1:8000/apply/`
- [ ] اضغط "تسجيل الدخول عبر Discord"
- [ ] أكمل OAuth flow
- [ ] تحقق من البيانات

### شيك السجلات:
```bash
# افتح ملف السجلات
type discord_oauth_debug.log

# يجب تري:
# [OK] Authorization code received
# [SEND] Requesting access token
# [RECEIVE] Token response status: 200
# [SUCCESS] Session updated successfully
```

---

## 2️⃣ قبل Push إلى GitHub

```bash
# تأكد من عدم وجود أخطاء
python manage.py check --deploy

# تأكد من أن requirements synchronized
pip freeze > requirements.txt
```

---

## 3️⃣ بعد الرفع على Render

### تحقق من Logs على Render:
1. اذهب إلى https://dashboard.render.com
2. اختر Project
3. افتح **Logs** tab
4. ابحث عن:
   ```
   Successfully built application
   Application is running
   ```

### اختبر الموقع المباشر:
```bash
# استبدل YOUR_SERVICE_NAME بـ service name في Render
# مثال: myapp.onrender.com

# 1. اختبر أن الموقع يحمل
curl https://YOUR_SERVICE_NAME.onrender.com/apply/

# يجب تري: HTTP 200
```

### شيك Render Logs للأخطاء:
- [ ] لا توجد أخطاء في startup
- [ ] لا توجد أخطاء في database connection
- [ ] لا توجد أخطاء في Discord credentials

---

## 4️⃣ اختبار OAuth على Render

**في المتصفح:**
1. افتح `https://YOUR_SERVICE_NAME.onrender.com/apply/`
2. اضغط "تسجيل الدخول عبر Discord"
3. استكمل التسجيل
4. يجب ترجع مع البيانات

**في Render Logs:**
ابحث عن:
```
[OK] Authorization code received
[SEND] Requesting access token
[RECEIVE] Token response status: 200
```

---

## 5️⃣ أوامر مفيدة للـ Debugging

### عرض live logs من Render:
```bash
# قم بتثبيت Render CLI أولاً:
npm install -g @render-com/cli

# ثم شاهد logs
render logs --tail
```

### اختبر endpoint محدد:
```bash
# اختبر apply page
curl https://YOUR_SERVICE_NAME.onrender.com/apply/

# اختبر login redirect
curl -I https://YOUR_SERVICE_NAME.onrender.com/apply/discord-login/
```

---

## 6️⃣ الأخطاء الشائعة

| المشكلة | الحل |
|--------|------|
| 500 Error | شيك Render logs، غالباً database connection |
| ERROR 403 | تأكد من DISCORD_CLIENT_ID و DISCORD_CLIENT_SECRET صحيح |
| Redirect URI mismatch | تأكد من ALLOWED_HOSTS يحتوي على domain الـ Render |
| OAuth not working | تأكد من Discord OAuth callback URL محدث في Discord console |

---

## 7️⃣ خطوات سريعة قبل كل رفع

```bash
# ✅ خطوة 1: اختبر محلياً
python test_endpoints.py

# ✅ خطوة 2: شيك settings
python manage.py check --deploy

# ✅ خطوة 3: اختبر OAuth flow يدوياً
# افتح http://127.0.0.1:8000/apply/ واختبر

# ✅ خطوة 4: Push إلى GitHub
git add .
git commit -m "Fix: [وصف التغييرات]"
git push origin main

# ✅ خطوة 5: انتظر Render deployment
# يستغرق عادة 2-5 دقائق

# ✅ خطوة 6: اختبر على Render
# افتح https://YOUR_SERVICE.onrender.com/apply/
```

---

## 8️⃣ متحقق الأمان (Security Checks)

قبل الرفع:
- [ ] لا توجد API keys مكتوبة في الكود (استخدم .env)
- [ ] DEBUG=False في production
- [ ] ALLOWED_HOSTS محدثة بشكل صحيح
- [ ] SECURE_SSL_REDIRECT=True في production
- [ ] CSRF settings صحيحة

---

## ملاحظات إضافية

- **إذا حدث خطأ OAuth**: شيك [discord_oauth_debug.log](discord_oauth_debug.log) للتفاصيل
- **إذا بطء الموقع**: قد تحتاج هجرة database من MySQL إلى PostgreSQL على Render
- **إذا مشكلة في staticfiles**: تأكد من `python manage.py collectstatic` يركض أثناء build
