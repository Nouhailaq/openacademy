from datetime import timedelta
from odoo import models, fields, api, exceptions

class Course(models.Model):
    _name = 'openacademy.course'
    _description = "OpenAcademy Courses"

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    unit_price = fields.Float(string="Unit Price")
    responsible_id = fields.Many2one('res.users',ondelete='set null', string="Responsible", index=True)
    session_ids = fields.One2many('openacademy.session', 'course_id', string="Sessions")


    def create_course_invoice(self):
        self.env['account.move'].create({
            'invoice_origin': self.name,
            'partner_id': self.responsible_id.partner_id.id,
            'type': 'in_invoice',
        })


    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count([('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        return super(Course, self).copy(default)

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the course should not be the description"),

        ('name_unique',
         'UNIQUE(name)',
         "The course title must be unique"),
    ]

class Session(models.Model):
    _name = 'openacademy.session'
    _description = "OpenAcademy Sessions"

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help="Duration in days")
    seats = fields.Integer(string="Number of seats")
    active = fields.Boolean(default=True)
    color = fields.Integer()

    instructor_id = fields.Many2one('res.partner', string="Instructor", domain=['|', ('instructor', '=', True), ('category_id.name', 'ilike', "Teacher")])

    course_id = fields.Many2one('openacademy.course', ondelete='cascade', string="Course", required=True)
    attendee_ids = fields.Many2many('res.partner', string="Attendees")

    taken_seats = fields.Float(string="Taken seats", compute='_taken_seats')
    end_date = fields.Date(string="End Date", store=True, compute='_get_end_date', inverse='_set_end_date')
    attendees_count = fields.Integer(string="Attendees count", compute='_get_attendees_count', store=True)
    state = fields.Selection([
        ('session started', 'Session Started'),
        ('session en cours', 'Session En Cours'),
        ('session finished', 'Session Finished')
    ], string='Status', index=True, readonly=True, default='session started')

    def create_session_invoices(self):
        date_time = self.start_date.strftime("%m/%d/%Y")
        for r in self.attendee_ids:
            self.env['account.move'].create({
                'invoice_origin':self.course_id.name+"/"+self.name+" du date "+date_time,
                'partner_id': r.id,
                'amount_total' : self.course_id.unit_price,
                'invoice_line_ids' : [(0, 0, {
                'product_id': self.env.ref('openacademy.c_product').id,
                'quantity': self.duration,
                'price_unit': self.course_id.unit_price,
                 })],
                'type': 'out_invoice',
            })


    @api.depends('seats', 'attendee_ids')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats

    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': "Incorrect 'seats' value",
                    'message': "The number of available seats may not be negative",
                },
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': "Too many attendees",
                    'message': "Increase seats or remove excess attendees",
                },
            }

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            # Add duration to start_date, but: Monday + 5 days = Saturday, so
            # subtract one second to get on Friday instead
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = r.start_date + duration

    def _set_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the difference between dates, but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            r.duration = (r.end_date - r.start_date).days + 1

    @api.depends('attendee_ids')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)

    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                raise exceptions.ValidationError("A session's instructor can't be an attendee")

    def action_en_cours(self):
        for rec in self:
            rec.state = 'session en cours'

    def action_finished(self):
        for rec in self:
            rec.state = 'session finished'


class StudentRecord(models.Model):
    _name = "openacademy.student"
    name = fields.Char(string='Name', required=True)
    middle_name = fields.Char(string='Middle Name', required=True)
    last_name= fields.Char(string='Last Name', required=True)
    photo = fields.Binary(string='Photo')
    student_age = fields.Integer(string='Age')
    student_dob = fields.Date(string="Date of Birth")
    student_gender = fields.Selection([('m', 'Male'), ('f', 'Female'), ('o', 'Other')], string='Gender')
    student_blood_group = fields.Selection( [('A+', 'A+ve'), ('B+', 'B+ve'), ('O+', 'O+ve'),('AB+', 'AB+ve'),('A-', 'A-ve'),('B-', 'B-ve'), ('O-', 'O-ve'), ('AB-', 'AB-ve')],string='Blood Group')
    nationality = fields.Many2one('res.country', string='Nationality')