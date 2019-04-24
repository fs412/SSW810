""" Student Repository Website """

import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/student_repository')
def student_courses():
    sqlfile = 'C:/Users/Fran/Documents/Spring 2019/Prof Rowland/final/810_startup.db'
    query = """select i.cwid, i.name, i.dept, g.course, count(g.course) as Number_of_students_who_took_the_course
from HW11_instructors  as i left join HW11_grades as g on i.cwid=g.Instructor_CWID
group by i.cwid, i.name, i.dept, g.course"""

    conn = sqlite3.connect(sqlfile)
    c = conn.cursor()
    c.execute(query)
    results = c.fetchall()
    data = [{'cwid': cwid, 'name': name, 'department': department, 'course': course, 'total':total}
            for cwid, name, department, course, total in results]

    conn.close()

    return render_template('parameters.html',
                           title="Stevens Repository",
                           my_header="Stevens Repository",
                           my_param="My custom parameter",
                           table_title="Number of students by course and instructor",
                           students=data)

app.run(debug=True)