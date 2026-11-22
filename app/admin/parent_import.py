"""Bulk import of parent accounts and their children from an Excel sheet."""
import secrets
import string
from datetime import date, datetime
from io import BytesIO

from email_validator import validate_email, EmailNotValidError
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from sqlalchemy import func

from app.extensions import db
from app.models import User, Classe, Student

COLUMNS = ['Parent Name', 'Email', 'Phone', 'Password', 'Student Name', 'Class', 'Date of Birth']
REQUIRED_COLUMNS = ['Parent Name', 'Email']
DATE_FORMATS = ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y')
MIN_PASSWORD_LENGTH = 6


def _generate_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _text(value):
    """Cell value as a clean string ('' for empty cells)."""
    if value is None:
        return ''
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value).strip()


def _phone(value):
    text = _text(value)
    # Excel drops the leading zero when a mobile number is stored as a number.
    if isinstance(value, (int, float)) and len(text) == 10 and text.startswith('1'):
        text = '0' + text
    return text


def _parse_date(value):
    """Returns (date or None, ok)."""
    if value is None or _text(value) == '':
        return None, True
    if isinstance(value, datetime):
        return value.date(), True
    if isinstance(value, date):
        return value, True
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(_text(value), fmt).date(), True
        except ValueError:
            continue
    return None, False


def build_sample_workbook():
    """Sample sheet the admin can download, fill in and upload back."""
    class_names = [c.name for c in Classe.query.order_by(Classe.name).limit(2).all()]
    first_class = class_names[0] if class_names else ''
    second_class = class_names[-1] if class_names else ''

    wb = Workbook()
    ws = wb.active
    ws.title = 'Parents'
    ws.append(COLUMNS)
    ws.append(['Ahmed Mahmoud', 'ahmed.mahmoud@example.com', '01000000001', 'Pass1234',
               'Ghazal Ahmed Mahmoud', first_class, '2021-03-15'])
    ws.append(['Ahmed Mahmoud', 'ahmed.mahmoud@example.com', '01000000001', '',
               'Omar Ahmed Mahmoud', second_class, '2020-01-10'])
    ws.append(['Hatem Mosaad', 'hatem.mosaad@example.com', '01000000002', '',
               'Yassen Hatem Mosaad', first_class, ''])

    header_fill = PatternFill('solid', fgColor='DDEBF7')
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill
    for letter, width in zip('ABCDEFG', (28, 34, 18, 16, 30, 16, 16)):
        ws.column_dimensions[letter].width = width
    # Keep phone, password and date as text so Excel does not reformat them.
    for letter in ('C', 'D', 'G'):
        for row in range(1, 1001):
            ws[f'{letter}{row}'].number_format = '@'
    ws.freeze_panes = 'A2'

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def import_parents(stream):
    """Validate the whole sheet first; nothing is saved if any row has an error.

    Returns a dict with: errors, created_parents, existing_parents,
    students_created, students_skipped.
    """
    result = {
        'errors': [],
        'created_parents': [],
        'existing_parents': 0,
        'students_created': 0,
        'students_skipped': 0,
    }
    errors = result['errors']

    try:
        workbook = load_workbook(stream, read_only=True, data_only=True)
    except Exception:
        errors.append('تعذر قراءة الملف. تأكد أنه ملف Excel بصيغة ‎.xlsx')
        return result

    rows = workbook.worksheets[0].iter_rows(values_only=True)
    header = next(rows, None) or ()
    index = {_text(h).lower(): i for i, h in enumerate(header) if _text(h)}
    missing = [c for c in REQUIRED_COLUMNS if c.lower() not in index]
    if missing:
        errors.append('أعمدة مطلوبة غير موجودة في الصف الأول: ' + ', '.join(missing))
        return result

    def cell(row, column):
        i = index.get(column.lower())
        return row[i] if i is not None and i < len(row) else None

    classes = {c.name.strip().lower(): c.id for c in Classe.query.all()}

    parents = {}  # email -> parent data, in sheet order
    for row_number, row in enumerate(rows, start=2):
        if not any(_text(v) for v in row):
            continue

        def error(message):
            errors.append(f'صف {row_number}: {message}')

        name = _text(cell(row, 'Parent Name'))
        email = _text(cell(row, 'Email')).lower()
        phone = _phone(cell(row, 'Phone'))
        password = _text(cell(row, 'Password'))
        student_name = _text(cell(row, 'Student Name'))
        class_name = _text(cell(row, 'Class'))
        birth_date, date_ok = _parse_date(cell(row, 'Date of Birth'))

        if not email:
            error('البريد الإلكتروني مطلوب.')
            continue
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            error(f'البريد الإلكتروني غير صالح ({email}).')
            continue
        if len(email) > 120:
            error('البريد الإلكتروني أطول من 120 حرفاً.')
            continue

        parent = parents.get(email)
        if parent is None:
            existing = User.query.filter(func.lower(User.email) == email).first()
            if existing and existing.role != 'parent':
                error(f'البريد الإلكتروني {email} مستخدم لحساب غير ولي أمر.')
                continue
            parent = parents[email] = {
                'user': existing, 'email': email, 'name': name, 'phone': phone,
                'password': '', 'students': [],
            }
            if existing is None and not name:
                error('اسم ولي الأمر مطلوب.')

        if parent['user'] is None:
            if len(name) > 100:
                error('اسم ولي الأمر أطول من 100 حرف.')
            if len(phone) > 20:
                error('رقم الهاتف أطول من 20 رقماً.')
            if password and len(password) < MIN_PASSWORD_LENGTH:
                error(f'كلمة المرور يجب ألا تقل عن {MIN_PASSWORD_LENGTH} أحرف.')
            parent['phone'] = parent['phone'] or phone
            parent['password'] = parent['password'] or password

        if not student_name:
            continue
        if len(student_name) > 100:
            error('اسم الطالب أطول من 100 حرف.')
        class_id = None
        if class_name:
            class_id = classes.get(class_name.lower())
            if class_id is None:
                error(f'الفصل "{class_name}" غير موجود. أضفه أولاً من صفحة الفصول.')
        if not date_ok:
            error('تاريخ الميلاد غير صالح. استخدم الصيغة YYYY-MM-DD.')
        parent['students'].append({
            'name': student_name, 'class_id': class_id, 'birth_date': birth_date,
        })

    if not errors and not parents:
        errors.append('الملف لا يحتوي على أي بيانات.')
    if errors:
        return result

    for parent in parents.values():
        user = parent['user']
        if user is None:
            password = parent['password'] or _generate_password()
            user = User(email=parent['email'], full_name=parent['name'],
                        phone=parent['phone'] or None, role='parent', is_active=True)
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            known_students = set()
            created = {'name': user.full_name, 'email': user.email, 'phone': user.phone,
                       'password': password, 'students': []}
            result['created_parents'].append(created)
        else:
            result['existing_parents'] += 1
            known_students = {s.full_name.strip().lower() for s in user.students}
            created = None

        for student in parent['students']:
            key = student['name'].lower()
            if key in known_students:
                result['students_skipped'] += 1
                continue
            known_students.add(key)
            db.session.add(Student(parent_id=user.id, full_name=student['name'],
                                   class_id=student['class_id'],
                                   date_of_birth=student['birth_date']))
            result['students_created'] += 1
            if created is not None:
                created['students'].append(student['name'])

    db.session.commit()
    return result
