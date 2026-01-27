from flask import jsonify, make_response
from . import api_bp


@api_bp.route('/pages/privacy-policy', methods=['GET'])
def privacy_policy():
    """Get privacy policy page with HTML and CSS."""
    html = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سياسة الخصوصية - أكاديمية كيا الدولية</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Cairo', sans-serif;
            background: linear-gradient(135deg, #1B2B5A 0%, #2D4373 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #1B2B5A 0%, #2D4373 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }

        .logo {
            width: 80px;
            height: 80px;
            background: white;
            border-radius: 50%;
            margin: 0 auto 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            font-weight: bold;
            color: #1B2B5A;
        }

        .header h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .header .subtitle {
            font-size: 16px;
            opacity: 0.9;
        }

        .last-updated {
            background: rgba(255, 255, 255, 0.1);
            padding: 8px 20px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 15px;
            font-size: 14px;
        }

        .content {
            padding: 40px 30px;
        }

        .section {
            margin-bottom: 30px;
            padding-bottom: 30px;
            border-bottom: 1px solid #eee;
        }

        .section:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }

        .section h2 {
            color: #1B2B5A;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .section h2::before {
            content: '';
            width: 4px;
            height: 24px;
            background: linear-gradient(180deg, #667EEA 0%, #764BA2 100%);
            border-radius: 2px;
        }

        .section p {
            color: #555;
            line-height: 1.8;
            font-size: 16px;
            text-align: justify;
        }

        .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #eee;
        }

        .footer p {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .footer .contact {
            color: #1B2B5A;
            font-weight: 600;
        }

        .footer .app-name {
            color: #667EEA;
            font-weight: 700;
            font-size: 16px;
            margin-top: 15px;
        }

        @media (max-width: 600px) {
            body {
                padding: 10px;
            }

            .header {
                padding: 30px 20px;
            }

            .header h1 {
                font-size: 24px;
            }

            .content {
                padding: 30px 20px;
            }

            .section h2 {
                font-size: 18px;
            }

            .section p {
                font-size: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">KIA</div>
            <h1>سياسة الخصوصية</h1>
            <p class="subtitle">Privacy Policy</p>
            <span class="last-updated">آخر تحديث: 27 يناير 2026</span>
        </div>

        <div class="content">
            <div class="section">
                <h2>مقدمة</h2>
                <p>
                    مرحباً بكم في تطبيق أكاديمية كيا الدولية للأطفال (KIA). نحن نحترم خصوصيتكم ونلتزم بحماية بياناتكم الشخصية.
                    توضح سياسة الخصوصية هذه كيفية جمع واستخدام وحماية معلوماتكم عند استخدام تطبيقنا.
                </p>
            </div>

            <div class="section">
                <h2>المعلومات التي نجمعها</h2>
                <p>
                    نقوم بجمع المعلومات التي تقدمونها لنا مباشرة، بما في ذلك: الاسم، عنوان البريد الإلكتروني، رقم الهاتف،
                    معلومات الطالب، وتفاصيل الدفع. كما نقوم تلقائياً بجمع معلومات معينة عن جهازك واستخدامك لخدماتنا.
                </p>
            </div>

            <div class="section">
                <h2>كيف نستخدم معلوماتكم</h2>
                <p>
                    نستخدم المعلومات التي نجمعها من أجل: تقديم وصيانة خدماتنا، معالجة المعاملات، إرسال إشعارات حول حسابكم،
                    الاستجابة لطلباتكم، وتحسين خدماتنا.
                </p>
            </div>

            <div class="section">
                <h2>أمان البيانات</h2>
                <p>
                    نطبق إجراءات أمنية مناسبة لحماية معلوماتكم الشخصية من الوصول غير المصرح به أو التغيير أو الإفصاح أو التدمير.
                    ومع ذلك، لا توجد طريقة نقل عبر الإنترنت آمنة بنسبة 100%.
                </p>
            </div>

            <div class="section">
                <h2>مشاركة البيانات</h2>
                <p>
                    لا نبيع أو نتاجر أو نؤجر معلوماتكم الشخصية لأطراف ثالثة. قد نشارك معلوماتكم فقط مع مزودي الخدمات
                    الذين يساعدوننا في تشغيل تطبيقنا وإدارة أعمالنا.
                </p>
            </div>

            <div class="section">
                <h2>حقوقكم</h2>
                <p>
                    لديكم الحق في الوصول إلى معلوماتكم الشخصية أو تصحيحها أو حذفها. يمكنكم أيضاً طلب نسخة من بياناتكم
                    أو مطالبتنا بتقييد معالجة معلوماتكم.
                </p>
            </div>

            <div class="section">
                <h2>خصوصية الأطفال</h2>
                <p>
                    تتضمن خدمتنا إدارة معلومات الطلاب. نحن نولي اهتماماً خاصاً لحماية بيانات الأطفال ونجمع فقط المعلومات
                    الضرورية للأغراض التعليمية بموافقة أولياء الأمور.
                </p>
            </div>

            <div class="section">
                <h2>التغييرات على هذه السياسة</h2>
                <p>
                    قد نقوم بتحديث سياسة الخصوصية هذه من وقت لآخر. سنقوم بإعلامكم بأي تغييرات عن طريق نشر السياسة الجديدة
                    على هذه الصفحة وتحديث تاريخ "آخر تحديث".
                </p>
            </div>

            <div class="section">
                <h2>اتصل بنا</h2>
                <p>
                    إذا كانت لديكم أي أسئلة حول سياسة الخصوصية هذه، يرجى التواصل معنا عبر البريد الإلكتروني:
                    <strong>support@kia-academy.com</strong>
                </p>
            </div>
        </div>

        <div class="footer">
            <p>جميع الحقوق محفوظة © 2026</p>
            <p class="contact">أكاديمية كيا الدولية للأطفال</p>
            <p class="app-name">Kids International Academy</p>
        </div>
    </div>
</body>
</html>'''

    response = make_response(html)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response
