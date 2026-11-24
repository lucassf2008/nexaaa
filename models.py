from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)  # 'aluno', 'empresa', 'admin'
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def display_name(self):
        if self.role == 'aluno' and self.student_profile:
            return self.student_profile.full_name
        if self.role == 'empresa' and self.company_profile:
            return self.company_profile.name
        return self.email.split('@')[0].capitalize()

    @property
    def avatar(self):
        if self.role == 'aluno' and self.student_profile and self.student_profile.avatar_url:
            return self.student_profile.avatar_url
        if self.role == 'empresa' and self.company_profile and self.company_profile.logo_url:
            return self.company_profile.logo_url
        return '/static/images/default_avatar.png'


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False, index=True)
    birth_date = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    city = db.Column(db.String(100), default='São Paulo')
    state = db.Column(db.String(10), default='SP')
    senai_course = db.Column(db.String(150), default='Técnico em Desenvolvimento de Sistemas')
    course_status = db.Column(db.String(30), default='Em andamento')  # 'Em andamento', 'Concluído'
    professional_area = db.Column(db.String(100), default='Desenvolvimento de software')
    headline = db.Column(db.String(200), default='Estudante SENAI em busca de novos desafios')
    about_me = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(300), default='/static/images/default_student.png')
    banner_url = db.Column(db.String(300), default='/static/images/default_banner.jpg')
    connections_count = db.Column(db.Integer, default=0)

    # Detalhes do Perfil
    skills = db.relationship('Skill', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    experiences = db.relationship('Experience', backref='student', lazy='dynamic', cascade='all, delete-orphan', order_by='Experience.id.desc()')
    educations = db.relationship('Education', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    certificates = db.relationship('Certificate', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    saved_jobs = db.relationship('SavedJob', backref='student', lazy='dynamic', cascade='all, delete-orphan')


class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False, index=True)
    access_code = db.Column(db.String(100), nullable=False)
    is_authorized = db.Column(db.Boolean, default=True, nullable=False)
    is_blocked = db.Column(db.Boolean, default=False, nullable=False)
    logo_url = db.Column(db.String(300), default='/static/images/default_company.png')
    banner_url = db.Column(db.String(300), default='/static/images/default_company_banner.jpg')
    headline = db.Column(db.String(255), default='Inovação e Tecnologia Industrial')
    description = db.Column(db.Text, nullable=True)
    sector = db.Column(db.String(100), default='Tecnologia da Informação')
    location = db.Column(db.String(150), default='São Paulo - SP')
    website = db.Column(db.String(200), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(30), nullable=True)
    employee_count = db.Column(db.String(50), default='100-250 funcionários')
    facebook = db.Column(db.String(200), nullable=True)
    instagram = db.Column(db.String(200), nullable=True)
    twitter = db.Column(db.String(200), nullable=True)
    linkedin = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    jobs = db.relationship('Job', backref='company', lazy='dynamic', cascade='all, delete-orphan', order_by='Job.id.desc()')
    followers = db.relationship('Follow', backref='company', lazy='dynamic', cascade='all, delete-orphan')


class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    area = db.Column(db.String(100), nullable=False)  # Desenvolvimento de software, Automação industrial, Dados, etc.
    job_type = db.Column(db.String(50), nullable=False)  # Estágio, Emprego efetivo, Jovem aprendiz, Projeto, Freelancer
    modality = db.Column(db.String(50), nullable=False)  # Presencial, Híbrida, Remota
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(100), nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    experience_level = db.Column(db.String(50), default='Estágio')
    vacancies = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='aberta')  # 'aberta', 'encerrada'
    image_url = db.Column(db.String(300), default='/static/images/job_default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    applications = db.relationship('Application', backref='job', lazy='dynamic', cascade='all, delete-orphan')
    saved_by = db.relationship('SavedJob', backref='job', lazy='dynamic', cascade='all, delete-orphan')


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(30), default='recebida')  # recebida, em_analise, entrevista, aprovada, rejeitada
    notes = db.Column(db.Text, nullable=True)  # Anotações ou mensagem da empresa
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('job_id', 'student_id', name='uq_application_job_student'),
    )


class SavedJob(db.Model):
    __tablename__ = 'saved_jobs'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'job_id', name='uq_saved_job'),
    )


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(250), nullable=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    category = db.Column(db.String(50), default='novidades')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan', order_by='Comment.created_at.asc()')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='uq_post_like'),
    )


class Follow(db.Model):
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    follower = db.relationship('User', foreign_keys=[follower_id], backref='following_companies')

    __table_args__ = (
        db.UniqueConstraint('follower_id', 'company_id', name='uq_follow_company'),
    )


class Connection(db.Model):
    __tablename__ = 'connections'

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    addressee_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, aceita, recusada
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requester = db.relationship('User', foreign_keys=[requester_id], backref='sent_connections')
    addressee = db.relationship('User', foreign_keys=[addressee_id], backref='received_connections')

    __table_args__ = (
        db.UniqueConstraint('requester_id', 'addressee_id', name='uq_user_connection'),
    )


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(50), default='Intermediário')


class Experience(db.Model):
    __tablename__ = 'experiences'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)
    period = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_current = db.Column(db.Boolean, default=False)


class Education(db.Model):
    __tablename__ = 'educations'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    institution = db.Column(db.String(150), nullable=False)
    course = db.Column(db.String(150), nullable=False)
    start_year = db.Column(db.String(10), nullable=True)
    end_year = db.Column(db.String(10), nullable=True)
    status = db.Column(db.String(50), default='Em andamento')


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    technologies = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    link_url = db.Column(db.String(300), nullable=True)


class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    issuing_organization = db.Column(db.String(150), default='SENAI')
    issue_date = db.Column(db.String(30), nullable=True)
    credential_url = db.Column(db.String(300), nullable=True)


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='SET NULL'), nullable=True)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, resolvido, descartado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reporter = db.relationship('User', foreign_keys=[reporter_id])
    reported_user = db.relationship('User', foreign_keys=[reported_user_id])
    post = db.relationship('Post', foreign_keys=[post_id])


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    link = db.Column(db.String(200), default='#')
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
