""" Homework 11 """

from prettytable import PrettyTable
import os
import sys
from collections import defaultdict
import sqlite3

def file_reader(path, num_fields, seperator = ',', header = False):
    try:
        fp = open(path, "r", encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError("Could not open '{path}' for reading.")
    else:
        with fp:
            for n, line in enumerate(fp, 1):
                fields = line.rstrip('/n').split(seperator)
                if len(fields) != num_fields:
                    raise ValueError(f"'{path}' line: {n}: read {len(fields)} fields but expected different.")
                elif n == 1 and header:
                    continue
                else:
                    yield tuple([f.strip() for f in fields])

class Student: 

    def __init__(self, cwid, name, major):
        self.cwid = cwid
        self.name = name
        self.major = major
        self.course_and_grade = {}
        self.courses_completed = set()
        self.courses_remaining = set()
        self.courses_electives = set()

    def insert_grade(self, course, grade):
        self.course_and_grade[course] = grade
        if grade in ["A+","A","A-","B+","B","B-","C+","C"]:
            self.courses_completed.add(course)
            self.courses_remaining = self.courses_remaining.difference(self.courses_completed)
            if len (self.courses_electives.intersection(self.courses_completed)) > 0:
                self.courses_electives = {None}

    def student_major(self, major):
        self.courses_remaining = major.courses_remaining
        self.courses_electives = major.courses_electives

    def student_info(self):
        return [self.cwid, self.name, self.major, sorted(self.courses_completed), self.courses_remaining, self.courses_electives, self.course_and_grade]

class Instructor: 

    def __init__(self, cwid, name, department):
        self.cwid = cwid
        self.name = name
        self.department = department
        self.class_taken = {}

    def insert_grade(self, course, grade):
        if not course in self.class_taken:
            self.class_taken[course] = 0
            
        self.class_taken[course] += 1

    def instructor_info(self):
        if not len(self.class_taken):
            yield [self.cwid, self.name, self.department, "Unavailable", "Unknown"]
        else:
            print(len(self.class_taken))
            for course, taken in self.class_taken.items():
                yield [self. cwid, self.name, self.department, course, taken]


class Major: 
    def __init__(self, department):
        self.department = department
        self.courses_remaining = set()
        self.courses_electives = set()

    def insert_course(self, abv, flag):
        if flag == "E":
            self.courses_electives.add(abv)
        elif flag == "R":
            self.courses_remaining.add(abv)
        else:
            print('Flag {}'.format(flag))
            raise ValueError(f"Error: Missing data: Need either 'R' for required course or 'E' for elective course.")

    def major_info(self):
        return[self.department, sorted(self.courses_remaining), sorted(self.courses_electives)]

class Repository:

    def __init__(self, directory):
        self.directory = directory
        self.student_census = dict() 
        self.instructor_census = dict() 
        self.majors = dict()

        try:
            path = os.path.join(self.directory, "majors.txt") 
            for major, flag, abv in file_reader(path, 3, seperator='\t', header=False):
                print('{} {} {}'.format(major, flag, abv))
                if major not in self.majors:
                    self.majors[major] = Major(major)
                self.majors[major].insert_course(abv, flag)


            path = os.path.join(self.directory, "students.txt") 
            for cwid, name, department in file_reader(path, 3, seperator='\t', header=False):
                if department in self.majors:
                    self.student_census[cwid] = Student(cwid, name, department)
                else:
                    print('{} in {}'.format(department,self.majors))
                    raise ValueError("Please make sure all information entered in student.txt is appropriately filled.")

            path = os.path.join(self.directory, "instructors.txt") 
            for cwid, name, department in file_reader(path, 3, seperator='\t', header=False):
                #print(self.student_census)
                self.instructor_census[cwid] = Instructor(cwid, name, department)

            
            path = os.path.join(self.directory, "grades.txt") 
            for student_cwid, course, grade, instructor_cwid in file_reader(path, 4, seperator='\t', header=False):
                for i in self.student_census:
                    if student_cwid == i:
                        self.student_census[i].insert_grade(course,grade)
                for x in self.instructor_census:
                    if instructor_cwid == x:
                        self.instructor_census[x].insert_grade(course,grade)

        except FileNotFoundError:
            raise FileNotFoundError("Could not open '{path}' for reading.")

    def student_pretty_table(self):
        student_information = PrettyTable(field_names=["CWID", "Name", "Major", "Courses Completed", "Courses Remaining"])
        for studentbody in self.student_census.values():
            cwid, name, major, complete, remaining, electives, grades = studentbody.student_info()
            student_information.add_row([cwid,name,major,complete,remaining])
        print(student_information)
            
    def instructor_pretty_table(self):
        instructor_information = PrettyTable(field_names=["CWID", "Name", "Dept", "Course", "Students"])
        for theinstructor in self.instructor_census.values():
            for cwid, name, department, course, students in theinstructor.instructor_info():
                instructor_information.add_row([cwid, name, department, course, students])
        print(instructor_information)
        DB_file = "C:/Users/Fran/Documents/Spring 2019/Prof Rowland/810_startup.db"
        db = sqlite3.connect(DB_file)
        query = "select i.cwid, i.name, i.dept, g.course, count(g.course) as Number_of_students_who_took_the_course from HW11_instructors  as i left join HW11_grades as g on i.cwid=g.Instructor_CWID group by i.cwid, i.name, i.dept, g.course"
        for row in db.execute(query):
            print(row)

    def major_pretty_table(self):
        major_information = PrettyTable(field_names=["Department", "Courses Required", "Elective Courses"])
        for major in self.majors.values():
            major_information.add_row([major.department, major.courses_remaining,major.courses_electives])
        print(major_information)


def main():
    if __name__ == "__main__":      
        school = Repository("C:/Users/Fran/Documents/Spring 2019/Prof Rowland/")
        school.student_pretty_table()
        school.instructor_pretty_table()
        school.major_pretty_table()
main()

    
