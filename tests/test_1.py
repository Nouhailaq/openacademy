from odoo.tests.common import TransactionCase, tagged
# from odoo.tests.common import Form, SavepointCase
import datetime

class ClassTestCourses(TransactionCase):

    def test_creation_information(self):
        course = self.env["openacademy.course"].create({
            'name': 'Course',
            'description': 'testcourse',
        })
        self.assertEqual(course.name, 'Course 1')
        self.assertEqual(course.description, 'testcourse')
