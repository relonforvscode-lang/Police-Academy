# دليل النشر الكامل إلى Render (PostgreSQL)

هذا الدليل يشرح بالخطوات كل ما تحتاجه لرفع مشروع Django هذا على Render مع قاعدة بيانات PostgreSQL.

ماذا غُيّر في المشروع
- أُزيلت مراجع `mysqlclient` من ملفات المتطلبات المندرجة في المستودع لتجنّب أخطاء التثبيت على Render.
- أُضيف `requirements-render.txt` الذي لا يحتوي `mysqlclient` ويستخدم أثناء البناء على Render.
- أُحدّث `build/build.sh` ليثبّت `requirements-render.txt` حين يكتشف `DATABASE_URL` لبوستجريـس.
- `myproject/settings.py` الآن يقرأ `DATABASE_URL` عبر `dj-database-url`، ويفرض `sslmode=require` لبوستجريـس، ويطلب `DJANGO_SECRET_KEY` في الإنتاج.
- أُحدّث `render.yaml` لإضافة `CSRF_TRUSTED_ORIGINS` وبدء `gunicorn` مع توجيه السجلات إلى stdout.
- أُضيف `.gitignore` لاستبعاد `venv/`, `.env`, `db.sqlite3`، إلخ.

المتطلبات البيئية الأساسية على Render
- `DJANGO_SECRET_KEY` — قيمة سرية قوية
- `DEBUG` — ضع `False`
- `ALLOWED_HOSTS` — استخدم `${RENDER_EXTERNAL_HOSTNAME}` أو نطاقك
- `CSRF_TRUSTED_ORIGINS` — `https://${RENDER_EXTERNAL_HOSTNAME}`
- `SECURE_SSL_REDIRECT` — `True` مستحسن
- `DATABASE_URL` — تُنشئها Render تلقائياً عند إضافة خدمة PostgreSQL

خطوات نشر سريعة
1) ادفع التغييرات الى الريبو المتصل بـ Render:

```bash
git add .
git commit -m "Prepare repo for Render deployment (Postgres-compatible)"
git push origin main
```

2) افتح لوحة Render:
- انشئ Web Service جديد أو استورد `render.yaml`، Render سيعدّ قاعدة Postgres ويربط `DATABASE_URL`.
- في إعدادات الخدمة اضف/تحقق المتغيرات البيئية المذكورة أعلاه.

3) بناء ونشر:
- Render سيشغّل `build/build.sh` الذي يثبت `requirements-render.txt`, يجمع static، ويشغّل migrate (أو `release` من `Procfile`).
- راجع السجلات للتأكد من نجاح `pip install`, `collectstatic`, و`migrate`.

اختبار محلي سريع (باستخدام Postgres محلي أو Docker):

```bash
export DATABASE_URL='postgresql://user:pass@localhost:5432/dbname'
pip install --upgrade pip
pip install -r requirements-render.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

ملاحظات أمان وإنتاجية
- لا تدفع `DJANGO_SECRET_KEY` إلى المستودع.
- فعل `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` عندما `DEBUG=False`.
- راجع السجلات أول نشر إن حصل خطأ في المهاجرات.

مواضيع اختيارية يمكنني أجهزها لك بالمستودع لو تحب:
- إعداد النسخ الاحتياطي لقاعدة بيانات Render.
- إضافة Sentry أو Log drains لمراقبة الأخطاء.
- إعداد Email backend (SendGrid/Mailgun).

تم الإنشاء: 2026-02-02
