from django.core.management.base import BaseCommand
from main.models import Question

SAMPLES = [
    ("ما هو اختصار HTML؟", ["HyperText Markup Language","HighText Machine Language","Hyperlink and Text Markup","Home Tool Markup Language"], 0),
    ("أي لغة تُستخدم عادةً لبرمجة الواجهة الأمامية؟", ["Python","JavaScript","C#","Go"], 1),
    ("ما معني CSS؟", ["Cascading Style Sheets","Computer Style Sheets","Creative Style System","Control Style Sheet"], 0),
    ("ما هي قاعدة البيانات العلائقية؟", ["NoSQL","Relational DB","File System","Key-Value Store"], 1),
    ("ما هو بروتوكول HTTP؟", ["HyperText Transfer Protocol","High Transfer Text Protocol","Hyper Transfer Text Process","Home Transfer Tool Protocol"], 0),
    ("أي من التالي هو نظام تشغيل؟", ["Django","React","Linux","Postman"], 2),
    ("ما أداة إدارة الحزم في بايثون؟", ["npm","pip","gem","cargo"], 1),
    ("ما هو Docker؟", ["Virtual Machine","Containerization platform","Programming language","Database"], 1),
    ("أي من التالي يستخدم لتخزين ملفات JSON في بايثون؟", ["requests","json","os","re"], 1),
    ("ما هي وظيفة Git؟", ["نسخ الملفات","تتبع التغيرات في الكود","تشغيل التطبيقات","تنظيم قواعد البيانات"], 1),
    ("ما الفرق بين GET و POST في HTTP؟", ["GET يرسل جسم، POST لا يرسل","GET يطلب بيانات، POST يرسل بيانات","لا فرق","GET أسرع دائما"], 1),
    ("ما هي MVC؟", ["Model View Controller","Module View Controller","Model Version Control","Main View Controller"], 0),
    ("ما المقصود بالـ ORM؟", ["Object-Relational Mapping","Object Remote Manager","Online Resource Manager","Original Relational Model"], 0),
    ("أي من التالي هو بروتوكول أمان الشبكة؟", ["SSL/TLS","FTP","SMTP","HTTP"], 0),
    ("ما وظيفة Nginx؟", ["قاعدة بيانات","خادم ويب وعكس بروكسي","محرر نصوص","أداة اختبار"], 1),
    ("ما هو JSON؟", ["تنسيق بيانات نصي","قاعدة بيانات","لغة برمجة","خادم"], 0),
    ("أي من التالي هو نظام لإدارة قواعد البيانات؟", ["MySQL","HTML","CSS","React"], 0),
    ("ما الفرق بين synchronous و asynchronous؟", ["لا فرق","التنفيذ المتسلسل مقابل المتزامن","التنفيذ المتزامن مقابل المتسلسل","التنفيذ المحلي مقابل البعيد"], 1),
    ("ما الذي يحدد واجهات برمجة التطبيقات (API)؟", ["قواعد التواصل بين مكونات البرمجية","واجهة المستخدم","لغة البرمجة","قاعدة البيانات"], 0),
    ("ما هي مكتبة requests في بايثون؟", ["مكتبة للتعامل مع الشبكات وHTTP","مكتبة لعرض الواجهات","أداة قواعد بيانات","محرر نصوص"], 0),
    ("ما اسم إدارة الحزم في Node.js؟", ["pip","npm","cargo","composer"], 1),
    ("ما أهمية استخدام بيئات افتراضية في بايثون؟", ["تحسين الأداء","عزل تبعيات المشروع","زيادة الذاكرة","تسريع النسخ الاحتياطي"], 1),
    ("أي من التالي يُستخدم لتنسيق النص في HTML؟", ["<div>","<p>","<style>","<script>"], 1),
    ("ما معنى SQL؟", ["Structured Query Language","Simple Query List","Standard Query Language","Server Query Language"], 0),
    ("ما فائدة migrations في Django؟", ["تغيير الواجهات","تتبع وتطبيق تغييرات على هيكل قاعدة البيانات","توليد ملفات static","تنظيف السجلات"], 1),
    ("ما هي وحدة الزمن في توقيت الجافاسكربت؟", ["milliseconds","seconds","minutes","hours"], 0),
    ("ما الذي يقوم به whitenoise في Django؟", ["إدارة قواعد البيانات","خدمة ملفات static مبسطة","مراقبة الأداء","التخزين السحابي"], 1),
    ("أي من التالي إطار عمل ويب في بايثون؟", ["Laravel","Django","Ruby on Rails","Angular"], 1),
    ("ما المقصود بـ CSRF؟", ["Cross-Site Request Forgery","Client-Side Request Form","Central Server Request Framework","Cross-Site Resource Format"], 0)
]

class Command(BaseCommand):
    help = 'Load 30 sample questions into the DB'

    def handle(self, *args, **options):
        created = 0
        for text, opts, correct in SAMPLES:
            q = Question.objects.create(
                text=text,
                option_a=opts[0],
                option_b=opts[1],
                option_c=opts[2],
                option_d=opts[3],
                correct_index=correct
            )
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created} sample questions'))
