from flask import Flask, render_template

from database import get_connection

from routes.auth import auth_bp
from routes.student import student_bp
from routes.placement import placement_bp


app = Flask(__name__)

app.secret_key = 'student_placement_secret_key'


# -------------------- REGISTER BLUEPRINTS --------------------

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(placement_bp)


app.add_url_rule(
    '/register',
    endpoint='register',
    view_func=app.view_functions['auth.register'],
    methods=['GET', 'POST']
)

app.add_url_rule(
    '/login',
    endpoint='login',
    view_func=app.view_functions['auth.login'],
    methods=['GET', 'POST']
)

app.add_url_rule(
    '/logout',
    endpoint='logout',
    view_func=app.view_functions['auth.logout']
)

app.add_url_rule(
    '/dashboard',
    endpoint='dashboard',
    view_func=app.view_functions['student.dashboard']
)

app.add_url_rule(
    '/profile',
    endpoint='profile',
    view_func=app.view_functions['student.profile']
)

app.add_url_rule(
    '/jobs',
    endpoint='jobs',
    view_func=app.view_functions['placement.jobs']
)

app.add_url_rule(
    '/apply/<int:job_id>',
    endpoint='apply_job',
    view_func=app.view_functions['placement.apply_job']
)

app.add_url_rule(
    '/applied-jobs',
    endpoint='applied_jobs',
    view_func=app.view_functions['placement.applied_jobs']
)

app.add_url_rule(
    '/interview-status',
    endpoint='interview_status',
    view_func=app.view_functions['placement.interview_status']
)

app.add_url_rule(
    '/opt-out-placement',
    endpoint='opt_out_placement',
    view_func=app.view_functions['placement.opt_out_placement'],
    methods=['POST']
)


# -------------------- HOME --------------------

@app.route('/')
def home():
    return render_template('home.html')


# -------------------- DATABASE TEST --------------------

@app.route('/test-db')
def test_db():

    connection = get_connection()

    if connection:
        connection.close()
        return 'Database Connected Successfully!'

    return 'Database Connection Failed!'


# -------------------- RUN APPLICATION --------------------

if __name__ == '__main__':
    app.run(debug=True)