from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import db, User, StudentProfile, CompanyProfile
from forms import (
    clean_digits, validate_cpf, validate_cnpj, format_cpf, format_cnpj, validate_email_format
)

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Por favor, faça login para acessar esta página.', 'warning')
                return redirect(url_for('auth.login'))
            user = db.session.get(User, session['user_id'])
            if not user or user.role not in roles:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                return redirect(url_for('main.feed'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        if user:
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.feed'))

    active_tab = request.args.get('tab', 'aluno')

    if request.method == 'POST':
        login_type = request.form.get('login_type', 'aluno')
        active_tab = login_type

        # -----------------------------
        # 1. LOGIN DE ALUNO
        # -----------------------------
        if login_type == 'aluno':
            identifier = request.form.get('identifier', '').strip()  # Pode ser CPF ou Email
            password = request.form.get('password', '')

            if not identifier or not password:
                flash('Preencha todos os campos para entrar.', 'danger')
                return render_template('login.html', active_tab=active_tab, identifier=identifier)

            # Verifica se digitou CPF ou e-mail
            digits_only = clean_digits(identifier)
            user = None
            if len(digits_only) == 11 and digits_only.isdigit():
                if not validate_cpf(digits_only):
                    flash('O CPF informado é inválido pelo algoritmo de validação.', 'danger')
                    return render_template('login.html', active_tab=active_tab, identifier=identifier)
                formatted_cpf = format_cpf(digits_only)
                student = StudentProfile.query.filter(
                    (StudentProfile.cpf == digits_only) | (StudentProfile.cpf == formatted_cpf)
                ).first()
                if student:
                    user = student.user
            else:
                user = User.query.filter_by(email=identifier.lower(), role='aluno').first()

            if not user or not user.check_password(password):
                flash('CPF/E-mail ou senha incorretos.', 'danger')
                return render_template('login.html', active_tab=active_tab, identifier=identifier)

            if not user.is_active:
                flash('Sua conta está desativada ou bloqueada. Contate o suporte.', 'danger')
                return render_template('login.html', active_tab=active_tab)

            session.clear()
            session['user_id'] = user.id
            session['user_role'] = user.role
            flash(f'Bem-vindo de volta, {user.display_name}!', 'success')
            next_url = request.args.get('next') or url_for('main.feed')
            return redirect(next_url)

        # -----------------------------
        # 2. LOGIN DE EMPRESA
        # -----------------------------
        elif login_type == 'empresa':
            cnpj_raw = request.form.get('cnpj', '').strip()
            access_code = request.form.get('access_code', '').strip()

            if not cnpj_raw or not access_code:
                flash('Informe o CNPJ e o Código de Acesso Empresarial.', 'danger')
                return render_template('login.html', active_tab='empresa', cnpj=cnpj_raw)

            clean_cnpj_val = clean_digits(cnpj_raw)
            if not validate_cnpj(clean_cnpj_val):
                flash('CNPJ inválido pelo algoritmo de validação matemática.', 'danger')
                return render_template('login.html', active_tab='empresa', cnpj=cnpj_raw)

            formatted_c = format_cnpj(clean_cnpj_val)
            company = CompanyProfile.query.filter(
                (CompanyProfile.cnpj == clean_cnpj_val) | (CompanyProfile.cnpj == formatted_c)
            ).first()

            if not company:
                flash('Empresa não cadastrada no sistema. O acesso corporativo deve ser autorizado pela administração do SENAI.', 'danger')
                return render_template('login.html', active_tab='empresa', cnpj=cnpj_raw)

            if not company.is_authorized or company.is_blocked or not company.user.is_active:
                flash('Acesso empresarial bloqueado ou não autorizado. Entre em contato com a administração do Nexa SENAI.', 'danger')
                return render_template('login.html', active_tab='empresa', cnpj=cnpj_raw)

            if company.access_code != access_code:
                flash('Código de acesso empresarial incorreto.', 'danger')
                return render_template('login.html', active_tab='empresa', cnpj=cnpj_raw)

            session.clear()
            session['user_id'] = company.user.id
            session['user_role'] = 'empresa'
            flash(f'Acesso concedido à empresa {company.name}!', 'success')
            return redirect(url_for('company.profile_view', company_id=company.id))

        # -----------------------------
        # 3. LOGIN ADMINISTRATIVO
        # -----------------------------
        elif login_type == 'admin':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            user = User.query.filter_by(email=email, role='admin').first()
            if not user or not user.check_password(password):
                flash('Credenciais administrativas incorretas.', 'danger')
                return render_template('login.html', active_tab='admin', email=email)

            session.clear()
            session['user_id'] = user.id
            session['user_role'] = 'admin'
            flash('Sessão administrativa iniciada com sucesso.', 'success')
            return redirect(url_for('admin.dashboard'))

    return render_template('login.html', active_tab=active_tab)


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def register_aluno():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        cpf_raw = request.form.get('cpf', '').strip()
        birth_date = request.form.get('birth_date', '').strip()
        email = request.form.get('email', '').strip().lower()
        senai_course = request.form.get('senai_course', '').strip()
        professional_area = request.form.get('professional_area', 'Desenvolvimento de software').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # Validações obrigatórias
        if not full_name or not cpf_raw or not email or not password or not password_confirm:
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'danger')
            return render_template('register_aluno.html', form_data=request.form)

        cpf_clean = clean_digits(cpf_raw)
        if not validate_cpf(cpf_clean):
            flash('O CPF informado é inválido segundo o algoritmo de validação matemática.', 'danger')
            return render_template('register_aluno.html', form_data=request.form)

        if not validate_email_format(email):
            flash('Formato de e-mail inválido. Utilize seu e-mail institucional ou educacional.', 'danger')
            return render_template('register_aluno.html', form_data=request.form)

        if password != password_confirm:
            flash('As senhas informadas não coincidem.', 'danger')
            return render_template('register_aluno.html', form_data=request.form)

        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return render_template('register_aluno.html', form_data=request.form)

        # Checar duplicidades
        if User.query.filter_by(email=email).first():
            flash('Este e-mail já está cadastrado na plataforma.', 'danger')
            return render_template('register_aluno.html', form_data=request.form)

        formatted_c = format_cpf(cpf_clean)
        if StudentProfile.query.filter((StudentProfile.cpf == cpf_clean) | (StudentProfile.cpf == formatted_c)).first():
            flash('Este CPF já está cadastrado no sistema Nexa SENAI.', 'danger')
            return render_template('register_aluno.html', form_data=request.form)

        # Criação do usuário e perfil do aluno
        new_user = User(
            role='aluno',
            email=email,
            is_active=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        new_student = StudentProfile(
            user_id=new_user.id,
            full_name=full_name,
            cpf=formatted_c,
            birth_date=birth_date,
            senai_course=senai_course or 'Curso Técnico SENAI',
            course_status='Em andamento',
            professional_area=professional_area,
            headline=f'Aluno SENAI | {professional_area}',
            about_me='Estudante dedicado, entusiasmado com inovação, tecnologia e novos desafios profissionais.'
        )
        db.session.add(new_student)
        db.session.commit()

        # Login automático
        session.clear()
        session['user_id'] = new_user.id
        session['user_role'] = 'aluno'
        flash('Cadastro realizado com sucesso! Bem-vindo ao Nexa SENAI.', 'success')
        return redirect(url_for('profile.student_profile', student_id=new_student.id))

    return render_template('register_aluno.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta com segurança.', 'info')
    return redirect(url_for('auth.login'))
