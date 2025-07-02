from flask import Blueprint, request, jsonify
import mysql.connector
from config import db_config
from werkzeug.security import generate_password_hash, check_password_hash

admin_account_bp = Blueprint('admin_account', __name__)

#账号信息接口  
@admin_account_bp.route('/api/admin/info', methods=['GET'])
def account_info():
    user_id = request.args.get('id')
    if not user_id:
        return jsonify({'success': False, 'message': '缺少账号ID'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, password, role FROM login_account WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify({'success': True, 'id': user['id'], 'password': user['password'], 'role': user['role']})
    else:
        return jsonify({'success': False, 'message': '账号不存在'}), 404

# 查询账号（支持搜索和首字母排序）
@admin_account_bp.route('/api/admin/accounts', methods=['GET'])
def get_accounts():
    keyword = request.args.get('keyword', '').strip()
    exclude_id = request.args.get('exclude_id', '').strip()
    print(exclude_id)
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if keyword:
        if exclude_id:
            query = "SELECT id, role FROM login_account WHERE id LIKE %s AND id != %s ORDER BY id"
            cursor.execute(query, (f"%{keyword}%", exclude_id))
        else:
            query = "SELECT id, role FROM login_account WHERE id LIKE %s ORDER BY id"
            cursor.execute(query, (f"%{keyword}%",))
    else:
        if exclude_id:
            query = "SELECT id, role FROM login_account WHERE id != %s ORDER BY id"
            cursor.execute(query, (exclude_id,))
        else:
            query = "SELECT id, role FROM login_account ORDER BY id"
            cursor.execute(query)
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'accounts': accounts})

# 修改账号密码（无需原始密码）
@admin_account_bp.route('/api/admin/account/change_password', methods=['POST'])
def admin_change_password():
    data = request.get_json()
    user_id = data.get('id')
    new_password = data.get('new_password')
    if not user_id or not new_password:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    hashed_password = generate_password_hash(new_password)
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE login_account SET password = %s WHERE id = %s", (hashed_password, user_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 删除账号
@admin_account_bp.route('/api/admin/account/delete', methods=['POST'])
def admin_delete_account():
    data = request.get_json()
    user_id = data.get('id')
    if not user_id:
        return jsonify({'success': False, 'message': '缺少账号ID'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # 1. 查询该学生选了哪些课（如果是学生）
    cursor.execute("SELECT course_id FROM student_course WHERE student_id = %s", (user_id,))
    affected_courses = [row[0] for row in cursor.fetchall()]

    # 2. 删除 student_course 选课关系
    cursor.execute("DELETE FROM student_course WHERE student_id = %s", (user_id,))

    # 3. 删除 student/teacher 表
    cursor.execute("DELETE FROM student WHERE student_id = %s", (user_id,))
    cursor.execute("DELETE FROM teacher WHERE teacher_id = %s", (user_id,))

    # 4. 删除账号表
    cursor.execute("DELETE FROM login_account WHERE id = %s", (user_id,))

    # 5. 更新受影响课程的选课人数
    for course_id in affected_courses:
        cursor.execute(
            "UPDATE course SET numStudents = (SELECT COUNT(*) FROM student_course WHERE course_id=%s) WHERE course_id=%s",
            (course_id, course_id)
        )

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 添加账号
@admin_account_bp.route('/api/admin/account/add', methods=['POST'])
def admin_add_account():
    data = request.get_json()
    user_id = data.get('id')
    password = data.get('password')
    role = data.get('role')
    name = data.get('name', None)
    if not user_id or not password or not role:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    if role in ['student', 'teacher'] and not name:
        return jsonify({'success': False, 'message': '请填写姓名'}), 400
    # 账号前缀校验
    if (role == 'admin' and not user_id.startswith('A')) or \
       (role == 'teacher' and not user_id.startswith('T')) or \
       (role == 'student' and not user_id.startswith('S')):
        return jsonify({'success': False, 'message': '账号开头与职责不符'}), 400
    hashed_password = generate_password_hash(password)
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # 检查账号是否已存在
    cursor.execute("SELECT id FROM login_account WHERE id = %s", (user_id,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '账号已存在'}), 409
    #插入账号表
    cursor.execute("INSERT INTO login_account (id, password, role) VALUES (%s, %s, %s)", (user_id, hashed_password, role))
    #同步插入 student 或 teacher 表
    if role == 'student':
        cursor.execute("INSERT INTO student (student_id, name) VALUES (%s, %s)", (user_id, name))
    elif role == 'teacher':
        cursor.execute("INSERT INTO teacher (teacher_id, name) VALUES (%s, %s)", (user_id, name))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})