from flask import redirect, request, url_for
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel
from auth import get_current_user


class AuthenticatedAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return get_current_user() is not None

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return get_current_user() is not None

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


def init_admin(app, db, model):
    """Attach Babel and register secured admin views for the given model."""
    Babel(app, locale_selector=lambda: 'en')
    admin = Admin(app, name="Admin", template_mode="bootstrap4",
                  index_view=AuthenticatedAdminIndexView())
    admin.add_view(AuthenticatedModelView(model, db.session,
                                          endpoint="todo_admin",
                                          name="Todos"))
    return admin
