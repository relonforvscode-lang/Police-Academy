# حل مشكلة Invalid OAuth2 Redirect URI

## المشكلة
```
Error: Invalid Form Body
code: 50035
errors: {"redirect_uri": {"_errors": [{"code": "URL_TYPE_INVALID_URL", "message": "Not a well formed URL."}]}}
```

هذا يعني الـ redirect_uri الذي يرسله Django **لا يطابق** ما مسجل في Discord console.

---

## الحل (3 خطوات)

### ✅ الخطوة 1: اعرف الـ Redirect URI الصحيح

**في local development:**
```
http://127.0.0.1:8000/apply/discord-callback/
```

**على Render:**
```
https://your-service.onrender.com/apply/discord-callback/
```

للتحقق من الـ URI الفعلي:
```bash
# الطريقة 1: من خلال السجلات
# ستري لقطة "Redirect URI: ..." في discord_oauth_debug.log

# الطريقة 2: اضغط discord login وشوف الخطأ - سيقول ايش الـ URI الذي أرسله Django
```

---

### ✅ الخطوة 2: حدّث Discord Console

1. اذهب إلى https://discord.com/developers/applications
2. اختر تطبيقك
3. في الـ sidebar، اختر **OAuth2** → **General**
4. ابحث عن **Redirects** section
5. أضف الـ redirect URI بالضبط:
   - **Local:** `http://127.0.0.1:8000/apply/discord-callback/`
   - **Render:** `https://your-service.onrender.com/apply/discord-callback/`

**مهم:** 
- ✅ يجب أن يطابق بالضبط (protocol + domain + path)
- ✅ لا تنسى `/` في النهاية
- ✅ HTTP للـ local، HTTPS للـ Render

---

### ✅ الخطوة 3: اختبر مجدداً

**Local:**
```bash
# 1. شغّل السيرفر
python manage.py runserver

# 2. افتح http://127.0.0.1:8000/apply/
# 3. اضغط Discord login button
```

**Render:**
```bash
# 1. Push إلى GitHub
git add .
git commit -m "Fix: Discord OAuth redirect URI"
git push

# 2. انتظر deployment
# 3. افتح https://your-service.onrender.com/apply/
# 4. اضغط Discord login button
```

---

## صور متاحة للـ URI الخاص بك

قبل ما تروح Discord console، شغّل هذا:

```bash
cd C:\Users\Gaming\Desktop\Newww

# لـ local
python manage.py runserver
# ثم افتح المتصفح وروح: http://127.0.0.1:8000/apply/discord-login/
# سيعطيك رسالة error لكن check السجلات لـ Redirect URI

# أو شيك السجلات مباشرة:
type discord_oauth_debug.log | findstr "Redirect URI"
```

---

## إذا كان الـ Error زي هيك:
```
"message": "Invalid Form Body"
```
**السبب:** الـ URI في Discord console مختلف عن اللي يرسله Django

---

## بديل: استخدم متغير بيئي

إذا تريد تحديد الـ redirect_uri يدويّاً (optional):

أضيف في `.env`:
```
DISCORD_REDIRECT_URI=https://your-service.onrender.com/apply/discord-callback/
```

أو في الكود:
```python
redirect_uri = os.getenv('DISCORD_REDIRECT_URI') or request.build_absolute_uri('/apply/discord-callback/')
```

---

## ملخص سريع

| المكان | الـ Redirect URI |
|--------|-----------------|
| Local | `http://127.0.0.1:8000/apply/discord-callback/` |
| Render | `https://your-service.onrender.com/apply/discord-callback/` |
| Discord تطبيقك | نفس الـ URL المستخدم |

✅ **يجب أن تكون نفس الـ URL بالضبط في جميع الأماكن**

---

## الخطوات الفعلية:

1. **اعرف render domain الخاص بك:**
   - من render.com dashboard أو URL في المتصفح
   - مثال: `my-app.onrender.com`

2. **الـ redirect_uri للـ Render:**
   - `https://my-app.onrender.com/apply/discord-callback/`

3. **أضفه في Discord console:**
   - Applications → Your App → OAuth2 → Redirects
   - Paste: `https://my-app.onrender.com/apply/discord-callback/`
   - Save

4. **اختبر:**
   - Return إلى الموقع وضغط Discord login مرة ثانية
