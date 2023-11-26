import sqlite3

class Course:
    def __init__(self, course_code, course_name, instructor, capacity, enrolled_students):
        self.course_code = course_code
        self.course_name = course_name
        self.instructor = instructor
        self.capacity = capacity
        self.enrolled_students = enrolled_students

class CourseRegistrationSystem:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                course_code TEXT PRIMARY KEY,
                course_name TEXT,
                instructor TEXT,
                capacity INTEGER,
                enrolled_students TEXT
            )
        ''')
        self.conn.commit()

    def add_course(self, course_code, course_name, instructor, capacity):
        new_course = Course(course_code, course_name, instructor, capacity, [])
        self.cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?)", (new_course.course_code, new_course.course_name, new_course.instructor, new_course.capacity, ', '.join(new_course.enrolled_students)))
        self.conn.commit()
        print(f"{course_code}\t{course_name}\t{instructor}\t{capacity}已成功添加")
        return f"{course_code}\t{course_name}\t{instructor}\t{capacity}已成功添加"

    def query_course(self, search_type, search_query):
        if search_type == "*":
            self.cur.execute("SELECT * FROM courses")
        elif search_type == 'Course Code':
            self.cur.execute("SELECT * FROM courses WHERE course_code=?", (search_query,))
        elif search_type == 'Course Name':
            self.cur.execute("SELECT * FROM courses WHERE course_name LIKE ?", ('%' + search_query + '%',))
        elif search_type == 'Instructor':
            self.cur.execute("SELECT * FROM courses WHERE instructor LIKE ?", ('%' + search_query + '%',))
        else:
            return "无效的查询类型"
            

        courses_data = self.cur.fetchall()
        result = "课程名称\t课程代码\t授课教师\t课程容量\t已选学生\n"
        res = []
        if courses_data:
            for course_data in courses_data:
                course = Course(course_data[0], course_data[1], course_data[2], course_data[3], course_data[4].split(', '))
                res.append(course) 
                print(f"课程代码：{course.course_code}")
                print(f"课程名称：{course.course_name}")
                print(f"授课教师：{course.instructor}")
                print(f"课程容量：{course.capacity}")
                print(f"已选学生：{', '.join(course.enrolled_students)}")
            
            for item in res:
                result += f"{item.course_name}\t{item.course_code}\t{item.instructor}\t{item.capacity}\t{', '.join(item.enrolled_students)}\n"
            return result
        else:
            return "未找到符合条件的课程"

    def modify_course(self, course_code, new_course_name, new_instructor, new_capacity):
        self.cur.execute("SELECT * FROM courses WHERE course_code=?", (course_code,))
        course_data = self.cur.fetchone()
        if course_data:
            self.cur.execute("UPDATE courses SET course_name=?, instructor=?, capacity=? WHERE course_code=?", (new_course_name, new_instructor, new_capacity, course_code))
            self.conn.commit()
            print(f"{course_code}\t{new_course_name}\t{new_capacity}修改成功")
            return f"{course_code}\t{new_course_name}\t{new_capacity}修改成功"
        else:
            return "未找到该课程"

    def cancel_course(self, course_code):
        self.cur.execute("SELECT * FROM courses WHERE course_code=?", (course_code,))
        course_data = self.cur.fetchone()
        if course_data:
            self.cur.execute("DELETE FROM courses WHERE course_code=?", (course_code,))
            self.conn.commit()
            print(f"{course_data[0]}\t{course_data[1]}\t{course_data[2]}\t{course_data[3]}已成功取消")
            return "课程名称\t课程代码\t授课教师\t课程容量\n" + f"{course_data[0]}\t{course_data[1]}\t{course_data[2]}\t{course_data[3]}已成功取消"
        else:
            print("未找到该课程")
            return "未找到该课程"

    def close_connection(self):
        self.conn.close()
        print("数据库连接已关闭")
        return "数据库连接已关闭"

# 创建或连接数据库并初始化选课系统对象
db_name = 'course_registration.db'
registration_system = CourseRegistrationSystem(db_name)

# 添加课程示例
registration_system.add_course("CS101", "计算机科学基础", "张老师", 50)
registration_system.add_course("ENG201", "英语进阶", "王老师", 40)
registration_system.add_course("MATH301", "高等数学", "李老师", 60)
registration_system.add_course("CS201", "计算机科学进阶", "张老师", 40)
registration_system.add_course("CS301", "计算机科学高级", "张老师", 30)
registration_system.add_course("MATH101", "线性代数", "李老师", 50)
registration_system.add_course("ENG101", "英语基础", "王老师", 60)
registration_system.add_course("MATH201", "概率论", "李老师", 40)
registration_system.add_course("ENG301", "英语高级", "王老师", 30)
registration_system.add_course("CS401", "计算机科学毕业设计", "张老师", 20)

import gradio as gr

# Gradio界面函数
def course_registration(action, query_type, query, course_code, course_name, instructor, capacity):
    if action == "Add Course":
        return registration_system.add_course(course_code, course_name, instructor, int(capacity))
    elif action == "Query Course":
        return registration_system.query_course(query_type, query)
    elif action == "Modify Course":
        return registration_system.modify_course(course_code, course_name, instructor, int(capacity))
    elif action == "Cancel Course":
        return registration_system.cancel_course(course_code)
    elif action == "Close Connection":
        return registration_system.close_connection()

# 创建下拉菜单操作选项
action_options = ["Query Course", "Add Course", "Modify Course", "Cancel Course", "Close Connection"]
query_options = ["*", "Course Code", "Course Name", "Instructor"]
# 创建 Gradio 界面
iface = gr.Interface(
    fn=course_registration,
    inputs=[
        gr.inputs.Dropdown(choices=action_options, label="Action"),
        gr.inputs.Dropdown(choices=query_options, label="Query Type"),
        gr.inputs.Textbox(label="Query"),
        gr.inputs.Textbox(label="Course Code (for Add and Cancel Course)"),
        gr.inputs.Textbox(label="Course Name (for Add and Modify Course)"),
        gr.inputs.Textbox(label="Instructor (for Add and Modify Course)"),
        gr.inputs.Textbox(label="Capacity (for Add and Modify Course)"),
    ],
    outputs="text",
    title="Course Registration System",
    description="Enter course details and select action"
)

iface.launch(server_port=9999)

