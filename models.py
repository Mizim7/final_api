from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    city_from = db.Column(db.String(100), nullable=False)
    jobs = db.relationship('Jobs', backref='team_leader', lazy=True)


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


job_category = db.Table(
    'job_category',
    db.Column('job_id', db.Integer, db.ForeignKey('jobs.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True)
)


class Jobs(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    team_leader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    work_size = db.Column(db.Integer, nullable=False)
    collaborators = db.Column(db.String(100), nullable=False)
    is_finished = db.Column(db.Boolean, default=False)

    categories = db.relationship(
        'Category',
        secondary=job_category,
        backref=db.backref('jobs', lazy='dynamic'),
        lazy='dynamic'
    )


class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    chief_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    members = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    chief = db.relationship('User', foreign_keys=[chief_id])
