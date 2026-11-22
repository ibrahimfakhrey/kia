"""Bulk import of parent accounts and their children from an Excel sheet."""
import re
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
# A first row with any of these headers means the detailed format; otherwise the
# file is treated as plain name lists (one sheet per class, one name per row).
DETAILED_HEADERS = {'parent name', 'email', 'student name'}
NAME_LIST_HEADERS = {'name list', 'names list', 'name', 'names', 'student name', 'students'}
EMAIL_DOMAIN = 'kia.com'


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


def _clean_name(value):
    """Tidy a name typed in a list: drops numbering ("12. "), invisible characters and stray dots."""
    name = re.sub(r'[\u200b-\u200f\ufeff]', '', _text(value)).replace('\u00a0', ' ')
    name = re.sub(r'^\s*\d+\s*[.)\-]\s*', '', name)
    name = re.sub(r'\s+', ' ', name).strip(' .')
    return ' '.join(word[0].upper() + word[1:] for word in name.split(' ') if word)


def _class_key(name):
    """Key for matching a sheet title to a class: "k1", "K1 A" and "KG1 A" style names line up."""
    key = re.sub(r'\s+', '', name).upper()
    return re.sub(r'^K(?=\d)', 'KG', key)


def _class_display_name(sheet_title):
    """Name for a class that has to be created from a sheet title ("K1 B" -> "KG1 B")."""
    match = re.fullmatch(r'KG(\d+)([A-Z]?)', _class_key(sheet_title))
    if not match:
        return sheet_title.strip()
    return f'KG{match.group(1)} {match.group(2)}'.strip()


def _email_base(name):
    """"Zain Ibrahim" -> "zain.ibrahim" (first two words, English letters and digits only)."""
    words = [re.sub(r'[^a-z0-9]', '', word) for word in name.lower().split()]
    return '.'.join([word for word in words if word][:2]) or 'parent'


def _unique_email(name, used_emails):
    base = _email_base(name)
    email = f'{base}@{EMAIL_DOMAIN}'
    counter = 1
    while email in used_emails:
        email = f'{base}{counter}@{EMAIL_DOMAIN}'
        counter += 1
    used_emails.add(email)
    return email


def build_credentials_workbook(created_parents):
    """Excel file with the login details of the accounts an import just created."""
    wb = Workbook()
    ws = wb.active
    ws.title = 'Accounts'
    ws.append(['Name', 'Class', 'Email', 'Password', 'Phone', 'Students'])
    for parent in created_parents:
        ws.append([parent['name'], parent.get('class', ''), parent['email'], parent['password'],
                   parent['phone'] or '', ', '.join(parent['students'])])
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill('solid', fgColor='DDEBF7')
    for letter, width in zip('ABCDEF', (30, 14, 34, 16, 16, 34)):
        ws.column_dimensions[letter].width = width
    ws.freeze_panes = 'A2'
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def build_name_list_sample_workbook():
    """Sample for the simple format: one sheet per class, one student name per row."""
    class_names = [c.name for c in Classe.query.order_by(Classe.name).limit(2).all()] or ['KG1', 'KG2']
    samples = [['Zain Ibrahim', 'Yara Ayman', 'Selim Mahmoud'], ['Omar Ismail', 'Laila Ibrahim']]
    wb = Workbook()
    wb.remove(wb.active)
    for class_name, names in zip(class_names, samples):
        ws = wb.create_sheet(class_name[:31])
        ws.append(['Name list'])
        ws['A1'].font = Font(bold=True)
        for name in names:
            ws.append([name])
        ws.column_dimensions['A'].width = 32
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def _import_name_lists(workbook, result, default_password):
    """Each sheet is a class and each row a student; a parent account is generated per student."""
    errors = result['errors']
    entries = []  # (sheet title, student name)
    for sheet in workbook.worksheets:
        for row_number, row in enumerate(sheet.iter_rows(values_only=True), start=1):
            name = _clean_name(next((v for v in row if _text(v)), None))
            if not name or name.lower() in NAME_LIST_HEADERS:
                continue
            if len(name) > 100:
                errors.append(f'ورقة "{sheet.title}" صف {row_number}: الاسم أطول من 100 حرف.')
                continue
            entries.append((sheet.title, name))

    if not errors and not entries:
        errors.append('الملف لا يحتوي على أي أسماء.')
    if errors:
        return result

    classes = {_class_key(c.name): c for c in Classe.query.all()}
    used_emails = {email.lower() for (email,) in db.session.query(User.email)}
    known_students = {}  # class id -> names already in that class

    for sheet_title, name in entries:
        key = _class_key(sheet_title)
        classe = classes.get(key)
        if classe is None:
            classe = Classe(name=_class_display_name(sheet_title))
            db.session.add(classe)
            db.session.flush()
            classes[key] = classe
            result['classes_created'].append(classe.name)
        if classe.id not in known_students:
            known_students[classe.id] = {
                s.full_name.strip().lower() for s in Student.query.filter_by(class_id=classe.id)
            }
        if name.lower() in known_students[classe.id]:
            result['students_skipped'] += 1
            continue
        known_students[classe.id].add(name.lower())

        password = default_password or _generate_password()
        user = User(email=_unique_email(name, used_emails), full_name=name,
                    role='parent', is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        db.session.add(Student(parent_id=user.id, full_name=name, class_id=classe.id))
        result['students_created'] += 1
        result['created_parents'].append({
            'name': name, 'email': user.email, 'phone': None, 'password': password,
            'class': classe.name, 'students': [name],
        })

    db.session.commit()
    return result


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


def import_parents(stream, default_password=''):
    """Validate the whole file first; nothing is saved if any row has an error.

    Accepts the detailed format (one row per child with parent details) or plain
    name lists (one sheet per class). default_password is given to every new
    account that has no password of its own; without it a random one is generated.

    Returns a dict with: errors, created_parents, existing_parents,
    students_created, students_skipped, classes_created.
    """
    result = {
        'errors': [],
        'created_parents': [],
        'existing_parents': 0,
        'students_created': 0,
        'students_skipped': 0,
        'classes_created': [],
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
    if not DETAILED_HEADERS & index.keys():
        return _import_name_lists(workbook, result, default_password)
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
            password = parent['password'] or default_password or _generate_password()
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
