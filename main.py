# from flask import send_from_directory
from flask import Flask, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Jobs, Department, Category
from forms import LoginForm, RegisterForm, AddJobForm, AddDepartmentForm, EditDepartmentForm
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from blueprints.jobs_api import jobs_api_blueprint
from blueprints.users_api import users_api_blueprint
from users_resource import UsersListResource, UsersResource
from jobs_resource import JobsListResource, JobsResource
from flask_restful import Api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.register_blueprint(jobs_api_blueprint)
app.register_blueprint(users_api_blueprint)

api = Api(app)
api.add_resource(UsersListResource, '/api/v2/users')
api.add_resource(UsersResource, '/api/v2/users/<int:user_id>')

api.add_resource(JobsListResource, '/api/v2/jobs')
api.add_resource(JobsResource, '/api/v2/jobs/<int:job_id>')

# @app.route('/favicon1.ico')
# def favicon():
#     return send_from_directory(app.static_folder, 'favicon1.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(404)
def handle_404_error(error):
    return jsonify({'error': 'Job not found', 'description': str(error)}), 404


@app.errorhandler(500)
def handle_500_error(error):
    return jsonify({'error': 'Internal Server Error', 'description': str(error)}), 500


@login_manager.user_loader
def load_user(user_id):
    session = Session(db.engine)
    return session.get(User, int(user_id))


@app.route('/')
@login_required
def index():
    jobs = db.session.all()
    return render_template('index.html', jobs=jobs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неправильный логин или пароль.', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Пользователь с таким email уже существует.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            name=form.name.data,
            city_from=form.city_from.data
        )
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка базы данных: {str(e)}', 'danger')
            return redirect(url_for('register'))

        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('login'))


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def add_job():
    form = AddJobForm()
    users = User.query.all()
    form.team_leader_id.choices = [(user.id, user.name) for user in users]
    categories = Category.query.all()
    form.category_ids.choices = [(category.id, category.name) for category in categories]

    if form.validate_on_submit():
        new_job = Jobs(
            job_title=form.job_title.data,
            team_leader_id=form.team_leader_id.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data
        )

        selected_categories = Category.query.filter(Category.id.in_(form.category_ids.data)).all()
        new_job.categories.extend(selected_categories)
        db.session.add(new_job)
        db.session.commit()
        flash('Работа успешно добавлена!', 'success')
        return redirect(url_for('index'))
    return render_template('addjob.html', form=form, title='Add Job')


@app.route('/editjob/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = db.session.get_or_404(Jobs, job_id)
    if current_user.id != job.team_leader_id and current_user.id != 1:
        flash('У вас нет прав для редактирования этой работы.', 'danger')
        return redirect(url_for('index'))

    form = AddJobForm()
    users = User.query.all()
    form.team_leader_id.choices = [(user.id, user.name) for user in users]
    categories = Category.query.all()
    form.category_ids.choices = [(category.id, category.name) for category in categories]
    if form.validate_on_submit():
        job.job_title = form.job_title.data
        job.team_leader_id = form.team_leader_id.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        selected_categories = Category.query.filter(Category.id.in_(form.category_ids.data)).all()
        job.categories = selected_categories
        db.session.commit()
        flash('Работа успешно обновлена!', 'success')
        return redirect(url_for('index'))

    form.job_title.data = job.job_title
    form.team_leader_id.data = job.team_leader_id
    form.work_size.data = job.work_size
    form.collaborators.data = job.collaborators
    form.is_finished.data = job.is_finished
    current_category_ids = [category.id for category in job.categories]
    form.category_ids.data = current_category_ids
    return render_template('addjob.html', form=form, title='Edit Job')


@app.route('/deletejob/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    job = db.session.get_or_404(Jobs, job_id)
    if current_user.id != job.team_leader_id and current_user.id != 1:
        flash('У вас нет прав для удаления этой работы.', 'danger')
        return redirect(url_for('index'))

    db.session.delete(job)
    db.session.commit()
    flash('Работа успешно удалена!', 'success')
    return redirect(url_for('index'))


@app.route('/departments')
@login_required
def list_departments():
    departments = Department.query.all()
    return render_template('departments.html', departments=departments)


@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    form = AddDepartmentForm()
    users = User.query.all()
    form.chief_id.choices = [(user.id, user.name) for user in users]
    if form.validate_on_submit():
        new_department = Department(
            title=form.title.data,
            chief_id=form.chief_id.data,
            members=form.members.data,
            email=form.email.data
        )
        db.session.add(new_department)
        db.session.commit()
        flash('Департамент успешно добавлен!', 'success')
        return redirect(url_for('list_departments'))
    return render_template('add_department.html', form=form, title='Add Department')


@app.route('/edit_department/<int:department_id>', methods=['GET', 'POST'])
@login_required
def edit_department(department_id):
    department = Department.query.get_or_404(department_id)
    form = EditDepartmentForm()
    users = User.query.all()
    form.chief_id.choices = [(user.id, user.name) for user in users]
    if form.validate_on_submit():
        department.title = form.title.data
        department.chief_id = form.chief_id.data
        department.members = form.members.data
        department.email = form.email.data
        db.session.commit()
        flash('Департамент успешно обновлен!', 'success')
        return redirect(url_for('list_departments'))

    form.title.data = department.title
    form.chief_id.data = department.chief_id
    form.members.data = department.members
    form.email.data = department.email
    return render_template('edit_department.html', form=form, title='Edit Department')


@app.route('/delete_department/<int:department_id>', methods=['POST'])
@login_required
def delete_department(department_id):
    department = Department.query.get_or_404(department_id)
    if current_user.id != 1:
        flash('У вас нет прав для удаления этого департамента.', 'danger')
        return redirect(url_for('list_departments'))

    db.session.delete(department)
    db.session.commit()
    flash('Департамент успешно удален!', 'success')
    return redirect(url_for('list_departments'))


if __name__ == '__main__':
    app.run(debug=True)
