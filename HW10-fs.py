""" Homework 10 """

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
                if major not in self.majors:
                    self.majors[major] = Major(major)
                self.majors[major].insert_course(abv, flag)


            path = os.path.join(self.directory, "students.txt") 
            for cwid, name, department in file_reader(path, 3, seperator='\t', header=False):
                if department in self.majors:
                    self.student_census[cwid] = Student(cwid, name, department)
                else:
                    raise ValueError("Please make sure all information entered in student.txt is appropriately filled.")

            path = os.path.join(self.directory, "instructors.txt") 
            for cwid, name, department in file_reader(path, 3, seperator='\t', header=False):
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
            
    def instructor_pretty_table(self):
        instructor_information = PrettyTable(field_names=["CWID", "Name", "Dept", "Course", "Students"])
        for theinstructor in self.instructor_census.values():
            for cwid, name, department, course, students in theinstructor.instructor_info():
                instructor_information.add_row([cwid, name, department, course, students])

    def major_pretty_table(self):
        major_information = PrettyTable(field_names=["Department", "Courses Required", "Elective Courses"])
        for major in self.majors.values():
            major_information.add_row([major.department, major.courses_remaining,major.courses_electives])

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

class MajorTest(unittest.TestCase):
    def test_major(self):
        SYS = Major("SYS")
        SYS.insert_course("SSW 540", "R")
        SYS.insert_course("SSW 810", "E")
        courses_remaining = {"SSW 540"}
        courses_electives = {"SSW 810"}
        self.assertTrue(SYS.courses_remaining == courses_remaining)
        self.assertTrue(SYS.courses_electives == courses_electives)
        with self.assertRaises(ValueError):
            SYS.insert_course("SSW 707", "n/a")   


def main():
    if __name__ == "__main__":      
        unittest.main(exit=False, verbosity=2)
        school = Repository("C:/Users/Fran/Documents/Spring 2019/Prof Rowland/")
        school.student_pretty_table()
        school.instructor_pretty_table()
        school.major_pretty_table()
main()

    
