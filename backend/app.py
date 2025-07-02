from flask import Flask, request, jsonify
import mysql.connector
from config import db_config
from flask_cors import CORS

from werkzeug.security import generate_password_hash, check_password_hash #密码加密
#在后端的generate_password文件中可以测试

from admin_account import admin_account_bp
from admin_college_class import admin_college_class_bp
from teacher import teacher_bp
from student import student_bp

app = Flask(__name__)
CORS(app) #跨域连接

#注册或添加用户时使用
def encrypt_password(plain_password):
    return generate_password_hash(plain_password)

#登录时校验密�?
def verify_password(plain_password, hashed_password):
    return check_password_hash(hashed_password, plain_password)

#登录接口
@app.route('/api/login',methods=['POST'])
def login():
    #获取输入的账号和密码
    data = request.get_json()
    user_id = data.get('username')
    password = data.get('password')

    #连接数据�?
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    #sql语句
    query = "SELECT * FROM login_account WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and verify_password(password, user['password']):
        return jsonify({'success': True, 'user_id':user_id,'role': user['role']})
    else:
        return jsonify({'success': False, 'message': '账号密码错误'}), 401


#修改密码接口
@app.route('/api/account/change_password', methods=['POST'])
def account_change_password():
    data = request.get_json()
    user_id = data.get('id')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    if not user_id or not old_password or not new_password:
        return jsonify({'success': False, 'message': '缺少参数'}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT password FROM login_account WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '账号不存�?'}), 404

    if not check_password_hash(user['password'], old_password):
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'message': '原始密码错误'}), 403

    hashed_password = generate_password_hash(new_password)
    cursor2 = conn.cursor()
    cursor2.execute("UPDATE login_account SET password = %s WHERE id = %s", (hashed_password, user_id))
    conn.commit()
    cursor2.close()
    conn.close()
    return jsonify({'success': True, 'password': hashed_password})

app.register_blueprint(admin_account_bp)
app.register_blueprint(admin_college_class_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(student_bp)

if __name__ == '__main__':
    app.run(debug=True)