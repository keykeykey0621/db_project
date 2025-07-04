-- 账号表
CREATE TABLE login_account (
  id VARCHAR(50) PRIMARY KEY,
  password VARCHAR(1000) NOT NULL,
  role VARCHAR(20)
);

-- 学院
CREATE TABLE college (
  college_id VARCHAR(20) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  contact VARCHAR(100)
);

-- 班级
CREATE TABLE class (
  class_id VARCHAR(20) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  college_id VARCHAR(20),
  FOREIGN KEY (college_id) REFERENCES college(college_id) ON DELETE CASCADE
);

-- 学生
CREATE TABLE student (
  student_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  gender VARCHAR(10),
  birthday DATE,
  contact VARCHAR(100),
  major VARCHAR(100),
  class_id VARCHAR(20),
  FOREIGN KEY (student_id) REFERENCES login_account(id) ON DELETE CASCADE,
  FOREIGN KEY (class_id) REFERENCES class(class_id) ON DELETE CASCADE
);

-- 教师
CREATE TABLE teacher (
  teacher_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  gender VARCHAR(10),
  birthday DATE,
  title VARCHAR(50),
  contact VARCHAR(100),
  FOREIGN KEY (teacher_id) REFERENCES login_account(id) ON DELETE CASCADE
);

-- 班主任
CREATE TABLE class_headteacher (
  class_id VARCHAR(20) PRIMARY KEY,
  teacher_id VARCHAR(50) UNIQUE,
  FOREIGN KEY (class_id) REFERENCES class(class_id) ON DELETE CASCADE,
  FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id) ON DELETE CASCADE
);

-- 课程
CREATE TABLE course (
  course_id VARCHAR(20) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  credit DECIMAL(3,1),
  location VARCHAR(100),
  time VARCHAR(100),
  maxStudents int NOT NULL,
  numStudents int DEFAULT 0
);

-- 教师授课（多对多）
CREATE TABLE teacher_course (
  teacher_id VARCHAR(50),
  course_id VARCHAR(20),
  PRIMARY KEY (teacher_id, course_id),
  FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE
);

-- 学生选课（多对多）
CREATE TABLE student_course (
  student_id VARCHAR(50),
  course_id VARCHAR(20),
  PRIMARY KEY (student_id, course_id),
  FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE
);

-- 叠课申请表
CREATE TABLE overlap_application (
    student_id VARCHAR(32) NOT NULL,
    course_id VARCHAR(32) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'pending',
    PRIMARY KEY (student_id, course_id)
);

INSERT INTO login_account (id, password, role)
VALUES ('A001', 'scrypt:32768:8:1$1rVmpASOrfTegXNO$b7880e1506a74449809548266bb5cd1dd1adbac7dc2638bbb84f79ce5343f1c59e53b4d4fcdbc315c562909f75ab7385ea2a087b755c6cb1be1368c5c16dfef3', 'admin');
