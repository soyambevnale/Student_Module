from flask import Blueprint, render_template, redirect, session

from database import get_connection


student_bp = Blueprint('student', __name__)


# -------------------- STUDENT DASHBOARD --------------------

@student_bp.route('/dashboard')
def dashboard():

    if 'student_id' not in session:
        return redirect('/login')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                first_name, last_name, email, phone,
                address, date_of_birth, location,
                qualification, tenth_percentage, tenth_year,
                twelfth_percentage, twelfth_year,
                graduation_university, graduation_percentage,
                graduation_year, experience, domain,
                skills, resume, job_positions_looking_for,
                job_location
            FROM students
            WHERE student_id = %s
        """

        cursor.execute(query, (session['student_id'],))
        student = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    if student is None:
        session.clear()
        return redirect('/login')

    total_fields = len(student)

    completed_fields = sum(
        1 for value in student.values()
        if value is not None and str(value).strip() != ''
    )

    profile_completion = round(
        (completed_fields / total_fields) * 100
    )

    return render_template(
        'dashboard.html',
        student_name=session['student_name'],
        profile_completion=profile_completion
    )


# -------------------- STUDENT PROFILE --------------------

@student_bp.route('/profile')
def profile():

    if 'student_id' not in session:
        return redirect('/login')

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                student_id, first_name, last_name, email, phone,
                address, date_of_birth, location, qualification,
                skills, experience, resume,
                registration_number,
                technical_skills, soft_skills, hobbies,
                interests, job_positions_looking_for,
                job_location, domain, certifications, projects,
                linkedin_profile, github_profile, portfolio, photo,
                approval_status,
                tenth_year, tenth_percentage,
                twelfth_year, twelfth_percentage,
                graduation_year, graduation_percentage,
                postgrad_year, postgrad_percentage,
                graduation_university, postgrad_university
            FROM students
            WHERE student_id = %s
        """

        cursor.execute(query, (session['student_id'],))
        student = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    if student is None:
        return redirect('/login')

    return render_template('profile.html', student=student)