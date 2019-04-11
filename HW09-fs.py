""" Homework 9 """

from prettytable import PrettyTable
import unittest 
import os
import sys
from collections import defaultdict

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
                    yield tuple(fields)

class Student: 

    def __init__(self, cwid, name, major):
        self.cwid = cwid
        self.name = name
        self.major = major
        self.course_and_grade = {}

    def insert_grade(self, course, grade):
        self.course_and_grade[course] = grade

    def student_info(self):
        return [self.cwid, self.name, self.course_and_grade]

class Instructor: 

    def __init__(self, cwid, name, department):
        self.cwid = cwid
        self.name = name
        self.department = department
        self.class_taken = {}

    def insert_grade(self, course, grade):
        if course in self.class_taken:
            self.class_taken[course] += 1
        else:
            self.class_taken[course] = 1

    def instructor_info(self):
        if not len(self.class_taken):
            yield [self.cwid, self.name, self.department, "Unavailable", "Unknown"]
        else:
            print(len(self.class_taken))
            for course, taken in self.class_taken.items():
                yield [self. cwid, self.name, self.department, course, taken]

class Repository:

    def __init__(self, directory):
        self.directory = directory
        self.student_census = list()
        self.instructor_census = list()

        try:
            path = os.path.join(self.directory, "students.txt") 
            for cwid, name, major in file_reader(path, 3, seperator='\t', header=False):
                self.student_census.append(Student(cwid,name,major))
            path = os.path.join(self.directory, "instructors.txt") 
            for cwid, name, department in file_reader(path, 3, seperator='\t', header=False):
                self.instructor_census.append(Instructor(cwid,name,department))
            path = os.path.join(self.directory, "grades.txt") 
            for student_cwid, course, grade, instructor_cwid in file_reader(path, 4, seperator='\t', header=False):
                for i in self.student_census:
                    if student_cwid == i.cwid:
                        i.insert_grade(course,grade)
                for x in self.instructor_census:
                    if instructor_cwid == x.cwid:
                        x.insert_grade(course)

        except FileNotFoundError:
            
            raise FileNotFoundError("Could not open '{path}' for reading.")

    def student_pretty_table(self):
        student_information = PrettyTable(field_names=["CWID", "Name", "Course"])
        for studentbody in self.student_census:
            cwid, name, the_courses = studentbody.student_info()
            if the_courses == []:
                the_courses = "n/a"
            student_information.add_row([cwid,name,the_courses])
        print("Student")
        print(studentbody)

    def instructor_pretty_table(self):
        instructor_information = PrettyTable(field_names=["CWID", "Name", "Dept", "Course", "Students"])
        for theinstructor in self.instructor_census:
            for amount_of_courses in theinstructor.instructor_info():
                cwid, name, department, course, students = amount_of_courses
                instructor_information.add_row([cwid, name, department, course, students])
        print ("Instructor")
        print(instructor_information)

class StudentTest(unittest.TestCase):
    def test_Student(self):
        s=Student(10115, "Wyatt, X", "SFEN")
        s.insert_grade('c1','A')
        s.insert_grade('c2','B')
        s.insert_grade('c3','C')
        self.assertEqual(s.student_info(), [10115, 'Wyatt, X', {'c1': 'A', 'c2': 'B', 'c3': 'C'}])

class InstructorTest(unittest.TestCase):
    def test_Instructor(self):
        s=Instructor(98764, "Feynman, R", "SFEN")
        g=s.instructor_info()
        self.assertEqual(next(g),[98764, 'Feynman, R', 'SFEN', 'Unavailable', 'Unknown'])

class RepositoryTest(unittest.TestCase):
    def test_Repository(self):
        r=Repository(".")
        self.assertEqual(len(r.student_census),10)

def main():
    if __name__ == "__main__":
        unittest.main(exit=False, verbosity=2)
        school = Repository("C:/Users/Fran/Documents/Spring 2019/Prof Rowland")
        school = Repository(".")
        school.student_pretty_table()
        school.instructor_pretty_table()
main()