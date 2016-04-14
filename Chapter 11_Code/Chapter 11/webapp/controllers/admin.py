from flask.ext.admin import BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
from flask.ext.login import login_required, current_user

from webapp.extensions import admin_permission
from webapp.forms import CKTextAreaField


class CustomView(BaseView):
    @expose('/')
    @login_required
    @admin_permission.require(http_exception=403)
    def index(self):
        return self.render('admin/custom.html')

    @expose('/second_page')
    @login_required
    @admin_permission.require(http_exception=403)
    def second_page(self):
        return self.render('admin/second_page.html')


class CustomModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated() and admin_permission.can()


class PostView(CustomModelView):
    form_overrides = dict(text=CKTextAreaField)
    column_searchable_list = ('text', 'title')
    column_filters = ('publish_date',)

    create_template = 'admin/post_edit.html'
    edit_template = 'admin/post_edit.html'


class CustomFileAdmin(FileAdmin):
    def is_accessible(self):
        return current_user.is_authenticated() and admin_permission.can()
