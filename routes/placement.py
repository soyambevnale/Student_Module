from flask import (
    Blueprint, render_template, redirect,
    session, flash
)

from database import get_connection


placement_bp = Blueprint('placement', __name__)


# -------------------- AVAILABLE JOBS --------------------

@placement_bp.route('/jobs')
def jobs():

    if 'student_id' not in session:
        return redirect('/login')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT approval_status
            FROM students
            WHERE student_id = %s
            """,
            (session['student_id'],)
        )

        student = cursor.fetchone()

        if student is None or student['approval_status'] != 'Approved':
            session.clear()
            return redirect('/login')

        query = """
            SELECT *
            FROM jobs
            WHERE job_status = 'Open'
            ORDER BY posted_at DESC
        """

        cursor.execute(query)
        job_list = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template('jobs.html', jobs=job_list)


# -------------------- APPLY FOR JOB --------------------

@placement_bp.route('/apply/<int:job_id>')
def apply_job(job_id):

    if 'student_id' not in session:
        return redirect('/login')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        student_id = session['student_id']

        cursor.execute(
            """
            SELECT approval_status
            FROM students
            WHERE student_id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if student is None or student['approval_status'] != 'Approved':
            flash("Your account is not approved.")
            return redirect('/login')

        cursor.execute(
            """
            SELECT job_id
            FROM jobs
            WHERE job_id = %s AND job_status = 'Open'
            """,
            (job_id,)
        )

        job = cursor.fetchone()

        if job is None:
            flash("This job is not available.")
            return redirect('/jobs')

        cursor.execute(
            """
            SELECT application_id
            FROM applications
            WHERE student_id = %s AND job_id = %s
            """,
            (student_id, job_id)
        )

        existing_application = cursor.fetchone()

        if existing_application:
            flash("You have already applied for this job.")
            return redirect('/jobs')

        cursor.execute(
            """
            INSERT INTO applications (student_id, job_id)
            VALUES (%s, %s)
            """,
            (student_id, job_id)
        )

        connection.commit()

        flash("Job application submitted successfully!")

    finally:
        cursor.close()
        connection.close()

    return redirect('/jobs')


# -------------------- APPLIED JOBS --------------------

@placement_bp.route('/applied-jobs')
def applied_jobs():

    if 'student_id' not in session:
        return redirect('/login')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                applications.application_id,
                applications.application_date,
                applications.status,
                jobs.company_name,
                jobs.position,
                jobs.package,
                jobs.location,
                jobs.domain
            FROM applications
            INNER JOIN jobs
            ON applications.job_id = jobs.job_id
            WHERE applications.student_id = %s
            ORDER BY applications.application_date DESC
        """

        cursor.execute(query, (session['student_id'],))

        application_list = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        'applied_jobs.html',
        applications=application_list
    )


# -------------------- INTERVIEW STATUS --------------------

@placement_bp.route('/interview-status')
def interview_status():

    if 'student_id' not in session:
        return redirect('/login')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                interviews.interview_id,
                jobs.company_name,
                jobs.position,
                interviews.interview_date,
                interviews.interview_time,
                interviews.location,
                interviews.status,
                interviews.result
            FROM interviews
            JOIN jobs
            ON interviews.job_id = jobs.job_id
            WHERE interviews.student_id = %s
            ORDER BY interviews.interview_date DESC
        """

        cursor.execute(query, (session['student_id'],))
        interviews = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        'interview_status.html',
        interviews=interviews
    )


# -------------------- OPT OUT FROM PLACEMENT --------------------

@placement_bp.route('/opt-out-placement', methods=['POST'])
def opt_out_placement():

    if 'student_id' not in session:
        return redirect('/login')

    connection = get_connection()
    cursor = connection.cursor()

    try:
        query = """
            UPDATE students
            SET placement_opt_out = 1
            WHERE student_id = %s
        """

        cursor.execute(query, (session['student_id'],))
        connection.commit()

    finally:
        cursor.close()
        connection.close()

    flash("You have successfully opted out from placement.")

    return redirect('/dashboard')
