from datetime import date

from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, LoginManager, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from functools import wraps
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, Integer
from forms import RegisterForm, AutomateForm
import os
from automte import Automation, working, problem_status, final_status, logs_left, check_logs

UPLOAD_FOLDER = 'static/'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'success_is_a_big_boy'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///celfautomate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


automation = Automation()
completed = False


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    uploads = relationship('Automate', back_populates='uploader')


class Automate(db.Model):
    __tablename__ = 'automate'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    uploader_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'))
    uploader = relationship('User', back_populates='uploads')

    date: Mapped[str] = mapped_column(String(100), nullable=False)
    attendance_range: Mapped[str] = mapped_column(String(100), nullable=False)
    first_timer: Mapped[str] = mapped_column(String(100), nullable=False)
    midweek_attendance: Mapped[str] = mapped_column(String(100), nullable=False)
    sunday_attendance: Mapped[str] = mapped_column(String(100), nullable=False)
    meeting_date: Mapped[str] = mapped_column(String(100), nullable=False)
    testimonies: Mapped[str] = mapped_column(String(500), nullable=False)

    no_of_logs: Mapped[int] = mapped_column(Integer, nullable=False)
    no_of_problem_logs: Mapped[int] = mapped_column(Integer, nullable=True)
    no_of_successful_logs: Mapped[int] = mapped_column(Integer, nullable=True)

    status: Mapped[str] = mapped_column(String(100), nullable=False)


with app.app_context():
    db.create_all()


login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        try:
            if current_user.id != 1 and current_user.email != 'successabalaka2002@gmail.com':
                return abort(403)
        except AttributeError:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


@app.route('/', methods=['POST', 'GET'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login_page'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login_page'))
        else:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('index2.html', current_user=current_user)


@app.route('/register', methods=['POST', 'GET'])
# @admin_only
def register():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirmpassword')
        print(password, confirm_password)
        if password == confirm_password:
            user = db.session.execute(db.select(User).where(User.email == request.form.get('email'))).scalar()
            if user is None:
                new_user = User(
                    first_name=request.form.get('fname'),
                    last_name=request.form.get('lname'),
                    email=request.form.get('email'),
                    password=generate_password_hash(password,
                                                    method='pbkdf2:sha256',
                                                    salt_length=8)
                )

                db.session.add(new_user)
                db.session.commit()

                login_user(new_user)
                return redirect(url_for('dashboard'))
            else:
                flash("You've already signed up with that email. Log in instead")
                return redirect(url_for('login_page'))
        else:
            flash("The passwords don't match")
            return redirect(url_for('register'))
    return render_template('register2.html', current_user=current_user)


@app.route('/dashboard')
@login_required
def dashboard():
    status = 'Completed'
    no_of_logs = db.session.execute(db.select(Automate.no_of_logs)).scalars().all()
    no_of_problem_logs = db.session.execute(db.select(Automate.no_of_problem_logs)).scalars().all()
    no_of_successful_logs = db.session.execute(db.select(Automate.no_of_successful_logs)).scalars().all()

    try:
        total_no_logs = sum(map(int, no_of_logs))

        total_no_plogs = sum(map(int, no_of_problem_logs))

        total_no_slogs = sum(map(int, no_of_successful_logs))

    #
    except TypeError:
        total_no_logs = sum(map(int, no_of_logs))
        total_no_plogs = db.session.execute(db.select(Automate.no_of_problem_logs)).scalar()
        total_no_slogs = db.session.execute(db.select(Automate.no_of_successful_logs)).scalar()

    result = db.session.execute(db.select(Automate).order_by(Automate.date)).scalars()
    uploads = result.all()
    # print(uploads.all()[0].attendance_range)
    # for upload in uploads:
    #     print(upload)

    # print(result.scalar())
    return render_template('dashboard.html', current_user=current_user, no_of_logs=total_no_logs,
                           no_of_problem_logs=total_no_plogs, no_of_successful_logs=total_no_slogs,
                           uploads=uploads, status=status)


@app.route('/charts')
@login_required
def charts():
    return render_template('charts.html', current_user=current_user)


@app.route('/tables')
@login_required
def tables():
    result = db.session.execute(db.select(Automate).order_by(Automate.date)).scalars()
    uploads = result.all()
    return render_template('tables.html', current_user=current_user, uploads=uploads)


@app.route('/layout-static')
@login_required
def layout_static():
    return render_template('layout-static.html', current_user=current_user)


@app.route('/layout-sidenav')
@login_required
def layout_sidenav():
    return render_template('layout-sidenav-light.html', current_user=current_user)


@app.route('/new', methods=['POST', 'GET'])
@login_required
def new():
    form = AutomateForm()
    if request.method == 'POST':
        type_of_meeting = request.form.getlist('meeting_type')
        attendance1 = request.form['attendance1']
        attendance2 = request.form['attendance2']
        ft1 = request.form['ft1']
        ft2 = request.form['ft2']
        ma1 = request.form['ma1']
        ma2 = request.form['ma2']
        sunday1 = request.form['sunday1']
        sunday2 = request.form['sunday2']
        meeting_date = str(request.form['meeting_date'])
        testimonies = request.form.get('testimonies')
        testimony_list = testimonies.split(', ')
        # if len(type_of_meeting) == 1:
        # print(type_of_meeting)
        if 'csv_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['csv_file']
        # cwd = os.getcwd()  # Get the current working directory (cwd)
        # files = os.listdir(cwd)  # Get all the files in that directory
        # print("Files in %r: %s" % (cwd, files))
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            automation.read_csv(filepath=f'static/{filename}',
                                meeting_list=type_of_meeting,
                                attendance1=attendance1, attendance2=attendance2,
                                first_timers1=ft1, first_timers2=ft2,
                                midweek1=ma1, midweek2=ma2,
                                sunday1=sunday1, sunday2=sunday2, date=meeting_date.split('-')[2],
                                testimony_list=testimony_list)

            new_automate = Automate(date=date.today().strftime("%B %d, %Y"),
                                    attendance_range=f'{attendance1}, {attendance2}',
                                    first_timer=f'{ft1}, {ft2}',
                                    midweek_attendance=f'{ma1}, {ma2}',
                                    sunday_attendance=f'{sunday1}, {sunday2}',
                                    meeting_date=meeting_date,
                                    testimonies=testimonies,
                                    no_of_logs=len(automation.login_dict),
                                    status='Pending',
                                    uploader=current_user)
            db.session.add(new_automate)
            db.session.commit()

            automation.begin_automation()
            results = db.session.execute(db.select(Automate).where(Automate.meeting_date == meeting_date)).scalars()
            for result in results:
                if result.attendance_range == f'{attendance1}, {attendance2}':
                    result.no_of_problem_logs = len(automation.problem_logins['email'])
                    result.no_of_successful_logs = len(automation.login_dict) - len(automation.problem_logins['email'])
                    result.status = 'Completed'
                    db.session.commit()
            os.remove(f'static/{filename}')
            return redirect(url_for('dashboard'))
        # elif len(type_of_meeting) > 1:
        # print('More than 1')
        # print(testimony_list)
        # meeting_date = str(request.form.get('meeting_date'))
        # print(type(meeting_date))
    return render_template('new.html', form=form, current_user=current_user)


@app.route('/view')
@login_required
def view_details():
    detail_id = request.args.get('id')
    result = db.session.execute(db.select(Automate).where(Automate.id == detail_id)).scalar()
    return render_template('details.html', upload=result)


@app.route('/running-logs')
@login_required
def running_logs():
    logs_left1 = check_logs()[0]
    problem = check_logs()[2]
    complete = check_logs()[3]
    work = check_logs()[1]
    final = check_logs()[4]
    # print(final)
    total_logs = check_logs()[5]
    logs_completed = check_logs()[6]
    return render_template('running_logs.html', logs_left=logs_left1, problem_status=problem,
                           completed=complete, working=work, final_status=final, total_logs=total_logs,
                           logs_completed=logs_completed)


@app.route('/download')
@login_required
def download():
    return send_from_directory(directory='static', path='problem_logss.csv')


@app.route('/delete-plog')
@admin_only
def delete_plogs():
    try:
        os.remove(f'static/problem_logss.csv')
    except FileNotFoundError:
        pass
    return redirect(url_for('dashboard'))


@app.route('/all_users')
@login_required
@admin_only
def users():
    result = db.session.execute(db.select(User).order_by(User.id)).scalars()
    registered_users = result.all()
    return render_template('users.html', users=registered_users, current_user=current_user)


@app.route('/delete')
def delete():
    delete_id = request.args.get('id')
    result = db.get_or_404(User, delete_id)
    db.session.delete(result)
    db.session.commit()
    return redirect(url_for('users'))


@app.route('/delete-log')
@login_required
def delete_upload():
    delete_id = request.args.get('id')
    result = db.get_or_404(Automate, delete_id)
    if current_user == result.uploader or current_user.id == 1:
        db.session.delete(result)
        db.session.commit()
    else:
        return render_template('401.html', current_user=current_user)
    return redirect(url_for('dashboard'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', current_user=current_user)


@app.route('/edit-profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    edit = True
    if request.method == 'POST':
        if request.form.get('password') == request.form.get('confirmpassword'):
            user = db.get_or_404(User, current_user.id)
            user.first_name = request.form.get('fname')
            user.last_name = request.form.get('lname')
            user.email = request.form.get('email')
            user.password = generate_password_hash(request.form.get('password'),
                                                   method='pbkdf2:sha256',
                                                   salt_length=8)
            db.session.commit()
            return redirect(url_for('profile'))
        else:
            flash("The passwords don't match")
            return redirect(url_for('edit_profile'))
    return render_template('register2.html', edit=edit, current_user=current_user)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(debug=True)
