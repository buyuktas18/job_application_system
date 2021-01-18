from flask import Flask, render_template
import views

app = Flask(__name__)
app.secret_key = 'super secret key'

def create_app():
    app = Flask(__name__)
    app.add_url_rule("/", view_func=views.home_page)
    app.add_url_rule("/job_page", view_func=views.job_page, methods=['GET', 'POST'])
    app.add_url_rule("/annons", view_func=views.annons_page, methods=['GET', 'POST'])
    app.add_url_rule("/login", view_func=views.login_page, methods=['GET', 'POST'])
    app.add_url_rule("/app_login", view_func=views.app_login_page, methods=['GET', 'POST'])
    app.add_url_rule("/profile", view_func=views.profile_page, methods=['GET', 'POST'])
    app.add_url_rule("/announcements", view_func=views.ans_page, methods=['GET', 'POST'])
    app.add_url_rule("/confirm", view_func=views.confirm_page, methods=['GET', 'POST'])
    app.add_url_rule("/logout", view_func=views.logout, methods=['GET', 'POST'])
    app.add_url_rule("/cprofile", view_func=views.cprofile_page, methods=['GET', 'POST'])
    app.add_url_rule("/download", view_func=views.download, methods=['GET', 'POST'])
    return app

if __name__ == "__main__":
    app = create_app()
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host="0.0.0.0", port=8000, debug=True)
