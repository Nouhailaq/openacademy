# -*- coding: utf-8 -*-
from odoo import fields, models, api

class User(models.Model):
    _inherit = 'res.users'
    course_number = fields.Integer(compute='compute_course_number', string="Number of Course")
    course_ids = fields.One2many('openacademy.course', 'responsible_id' , string="Courses")


    def course_list(self):
        action = self.env.ref('openacademy.course_list_action').read()[0]
        action['domain']=[('id','in',self.course_ids.ids)]
        action['views'] = [(self.env.ref('openacademy.course_tree_view').id, 'tree'),
                           (self.env.ref('openacademy.course_form_view').id, 'form')]
        action['context']={'default_responsible_id':self.id}
        return action



    @api.depends('course_ids')
    def compute_course_number(self):
        for r in self:
            r.course_number = len(self.course_ids)
