import os
import re
from datetime import date

from flask import (
    Blueprint, render_template, request,
    redirect, session, url_for
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from database import get_connection


auth_bp = Blueprint('auth', __name__)


# -------------------- COMMON FUNCTION --------------------

def show_error(field, message):
    return render_template(
        'register.html',
        form_data=request.form,
        errors={field: message}
    )


# -------------------- STUDENT REGISTRATION --------------------

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        # Personal Details
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        address = request.form.get('address', '').strip()
        location = request.form.get('location', '').strip()
        qualification = request.form.get('qualification', '').strip()
        experience = request.form.get('experience', '').strip()

        # Date of Birth
        try:
            dob = date.fromisoformat(
                request.form.get('date_of_birth', '')
            )
        except ValueError:
            return show_error('date_of_birth', 'Enter a valid Date of Birth!')

        # Education Details
        tenth_percentage = request.form.get('tenth_percentage', '').strip()
        tenth_year = request.form.get('tenth_year', '').strip()

        twelfth_percentage = request.form.get('twelfth_percentage', '').strip()
        twelfth_year = request.form.get('twelfth_year', '').strip()

        graduation_university = request.form.get(
            'graduation_university', ''
        ).strip()

        graduation_percentage = request.form.get(
            'graduation_percentage', ''
        ).strip()

        graduation_year = request.form.get(
            'graduation_year', ''
        ).strip()

        postgrad_university = request.form.get(
            'postgrad_university', ''
        ).strip()

        postgrad_percentage = request.form.get(
            'postgrad_percentage', ''
        ).strip()

        postgrad_year = request.form.get(
            'postgrad_year', ''
        ).strip()

        # Professional Details
        skills = request.form.get('skills', '').strip()
        domain = request.form.get('domain', '').strip()
        technical_skills = request.form.get('technical_skills', '').strip()
        soft_skills = request.form.get('soft_skills', '').strip()

        certifications = request.form.get('certifications', '').strip()
        projects = request.form.get('projects', '').strip()
        hobbies = request.form.get('hobbies', '').strip()
        interests = request.form.get('interests', '').strip()

        job_positions_looking_for = request.form.get(
            'job_positions_looking_for', ''
        ).strip()

        job_location = request.form.get('job_location', '').strip()

        # Social Profiles
        linkedin_profile = request.form.get('linkedin_profile', '').strip()
        github_profile = request.form.get('github_profile', '').strip()
        portfolio = request.form.get('portfolio', '').strip()

        # -------------------- VALIDATIONS --------------------

        if not first_name.isalpha():
            return show_error('first_name', 'Enter a valid first name!')

        if not last_name.isalpha():
            return show_error('last_name', 'Enter a valid last name!')

        if not re.fullmatch(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+', email):
            return show_error('email', 'Enter a valid email address!')

        if not re.fullmatch(r'\d{10}', phone):
            return show_error('phone', 'Phone number must contain 10 digits!')

        if not address:
            return show_error('address', 'Address is required!')

        if dob > date.today():
            return show_error('date_of_birth', 'Date of Birth cannot be in the future!')

        age = (
            date.today().year - dob.year
            - ((date.today().month, date.today().day) < (dob.month, dob.day))
        )

        if age < 18 or age > 30:
            return show_error('date_of_birth', 'Age must be between 18 and 30 years!')

        if not location:
            return show_error('location', 'Location is required!')

        if not graduation_university:
            return show_error(
                'graduation_university',
                'Graduation university is required!'
            )

        # Percentage validation
        percentage_fields = [
            ('tenth_percentage', tenth_percentage),
            ('twelfth_percentage', twelfth_percentage),
            ('graduation_percentage', graduation_percentage)
        ]

        if postgrad_percentage:
            percentage_fields.append(
                ('postgrad_percentage', postgrad_percentage)
            )

        for field, value in percentage_fields:
            try:
                percentage = float(value)

                if percentage < 0 or percentage > 100:
                    return show_error(field, 'Percentage must be between 0 and 100!')

            except ValueError:
                return show_error(field, 'Enter a valid percentage!')

        # Year validation
        year_fields = [
            ('tenth_year', tenth_year),
            ('twelfth_year', twelfth_year),
            ('graduation_year', graduation_year)
        ]

        if postgrad_year:
            year_fields.append(('postgrad_year', postgrad_year))

        current_year = date.today().year

        for field, value in year_fields:
            if not value.isdigit():
                return show_error(field, 'Enter a valid year!')

            if int(value) < 1990 or int(value) > current_year:
                return show_error(field, 'Enter a valid education year!')

        # Postgraduation validation
        if any([
            postgrad_university,
            postgrad_percentage,
            postgrad_year
        ]):
            if not all([
                postgrad_university,
                postgrad_percentage,
                postgrad_year
            ]):
                return show_error(
                    'postgrad_university',
                    'Complete all postgraduate details!'
                )

        if not skills:
            return show_error('skills', 'Skills are required!')

        if not password or len(password) < 8:
            return show_error('password', 'Password must contain at least 8 characters!')

        if password != confirm_password:
            return show_error('confirm_password', 'Passwords do not match!')

        # -------------------- RESUME UPLOAD --------------------

        resume_file = request.files.get('resume')

        if not resume_file or not resume_file.filename:
            return show_error('resume', 'Please upload your resume!')

        if not resume_file.filename.lower().endswith('.pdf'):
            return show_error('resume', 'Only PDF resumes are allowed!')

        resume_original = secure_filename(resume_file.filename)

        if not resume_original:
            return show_error('resume', 'Invalid resume filename!')

        # -------------------- PHOTO UPLOAD --------------------

        photo_file = request.files.get('photo')
        photo_filename = None

        if photo_file and photo_file.filename:

            if not photo_file.filename.lower().endswith(
                ('.jpg', '.jpeg', '.png')
            ):
                return show_error(
                    'photo',
                    'Only JPG, JPEG and PNG photos are allowed!'
                )

            photo_original = secure_filename(photo_file.filename)

            if not photo_original:
                return show_error('photo', 'Invalid photo filename!')

            photo_filename = (
                email.replace('@', '_').replace('.', '_')
                + '_' + photo_original
            )

        # -------------------- CONVERT EDUCATION VALUES --------------------

        tenth_percentage = float(tenth_percentage)
        tenth_year = int(tenth_year)

        twelfth_percentage = float(twelfth_percentage)
        twelfth_year = int(twelfth_year)

        graduation_percentage = float(graduation_percentage)
        graduation_year = int(graduation_year)

        if postgrad_percentage and postgrad_year:
            postgrad_percentage = float(postgrad_percentage)
            postgrad_year = int(postgrad_year)
        else:
            postgrad_percentage = None
            postgrad_year = None
            postgrad_university = None

        # -------------------- DATABASE INSERT --------------------

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute(
                'SELECT student_id FROM students WHERE email = %s',
                (email,)
            )

            if cursor.fetchone():
                return show_error('email', 'Email already registered!')

            hashed_password = generate_password_hash(password)

            filename = (
                email.replace('@', '_').replace('.', '_')
                + '_' + resume_original
            )

            os.makedirs('static/resumes', exist_ok=True)
            os.makedirs('static/photos', exist_ok=True)

            query = """
                INSERT INTO students
                (
                    first_name, last_name, email, phone, password,
                    address, location, date_of_birth, qualification,
                    skills, experience, resume,
                    tenth_percentage, tenth_year,
                    twelfth_percentage, twelfth_year,
                    graduation_university, graduation_percentage,
                    graduation_year,
                    postgrad_university, postgrad_percentage,
                    postgrad_year,
                    domain, technical_skills, soft_skills,
                    certifications, projects, hobbies, interests,
                    job_positions_looking_for, job_location,
                    linkedin_profile, github_profile, portfolio, photo
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
            """

            values = (
                first_name, last_name, email, phone, hashed_password,
                address, location, dob, qualification,
                skills, experience, filename,
                tenth_percentage, tenth_year,
                twelfth_percentage, twelfth_year,
                graduation_university, graduation_percentage,
                graduation_year,
                postgrad_university, postgrad_percentage, postgrad_year,
                domain, technical_skills, soft_skills,
                certifications, projects, hobbies, interests,
                job_positions_looking_for, job_location,
                linkedin_profile, github_profile, portfolio,
                photo_filename
            )

            cursor.execute(query, values)

            student_id = cursor.lastrowid

            registration_number = f"STU{date.today().year}{student_id:03d}"

            update_query = """
                UPDATE students
                SET registration_number = %s
                WHERE student_id = %s
            """

            cursor.execute(
                update_query,
                (registration_number, student_id)
            )

            connection.commit()

            resume_file.save(os.path.join('static/resumes', filename))

            if photo_filename:
                photo_file.save(
                    os.path.join('static/photos', photo_filename)
                )

            return redirect(url_for('login'))

        except Exception as e:
            connection.rollback()
            return f'Registration Error: {e}'

        finally:
            cursor.close()
            connection.close()

    return render_template('register.html', form_data={}, errors={})


# -------------------- STUDENT LOGIN --------------------

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            attempt_query = """
                SELECT failed_attempts,
                       locked_until,
                       locked_until > NOW() AS is_locked,
                       locked_until <= NOW() AS is_expired
                FROM login_attempts
                WHERE email = %s
            """

            cursor.execute(attempt_query, (email,))
            attempt = cursor.fetchone()

            if attempt and attempt['is_locked']:

                return render_template(
                    'login.html',
                    error='Too many incorrect attempts! '
                          'Please try again after 30 seconds.'
                )

            if attempt and attempt['is_expired']:

                reset_query = """
                    UPDATE login_attempts
                    SET failed_attempts = 0,
                        locked_until = NULL
                    WHERE email = %s
                """

                cursor.execute(reset_query, (email,))
                connection.commit()

            query = """
                SELECT student_id, first_name, email,
                       password, approval_status
                FROM students
                WHERE email = %s
            """

            cursor.execute(query, (email,))
            student = cursor.fetchone()

            if student is None or not check_password_hash(
                student['password'], password
            ):

                if attempt is None:

                    insert_query = """
                        INSERT INTO login_attempts
                        (email, failed_attempts)
                        VALUES (%s, 1)
                    """

                    cursor.execute(insert_query, (email,))

                else:

                    update_query = """
                        UPDATE login_attempts
                        SET locked_until =
                            CASE
                                WHEN failed_attempts + 1 >= 3
                                THEN DATE_ADD(NOW(), INTERVAL 30 SECOND)
                                ELSE NULL
                            END,
                            failed_attempts = failed_attempts + 1
                        WHERE email = %s
                    """

                    cursor.execute(update_query, (email,))

                connection.commit()

                cursor.execute(
                    """
                    SELECT failed_attempts
                    FROM login_attempts
                    WHERE email = %s
                    """,
                    (email,)
                )

                result = cursor.fetchone()
                failed_attempts = result['failed_attempts']

                if failed_attempts >= 3:
                    error = 'Account locked for 30 seconds!'
                else:
                    remaining = 3 - failed_attempts

                    error = (
                        'Invalid email or password! '
                        f'{remaining} attempts remaining.'
                    )

                return render_template('login.html', error=error)

            cursor.execute(
                """
                DELETE FROM login_attempts
                WHERE email = %s
                """,
                (email,)
            )

            connection.commit()

            if student['approval_status'] != 'Approved':

                return render_template(
                    'login.html',
                    error='Your account is not approved yet!'
                )

            session['student_id'] = student['student_id']
            session['student_name'] = student['first_name']
            session['student_email'] = student['email']

            return redirect(url_for('dashboard'))

        finally:
            cursor.close()
            connection.close()

    return render_template('login.html', error=None)


# -------------------- STUDENT LOGOUT --------------------

@auth_bp.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('login'))
