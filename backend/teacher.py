from flask import Blueprint, request, jsonify
import mysql.connector
import os
from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename
from config import db_config

teacher_bp = Blueprint('teacher', __name__)

# 获取教师账号信息
@teacher_bp.route('/api/teacher/info', methods=['GET'])
def teacher_info():
    teacher_id = request.args.get('id')
    if not teacher_id:
        return jsonify({'success': False, 'message': '缺少教师ID'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT teacher_id AS id, name, gender, birthday, title, contact FROM teacher WHERE teacher_id = %s", (teacher_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        # 格式�?? birthday 字段
        if user['birthday']:
            user['birthday'] = user['birthday'].strftime('%Y-%m-%d')
        else:
            user['birthday'] = ''
        return jsonify({'success': True, **user})
    else:
        return jsonify({'success': False, 'message': '教师不存�??'}), 404
    
@teacher_bp.route('/api/teacher/update_info', methods=['POST'])
def update_teacher_info():
    data = request.get_json()
    teacher_id = data.get('teacher_id')
    gender = data.get('gender')
    birthday = data.get('birthday')
    title = data.get('title')
    contact = data.get('contact')
    if not teacher_id:
        return jsonify({'success': False, 'message': '缺少教师ID'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE teacher SET gender=%s, birthday=%s, title=%s, contact=%s
        WHERE teacher_id=%s
    """, (gender, birthday, title, contact, teacher_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 获取当前担任班主任的班级信息
@teacher_bp.route('/api/teacher/current_head_class', methods=['GET'])
def current_head_class():
    teacher_id = request.args.get('teacher_id')
    if not teacher_id:
        return jsonify({'success': False, 'message': '缺少教师ID'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.class_id, c.name, c.college_id
        FROM class_headteacher h
        JOIN class c ON h.class_id = c.class_id
        WHERE h.teacher_id = %s
    """, (teacher_id,))
    clazz = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'class': clazz})

# 更换班主任班�??
@teacher_bp.route('/api/teacher/change_head_class', methods=['POST'])
def change_head_class():
    data = request.get_json()
    teacher_id = data.get('teacher_id')
    new_class_id = data.get('class_id')  # 新班级id
    if not teacher_id:
        return jsonify({'success': False, 'message': '缺少教师ID'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # 先删除原有的班主任记�??
    cursor.execute("DELETE FROM class_headteacher WHERE teacher_id = %s", (teacher_id,))
    # 如果选择了新班级，则插入新记�??
    if new_class_id:
        # 保证一个班只能有一个班主任
        cursor.execute("DELETE FROM class_headteacher WHERE class_id = %s", (new_class_id,))
        cursor.execute("INSERT INTO class_headteacher (class_id, teacher_id) VALUES (%s, %s)", (new_class_id, teacher_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 获取班级学生列表（支持搜索）
@teacher_bp.route('/api/teacher/class_students', methods=['GET'])
def class_students():
    class_id = request.args.get('class_id')
    keyword = request.args.get('keyword', '').strip()
    if not class_id:
        return jsonify({'success': False, 'message': '缺少班级ID'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if keyword:
        cursor.execute("""
            SELECT student_id, name, gender, birthday, contact, major
            FROM student
            WHERE class_id = %s AND (student_id LIKE %s OR name LIKE %s)
            ORDER BY student_id
        """, (class_id, f"%{keyword}%", f"%{keyword}%"))
    else:
        cursor.execute("""
            SELECT student_id, name, gender, birthday, contact, major
            FROM student
            WHERE class_id = %s
            ORDER BY student_id
        """, (class_id,))
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'students': students})

# 添加学生到班�??
@teacher_bp.route('/api/teacher/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    student_id = data.get('student_id')
    class_id = data.get('class_id')
    if not student_id or not class_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # 检查学生是否存在且未分�??
    cursor.execute("SELECT class_id FROM student WHERE student_id = %s", (student_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '学生不存�??'}), 404
    if row[0]:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '该学生已分班'}), 409
    # 更新学生班级
    cursor.execute("UPDATE student SET class_id = %s WHERE student_id = %s", (class_id, student_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 删除学生（仅移出班级，不删账号）
@teacher_bp.route('/api/teacher/remove_student', methods=['POST'])
def remove_student():
    data = request.get_json()
    student_id = data.get('student_id')
    if not student_id:
        return jsonify({'success': False, 'message': '缺少学生ID'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # 只移出班级，不删除账�??
    cursor.execute("UPDATE student SET class_id = NULL WHERE student_id = %s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 查询未分班学生（可选参数：关键字搜索）
@teacher_bp.route('/api/teacher/unassigned_students', methods=['GET'])
def unassigned_students():
    keyword = request.args.get('keyword', '').strip()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if keyword:
        cursor.execute("""
            SELECT student_id, name, gender, birthday, contact, major
            FROM student
            WHERE class_id IS NULL AND (student_id LIKE %s OR name LIKE %s)
            ORDER BY student_id
        """, (f"%{keyword}%", f"%{keyword}%"))
    else:
        cursor.execute("""
            SELECT student_id, name, gender, birthday, contact, major
            FROM student
            WHERE class_id IS NULL
            ORDER BY student_id
        """)
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'students': students})

@teacher_bp.route('/api/teacher/admin/colleges', methods=['GET'])
def admin_colleges():
    import mysql.connector
    from flask import jsonify
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT college_id, name FROM college ORDER BY college_id")
    colleges = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'colleges': colleges})

# 获取所有课程（用于下拉�??
@teacher_bp.route('/api/teacher/admin/courses', methods=['GET'])
def admin_courses():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT course_id, name FROM course ORDER BY course_id")
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'courses': courses})

# 获取所有教师（用于下拉�??
@teacher_bp.route('/api/teacher/admin/teachers', methods=['GET'])
def admin_teachers():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT teacher_id, name FROM teacher ORDER BY teacher_id")
    teachers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'teachers': teachers})

# 查询教师相关课程（含所有任课教师，支持搜索�??
@teacher_bp.route('/api/teacher/teacher_courses', methods=['GET'])
def teacher_courses_full():
    teacher_id = request.args.get('teacher_id')
    keyword = request.args.get('keyword', '').strip()
    if not teacher_id:
        return jsonify({'success': False, 'message': '缺少教师ID'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    # 查询所有该教师参与的课程，增加maxStudents和numStudents
    if keyword:
        cursor.execute("""
            SELECT DISTINCT c.course_id, c.name, c.credit, c.location, c.time, c.maxStudents,
                (SELECT COUNT(*) FROM student_course sc WHERE sc.course_id = c.course_id) AS numStudents
            FROM teacher_course tc
            JOIN course c ON tc.course_id = c.course_id
            WHERE tc.teacher_id = %s AND (c.course_id LIKE %s OR c.name LIKE %s)
            ORDER BY c.course_id
        """, (teacher_id, f"%{keyword}%", f"%{keyword}%"))
    else:
        cursor.execute("""
            SELECT DISTINCT c.course_id, c.name, c.credit, c.location, c.time, c.maxStudents,
                (SELECT COUNT(*) FROM student_course sc WHERE sc.course_id = c.course_id) AS numStudents
            FROM teacher_course tc
            JOIN course c ON tc.course_id = c.course_id
            WHERE tc.teacher_id = %s
            ORDER BY c.course_id
        """, (teacher_id,))
    courses = cursor.fetchall()
    # 查询每门课程的所有任课教�?
    for course in courses:
        cursor.execute("SELECT teacher_id FROM teacher_course WHERE course_id = %s", (course['course_id'],))
        course['teachers'] = [row['teacher_id'] for row in cursor.fetchall()]
        course['teacher_course_id'] = f"{course['course_id']}_{'_'.join(course['teachers'])}"
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'courses': courses})

# 添加任课
@teacher_bp.route('/api/teacher/add_teacher_course', methods=['POST'])
def add_teacher_course():
    data = request.get_json()
    course_id = data.get('course_id')
    teacher_id = data.get('teacher_id')
    if not course_id or not teacher_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # 检查是否已存在
    cursor.execute("SELECT * FROM teacher_course WHERE course_id=%s AND teacher_id=%s", (course_id, teacher_id))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '该教师已任该课程'})
    cursor.execute("INSERT INTO teacher_course (course_id, teacher_id) VALUES (%s, %s)", (course_id, teacher_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 修改任课（更换该课程的某个教师为另一个教师）
@teacher_bp.route('/api/teacher/edit_teacher_course', methods=['POST'])
def edit_teacher_course():
    data = request.get_json()
    course_id = data.get('course_id')
    old_teacher_id = data.get('old_teacher_id')
    new_teacher_id = data.get('teacher_id')
    if not course_id or not old_teacher_id or not new_teacher_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # 删除原教�??
    cursor.execute("DELETE FROM teacher_course WHERE course_id=%s AND teacher_id=%s", (course_id, old_teacher_id))
    # 检查新教师是否已任该课�??
    cursor.execute("SELECT * FROM teacher_course WHERE course_id=%s AND teacher_id=%s", (course_id, new_teacher_id))
    if cursor.fetchone():
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '新教师已任该课程'})
    # 添加新教�??
    cursor.execute("INSERT INTO teacher_course (course_id, teacher_id) VALUES (%s, %s)", (course_id, new_teacher_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 删除任课（删除某教师与某课程的关系）
@teacher_bp.route('/api/teacher/delete_teacher_course', methods=['POST'])
def delete_teacher_course():
    data = request.get_json()
    course_id = data.get('course_id')
    teacher_id = data.get('teacher_id')
    if not course_id or not teacher_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teacher_course WHERE course_id=%s AND teacher_id=%s", (course_id, teacher_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 创建课程并添加任课教�??
@teacher_bp.route('/api/teacher/create_and_add_course', methods=['POST'])
def create_and_add_course():
    data = request.get_json()
    teacher_id = data.get('teacher_id')
    course_id = data.get('course_id')
    name = data.get('name')
    credit = data.get('credit')
    location = data.get('location')
    time = data.get('time')
    teachers = data.get('teachers', [])
    max_students = data.get('maxStudents')  # 新增
    if not all([teacher_id, course_id, name, credit, location, time, max_students]) or not teachers:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM course WHERE course_id=%s", (course_id,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '课程号已存在'})
    cursor.execute(
        "INSERT INTO course (course_id, name, credit, location, time, maxStudents) VALUES (%s, %s, %s, %s, %s, %s)",
        (course_id, name, credit, location, time, max_students)
    )
    for tid in set(teachers):
        cursor.execute(
            "INSERT INTO teacher_course (course_id, teacher_id) VALUES (%s, %s)",
            (course_id, tid)
        )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

@teacher_bp.route('/api/teacher/delete_course', methods=['POST'])
def delete_course():
    data = request.get_json()
    teacher_id = data.get('teacher_id')
    course_id = data.get('course_id')
    if not teacher_id or not course_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # 检查是否为任课教师
    cursor.execute("SELECT * FROM teacher_course WHERE course_id=%s AND teacher_id=%s", (course_id, teacher_id))
    is_teacher = cursor.fetchone()
    if not is_teacher:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '你不是该课程的任课教师，无法删除'})
    # 查询该课程所有教师
    cursor.execute("SELECT COUNT(*) FROM teacher_course WHERE course_id=%s", (course_id,))
    teacher_count = cursor.fetchone()[0]
    if teacher_count > 1:
        # 多教师，仅解除关联
        cursor.execute("DELETE FROM teacher_course WHERE course_id=%s AND teacher_id=%s", (course_id, teacher_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': '已退出该课程（合办课程未被删除）'})
    else:
        # 只有一位教师，删除课程及关联
        cursor.execute("DELETE FROM teacher_course WHERE course_id=%s", (course_id,))
        cursor.execute("DELETE FROM course WHERE course_id=%s", (course_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'message': '课程已删除'})

# 编辑课程信息
@teacher_bp.route('/api/teacher/edit_course', methods=['POST'])
def edit_course():
    data = request.get_json()
    course_id = data.get('course_id')
    name = data.get('name')
    credit = data.get('credit')
    location = data.get('location')
    time = data.get('time')
    teachers = data.get('teachers', [])
    max_students = data.get('maxStudents')  # 新增
    if not all([course_id, name, credit, location, time, max_students]) or not teachers:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE course SET name=%s, credit=%s, location=%s, time=%s, maxStudents=%s WHERE course_id=%s",
        (name, credit, location, time, max_students, course_id)
    )
    cursor.execute("DELETE FROM teacher_course WHERE course_id=%s", (course_id,))
    for tid in set(teachers):
        cursor.execute(
            "INSERT INTO teacher_course (course_id, teacher_id) VALUES (%s, %s)",
            (course_id, tid)
        )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

@teacher_bp.route('/api/teacher/upload_avatar', methods=['POST'])
def upload_teacher_avatar():
    teacher_id = request.form.get('teacher_id')
    file = request.files.get('avatar')
    if not teacher_id or not file:
        return jsonify({'success': False, 'message': '缺少参数'}), 400

    # 只允许图片类�?
    if not file.mimetype.startswith('image/'):
        return jsonify({'success': False, 'message': '只允许上传图片文�?'}), 400

    # 目标文件夹（public/assets�?
    assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/public/assets'))
    teacher_dir = os.path.join(assets_dir, secure_filename(teacher_id))
    os.makedirs(teacher_dir, exist_ok=True)

    # 统一保存�? avatar.png
    avatar_filename = 'avatar.png'
    avatar_path = os.path.join(teacher_dir, avatar_filename)

    # �? Pillow 统一转为 png
    try:
        img = Image.open(file.stream)
        img = img.convert('RGBA')
        img.save(avatar_path, format='PNG')
    except Exception as e:
        return jsonify({'success': False, 'message': f'图片处理失败: {e}'}), 400

    # 删除旧的 jpg/jpeg/gif 文件，避免混�?
    for ext in ['jpg', 'jpeg', 'gif']:
        old_path = os.path.join(teacher_dir, f'avatar.{ext}')
        if os.path.exists(old_path):
            os.remove(old_path)

    return jsonify({'success': True, 'avatar': f'/assets/{teacher_id}/{avatar_filename}'})

# 查询自己任教课程收到的叠课申请
@teacher_bp.route('/api/teacher/overlap_applications', methods=['GET'])
def get_teacher_overlap_applications():
    teacher_id = request.args.get('teacher_id')
    if not teacher_id:
        return jsonify({'success': False, 'message': '缺少教师ID'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    # 查询自己任教的课程
    cursor.execute("SELECT course_id FROM teacher_course WHERE teacher_id=%s", (teacher_id,))
    course_ids = [row['course_id'] for row in cursor.fetchall()]
    if not course_ids:
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'applications': []})
    format_strings = ','.join(['%s'] * len(course_ids))
    cursor.execute(f"""
        SELECT oa.student_id, oa.course_id, oa.status, s.name as student_name, c.name as course_name
        FROM overlap_application oa
        JOIN student s ON oa.student_id = s.student_id
        JOIN course c ON oa.course_id = c.course_id
        WHERE oa.course_id IN ({format_strings}) AND oa.status='pending'
    """, tuple(course_ids))
    apps = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'applications': apps})

# 处理叠课申请（同意：改状态并自动选课，拒绝：删除）
@teacher_bp.route('/api/teacher/process_overlap', methods=['POST'])
def process_overlap():
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    action = data.get('action')  # 'approve' or 'reject'
    if not student_id or not course_id or action not in ('approve', 'reject'):
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    if action == 'approve':
        # 1. 更新叠课申请状态
        cursor.execute("UPDATE overlap_application SET status='approved' WHERE student_id=%s AND course_id=%s AND status='pending'", (student_id, course_id))
        # 2. 添加选课记录（如果还没有）
        cursor.execute("SELECT 1 FROM student_course WHERE student_id=%s AND course_id=%s", (student_id, course_id))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO student_course (student_id, course_id) VALUES (%s, %s)", (student_id, course_id))
            cursor.execute("UPDATE course SET numStudents = numStudents + 1 WHERE course_id=%s", (course_id,))
    else:  # reject
        cursor.execute("DELETE FROM overlap_application WHERE student_id=%s AND course_id=%s AND status='pending'", (student_id, course_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})