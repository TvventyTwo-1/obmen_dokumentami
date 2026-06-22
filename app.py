# app.py
from flask import Flask, g, session
import db
from datetime import timedelta
from subjects import bp as subjects_bp
from auth import bp as auth_bp
from main import bp as main_bp
from docs import bp as docs_bp
from notifications import bp as notif_bp
from schedule import bp as schedule_bp
from admin import bp as admin_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret-key-change-me"

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(notif_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(schedule_bp)
    app.jinja_env.globals["timedelta"] = timedelta
    app.register_blueprint(admin_bp)

    @app.before_request
    def load_user():
        g.user = None
        g.main_role = None
        g.roles = []
        g.groups = []
        g.active_group = None
        g.unread_count = 0

        uid = session.get("user_id")
        if uid:
            g.user = db.get_user_by_id(uid)
            g.roles = db.get_user_roles(uid)
            g.groups = db.get_user_groups(uid)
            g.unread_count = db.count_unread_notifications(uid)
            g.main_role = db.pick_main_role(g.roles)

            # выбранная группа в сессии, иначе первая
            group_id = session.get("active_group_id")
            if group_id:
                g.active_group = next((x for x in g.groups if x["id"] == group_id), None)
            if not g.active_group and g.groups:
                g.active_group = g.groups[0]
                session["active_group_id"] = g.active_group["id"]

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
