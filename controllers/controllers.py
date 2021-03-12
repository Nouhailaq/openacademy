#-*- coding: utf-8 -*-
from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.http import local_redirect
from odoo.addons.portal.controllers.portal import CustomerPortal

class PortalCourse(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(PortalCourse, self)._prepare_portal_layout_values()
        domain = [('responsible_id','=',request.env.user.id)]
        course_count = request.env['openacademy.course'].search_count(domain)
        values['course_count'] = course_count
        return values

    def _course_get_page_view_values(self, course, access_token, **kwargs):
        values = {
            'page_name': 'course',
            'course': course,
        }
        return self._get_page_view_values(course, access_token, values, 'my_course_history', False, **kwargs)

    @http.route(['/my/courses'], type='http', auth="user", website=True)
    def portal_my_courses(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        courses = request.env['openacademy.course']
        domain = [('responsible_id','=',request.env.user.id)]
        Courses = courses.search(domain)
        values.update({
            'courses': Courses,
            'page_name': 'courses',
            'default_url': '/my/courses',
        })

        return request.render("openacademy.portal_my_courses", values)

    @http.route(['/my/courses/<int:course_id>'], type='http', auth="user", website=True)
    def course_followup(self, course_id=None, access_token=None, **kw):
        try:
            course_sudo = self._document_check_access('openacademy.course', course_id, access_token=None)

        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._course_get_page_view_values(course_sudo, access_token=None, **kw)
        return request.render("openacademy.portal_my_course", values)

    @http.route('/create_course', type='http', auth="user", website=True)
    def view_course_form_create(self, error=None, **kwargs):
        course = request.env['openacademy.course'].search([])

        values = {
            'course': course,
            'error': error,
        }
        return request.render("openacademy.course_submit", values)

    @http.route('/submit_course', type='http', auth="user", website=True)
    def submit_course(self, **post):
        try:
            name = post.get('name')
            unit_price = float(post.get('unit_price')) if float(post.get('unit_price', False)) != 0 else False

            data = {
                'name': name,
                'unit_price': unit_price,
                'responsible_id': request.env.user.id,
            }
            req= request.env['openacademy.course'].sudo().create(data)
            return local_redirect("/my/courses/%d" % req.id)

        except Exception as e:
            error = str(e)
            return self.view_course_form_create(error=error)

        return local_redirect("/my/courses/%d" % req.id)

    @http.route(['/update_course/<int:course_id>'], type='http', auth="user", website=True)
    def update_course(self, access_token=None, **post):
        course_id = int(post.get('id'))
        name = post.get('name')
        unit_price = float(post.get('unit_price')) if float(post.get('unit_price', False)) != 0 else False
        responsible_id = post.get('responsible_id')
        course = request.env['openacademy.course'].sudo().browse(course_id) or False
        course.sudo().write({'name': name})
        course.sudo().write({'unit_price': unit_price})
        course.sudo().write({'responsible_id': int(responsible_id)})

        return local_redirect("/my/courses")

class PortalSession(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(PortalSession, self)._prepare_portal_layout_values()
        domain = [('course_id.responsible_id','=',request.env.user.id)]
        session_count = request.env['openacademy.session'].search_count(domain)
        values['session_count'] = session_count
        return values

    def _session_get_page_view_values(self, session, access_token, **kwargs):
        print(session)
        values = {
            'page_name': 'session',
            'session': session,
        }
        return self._get_page_view_values(session, access_token, values, 'my_session_history', False, **kwargs)

    @http.route(['/my/sessions'], type='http', auth="user", website=True)
    def portal_my_sessions(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        s = request.env['openacademy.session']
        domain = [('course_id.responsible_id','=',request.env.user.id)]
        sessions = s.search(domain)
        values.update({
            'sessions': sessions,
            'page_name': 'sessions',
            'default_url': '/my/sessions',
        })
        return request.render("openacademy.portal_my_sessions", values)

    @http.route(['/my/session/<int:session_id>'], type='http', auth="user", website=True)
    def session_followup(self, session_id=None, access_token=None, **kw):
        try:
            session_sudo = self._document_check_access('openacademy.session', session_id, access_token=None)


        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._session_get_page_view_values(session_sudo, access_token=None, **kw)
        attendees = request.env['res.partner'].sudo().search([('session_ids.id', '=', session_id)])
        values.update({
            'page_name': 'sessions',
            'attendees': attendees,
        })
        return request.render("openacademy.portal_my_session", values)

    @http.route('/create_session', type='http', auth="user", website=True)
    def view_session_form_create(self, error=None, **kwargs):
        session = request.env['openacademy.session'].search([])
        courses = request.env['openacademy.course'].search([('responsible_id','=',request.env.user.id)])
        partners = request.env['res.partner'].search([])

        values = {
            'session': session,
            'courses' : courses,
            'partners' : partners,
            'error': error,
        }
        return request.render("openacademy.session_create", values)

    @http.route('/session_submit', type='http', auth="user", website=True)
    def session_submit(self, **post):
        try:
            name = post.get('name')
            course_id = int(post.get('course_id')) if int(post.get('course_id', False)) != 0 else False
            start_date = post.get('start_date') if post.get('start_date', False) != 0 else False
            duration = float(post.get('duration')) if float(post.get('duration', False)) != 0 else False
            seats = int(post.get('seats')) if int(post.get('seats', False)) != 0 else False
            a_ids = request.httprequest.form.getlist('attendee_ids')
            attendee_ids = []
            for a in a_ids:
                attendee_ids.append(int(a))
            data = {
                'name': name,
                'course_id': course_id,
                'start_date' : start_date,
                'duration': duration,
                'seats': seats,
                'attendee_ids': attendee_ids,
            }
            req= request.env['openacademy.session'].sudo().create(data)
            return local_redirect("/my/session/%d" % req.id)

        except Exception as e:
            error = str(e)
            return self.view_session_form_create(error=error)

    @http.route(['/my/session/update/<int:session_id>'], type='http', auth="user", website=True)
    def session_update_followup(self, session_id=None, access_token=None, **kw):
        try:
            session_sudo = self._document_check_access('openacademy.session', session_id, access_token=None)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._session_get_page_view_values(session_sudo, access_token=None, **kw)
        partners = request.env['res.partner'].sudo().search([])
        courses = request.env['openacademy.course'].sudo().search([('responsible_id','=',request.env.user.id)])
        values.update({
            'page_name': 'sessions',
            'partners': partners,
            'courses' : courses,
        })
        return request.render("openacademy.session_update", values)

    @http.route('/session_update_submit', type='http', auth="user", website=True)
    def session_update_submit(self, **post):
        try:
            session_id = int(post.get('id'))
            name = post.get('name')
            course_id = int(post.get('course_id')) if int(post.get('course_id', False)) != 0 else False
            start_date = post.get('start_date') if post.get('start_date', False) != 0 else False
            duration = float(post.get('duration')) if float(post.get('duration', False)) != 0 else False
            seats = int(post.get('seats')) if int(post.get('seats', False)) != 0 else False
            a_ids = request.httprequest.form.getlist('attendee_ids')
            attendee_ids = []
            for a in a_ids:
                attendee_ids.append(int(a))

            session = request.env['openacademy.session'].sudo().browse(session_id) or False
            session.sudo().write({'name': name})
            session.sudo().write({'course_id': course_id})
            session.sudo().write({'start_date': start_date})
            session.sudo().write({'duration': duration})
            session.sudo().write({'seats': seats})
            session.sudo().write({'attendee_ids': attendee_ids})

            return local_redirect("/my/session/update/%d" % session_id)

        except Exception as e:
            error = str(e)
            return self.view_session_form_create(error=error)

    @http.route("/my/session/delete/<int:session_id>", type='http', auth="user", website=True)
    def session_delete(self, session_id=None, access_token=None, **kw):
        try:
            session_sudo = self._document_check_access('openacademy.session', session_id, access_token=None)
        except (AccessError, MissingError):
            return request.redirect('/my')
        session_sudo.unlink()
        return local_redirect("/my/sessions")