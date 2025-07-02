from flask import Blueprint, request, jsonify
import mysql.connector
import os
from PIL import Image
from io import BytesIO

# 假设你有 db_config
from config import db_config

student_bp = Blueprint('student', __name__)

# 获取学生账号信息
@student_bp.route('/api/student/info', methods=['GET'])
def get_student_info():
    student_id = request.args.get('id')
    if not student_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT student_id AS id, name, gender, birthday, contact, major, class_id FROM student WHERE student_id=%s",
        (student_id,)
    )
    stu = cursor.fetchone()
    cursor.close()
    conn.close()
    if not stu:
        return jsonify({'success': False, 'message': '未找到该学生'}), 404
    # 统一格式化 birthday 字段
    if stu['birthday']:
        if hasattr(stu['birthday'], 'strftime'):
            stu['birthday'] = stu['birthday'].strftime('%Y-%m-%d')
        else:
            stu['birthday'] = str(stu['birthday'])[:10]
    else:
        stu['birthday'] = ''
    return jsonify({'success': True, **stu})

# 修改学生信息（仅允许改gender, birthday, contact, major）
@student_bp.route('/api/student/update_info', methods=['POST'])
def update_student_info():
    data = request.get_json()
    student_id = data.get('student_id')
    gender = data.get('gender')
    birthday = data.get('birthday')
    contact = data.get('contact')
    major = data.get('major')
    if not student_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE student SET gender=%s, birthday=%s, contact=%s, major=%s WHERE student_id=%s",
        (gender, birthday, contact, major, student_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'message': '信息更新成功'})

@student_bp.route('/api/student/courses', methods=['GET'])
def get_courses_for_student():
    student_id = request.args.get('student_id')
    course_id_kw = request.args.get('course_id')
    course_name_kw = request.args.get('course_name')
    only_selected = request.args.get('only_selected')
    if not student_id:
        return jsonify({'success': False, 'message': '缺少学生ID'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    sql = """
        SELECT c.course_id, c.name, c.credit, c.location, c.time, c.maxStudents, c.numStudents,
            EXISTS(SELECT 1 FROM student_course sc WHERE sc.course_id = c.course_id AND sc.student_id = %s) AS selected
        FROM course c
        WHERE 1=1
    """
    params = [student_id]
    if course_id_kw and course_id_kw.strip():
        sql += " AND LOWER(c.course_id) LIKE %s"
        params.append(f"%{course_id_kw.strip().lower()}%")
    if course_name_kw and course_name_kw.strip():
        sql += " AND LOWER(c.name) LIKE %s"
        params.append(f"%{course_name_kw.strip().lower()}%")
    if only_selected == '1':
        sql += " AND EXISTS(SELECT 1 FROM student_course sc WHERE sc.course_id = c.course_id AND sc.student_id = %s)"
        params.append(student_id)
    sql += " ORDER BY c.course_id"
    cursor.execute(sql, tuple(params))
    courses = cursor.fetchall()

    # 查询每门课程的所有任课教师（id和name）
    for course in courses:
        cursor.execute("""
            SELECT t.teacher_id, t.name
            FROM teacher_course tc
            JOIN teacher t ON tc.teacher_id = t.teacher_id
            WHERE tc.course_id = %s
        """, (course['course_id'],))
        course['teachers'] = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify({'success': True, 'courses': courses})

@student_bp.route('/api/student/select_course', methods=['POST'])
def select_course():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    if not student_id or not course_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # 检查是否已选
    cursor.execute("SELECT * FROM student_course WHERE student_id=%s AND course_id=%s", (student_id, course_id))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '已选该课程'})
    # 检查人数上限
    cursor.execute("SELECT maxStudents, numStudents FROM course WHERE course_id=%s", (course_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '课程不存在'})
    max_students, num_students = row
    if num_students >= max_students:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '人数已满'})
    # 插入选课
    cursor.execute("INSERT INTO student_course (student_id, course_id) VALUES (%s, %s)", (student_id, course_id))
    # numStudents加一
    cursor.execute("UPDATE course SET numStudents = numStudents + 1 WHERE course_id=%s", (course_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

@student_bp.route('/api/student/drop_course', methods=['POST'])
def drop_course():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    if not student_id or not course_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # 先判断是否已选
    cursor.execute("SELECT * FROM student_course WHERE student_id=%s AND course_id=%s", (student_id, course_id))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '未选该课程'})
    # 删除选课
    cursor.execute("DELETE FROM student_course WHERE student_id=%s AND course_id=%s", (student_id, course_id))
    # numStudents减一，防止负数
    cursor.execute("UPDATE course SET numStudents = GREATEST(numStudents - 1, 0) WHERE course_id=%s", (course_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

from werkzeug.utils import secure_filename

@student_bp.route('/api/student/upload_avatar', methods=['POST'])
def upload_avatar():
    student_id = request.form.get('student_id')
    file = request.files.get('avatar')
    if not student_id or not file:
        return jsonify({'success': False, 'message': '缺少参数'}), 400

    # 只允许图片类型
    if not file.mimetype.startswith('image/'):
        return jsonify({'success': False, 'message': '只允许上传图片文件'}), 400

    # 目标文件夹（public/assets）
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/public/assets'))
    student_dir = os.path.join(assets_dir, secure_filename(student_id))
    os.makedirs(student_dir, exist_ok=True)

    # 统一保存为 avatar.png
    avatar_filename = 'avatar.png'
    avatar_path = os.path.join(student_dir, avatar_filename)

    # 用 Pillow 统一转为 png
    try:
        img = Image.open(file.stream)
        img = img.convert('RGBA')  # 保证有透明通道
        img.save(avatar_path, format='PNG')
    except Exception as e:
        return jsonify({'success': False, 'message': f'图片处理失败: {e}'}), 400

    # 删除旧的 jpg/jpeg/gif 文件，避免混乱
    for ext in ['jpg', 'jpeg', 'gif']:
        old_path = os.path.join(student_dir, f'avatar.{ext}')
        if os.path.exists(old_path):
            os.remove(old_path)

    return jsonify({'success': True, 'avatar': f'/assets/{student_id}/{avatar_filename}'})

@student_bp.route('/api/student/timetable', methods=['GET'])
def get_student_timetable():
    student_id = request.args.get('student_id')
    if not student_id:
        return jsonify({'success': False, 'message': '缺少学生ID'}), 400

    # 查询学生已选课程及其时间
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.name, c.time, c.location
        FROM course c
        JOIN student_course sc ON c.course_id = sc.course_id
        WHERE sc.student_id = %s
    """, (student_id,))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()

    # 课表初始化：13节×7天，每格为列表
    table = [[[] for _ in range(7)] for _ in range(13)]

    # 解析时间字符串
    import re
    def parse_course_time(time_str):
        # 例：1-17周:1(1,2);2(3,4)
        # 或 1,3,5,7周:1(1,2)
        if not time_str:
            return []
        result = []
        # 先分割周和节次
        parts = time_str.split(':')
        if len(parts) == 2:
            week_part, day_part = parts
        else:
            week_part, day_part = '', parts[0]
        # 解析周数
        week_list = []
        week_part = week_part.replace('周', '')
        if week_part:
            for seg in week_part.split(','):
                if '-' in seg:
                    start, end = seg.split('-')
                    week_list += list(range(int(start), int(end)+1))
                elif seg.isdigit():
                    week_list.append(int(seg))
        # 解析节次
        for seg in day_part.split(';'):
            if not seg.strip():
                continue
            m = re.match(r'(\d+)\(([\d,]+)\)', seg.strip())
            if not m:
                continue
            day = int(m.group(1))
            periods = [int(x) for x in m.group(2).split(',')]
            result.append({'day': day, 'periods': periods, 'weeks': week_list})
        return result

    for course in courses:
        slots = parse_course_time(course['time'])
        for slot in slots:
            day = slot['day']  # 1~7
            for period in slot['periods']:  # 1~13
                if 1 <= day <= 7 and 1 <= period <= 13:
                    idx_row = period - 1
                    idx_col = day - 1
                    table[idx_row][idx_col].append({
                        'name': course['name'],
                        'weeks': slot['weeks'],
                        'weeks_str': compress_weeks(slot['weeks']),
                        'location': course.get('location', ''),
                        'raw_time': course['time']
                    })

    # 返回表头和节次名
    days = ['周一','周二','周三','周四','周五','周六','周日']
    periods = [
        '第1节','第2节','第3节','第4节','第5节',
        '第6节','第7节','第8节','第9节','第10节',
        '第11节','第12节','第13节'
    ]
    # 前端需要每行第一个为节次名
    table_with_period = []
    for i in range(13):
        table_with_period.append([periods[i]] + table[i])

    return jsonify({
        'success': True,
        'table': table_with_period,
        'days': days,
        'periods': periods
    })

def compress_weeks(weeks):
    if not weeks:
        return ''
    weeks = sorted(set(weeks))
    res = []
    start = weeks[0]
    end = weeks[0]
    for w in weeks[1:]:
        if w == end + 1:
            end = w
        else:
            if start == end:
                res.append(str(start))
            else:
                res.append(f"{start}-{end}")
            start = end = w
    if start == end:
        res.append(str(start))
    else:
        res.append(f"{start}-{end}")
    return ','.join(res)