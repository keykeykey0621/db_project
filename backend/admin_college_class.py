from flask import Blueprint, request, jsonify
import mysql.connector
from config import db_config

admin_college_class_bp = Blueprint('admin_college_class', __name__)

# 查询学院（支持搜索）
@admin_college_class_bp.route('/api/admin/colleges', methods=['GET'])
def get_colleges():
    keyword = request.args.get('keyword', '').strip()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if keyword:
        query = "SELECT college_id, name, contact FROM college WHERE college_id LIKE %s OR name LIKE %s ORDER BY college_id"
        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
    else:
        query = "SELECT college_id, name, contact FROM college ORDER BY college_id"
        cursor.execute(query)
    colleges = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'colleges': colleges})

# 添加学院
@admin_college_class_bp.route('/api/admin/college/add', methods=['POST'])
def add_college():
    data = request.get_json()
    college_id = data.get('college_id')
    name = data.get('name')
    contact = data.get('contact')
    if not college_id or not name:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT college_id FROM college WHERE college_id = %s", (college_id,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '学院号已存在'}), 409
    cursor.execute("INSERT INTO college (college_id, name, contact) VALUES (%s, %s, %s)", (college_id, name, contact))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 修改学院
@admin_college_class_bp.route('/api/admin/college/edit', methods=['POST'])
def edit_college():
    data = request.get_json()
    college_id = data.get('college_id')
    name = data.get('name')
    contact = data.get('contact')
    if not college_id or not name:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE college SET name = %s, contact = %s WHERE college_id = %s", (name, contact, college_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 删除学院
@admin_college_class_bp.route('/api/admin/college/delete', methods=['POST'])
def delete_college():
    data = request.get_json()
    college_id = data.get('college_id')
    if not college_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM college WHERE college_id = %s", (college_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 查询班级（支持搜索）
@admin_college_class_bp.route('/api/admin/classes', methods=['GET'])
def get_classes():
    keyword = request.args.get('keyword', '').strip()
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if keyword:
        query = "SELECT class_id, name, college_id FROM class WHERE class_id LIKE %s OR name LIKE %s ORDER BY class_id"
        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
    else:
        query = "SELECT class_id, name, college_id FROM class ORDER BY class_id"
        cursor.execute(query)
    classes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'classes': classes})

# 添加班级
@admin_college_class_bp.route('/api/admin/class/add', methods=['POST'])
def add_class():
    data = request.get_json()
    class_id = data.get('class_id')
    name = data.get('name')
    college_id = data.get('college_id')
    if not class_id or not name or not college_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT class_id FROM class WHERE class_id = %s", (class_id,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '班级号已存在'}), 409
    cursor.execute("INSERT INTO class (class_id, name, college_id) VALUES (%s, %s, %s)", (class_id, name, college_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 修改班级
@admin_college_class_bp.route('/api/admin/class/edit', methods=['POST'])
def edit_class():
    data = request.get_json()
    class_id = data.get('class_id')
    name = data.get('name')
    college_id = data.get('college_id')
    if not class_id or not name or not college_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE class SET name = %s, college_id = %s WHERE class_id = %s", (name, college_id, class_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

# 删除班级
@admin_college_class_bp.route('/api/admin/class/delete', methods=['POST'])
def delete_class():
    data = request.get_json()
    class_id = data.get('class_id')
    if not class_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM class WHERE class_id = %s", (class_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})