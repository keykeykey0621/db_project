from werkzeug.security import generate_password_hash, check_password_hash

test = '123456'
print(generate_password_hash(test))
print(check_password_hash(generate_password_hash(test),test))
