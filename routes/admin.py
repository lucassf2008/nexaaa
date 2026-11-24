import secrets
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models import (
    db, User, StudentProfile, CompanyProfile, Job, Application, Post, Report
)
from auth import login_required, role_required
from forms import clean_digits, validate_cnpj, format_cnpj, validate_email_format

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def generate_company_code(prefix="NEXA"):
    # Gera um código seguro e legível como NEXA-9482-BR
    rand_part = secrets.token_hex(3).upper()
    return f"{prefix}-{rand_part}"

@admin_bp.route('/')
@login_required
@role_required('admin')
def dashboard():
    total_students = StudentProfile.query.count()
    total_companies = CompanyProfile.query.count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()
    total_posts = Post.query.count()
    pending_reports = Report.query.filter_by(status='pendente').count()

    recent_companies = CompanyProfile.query.order_by(CompanyProfile.created_at.desc()).limit(5).all()
    recent_students = StudentProfile.query.order_by(StudentProfile.id.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_companies=total_companies,
        total_jobs=total_jobs,
        total_applications=total_applications,
        total_posts=total_posts,
        pending_reports=pending_reports,
        recent_companies=recent_companies,
        recent_students=recent_students,
        recent_jobs=recent_jobs
    )


@admin_bp.route('/empresas', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def companies():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        cnpj_raw = request.form.get('cnpj', '').strip()
        email = request.form.get('email', '').strip().lower()
        sector = request.form.get('sector', 'Indústria e Tecnologia').strip()
        location = request.form.get('location', 'São Paulo - SP').strip()
        custom_code = request.form.get('access_code', '').strip()

        if not name or not cnpj_raw or not email:
            flash('Nome, CNPJ e e-mail institucional são obrigatórios.', 'danger')
            return redirect(url_for('admin.companies'))

        cnpj_clean = clean_digits(cnpj_raw)
        if not validate_cnpj(cnpj_clean):
            flash('O CNPJ informado é inválido de acordo com o cálculo matemático oficial da Receita Federal.', 'danger')
            return redirect(url_for('admin.companies'))

        formatted_c = format_cnpj(cnpj_clean)

        # Checar se já existe
        if CompanyProfile.query.filter((CompanyProfile.cnpj == cnpj_clean) | (CompanyProfile.cnpj == formatted_c)).first():
            flash('Uma empresa com este CNPJ já está registrada no Nexa SENAI.', 'danger')
            return redirect(url_for('admin.companies'))

        if User.query.filter_by(email=email).first():
            flash('Já existe um usuário com este e-mail.', 'danger')
            return redirect(url_for('admin.companies'))

        # Gerar código de acesso empresarial único
        access_code = custom_code or generate_company_code()

        # Criação do usuário da empresa
        emp_user = User(
            role='empresa',
            email=email,
            is_active=True
        )
        emp_user.set_password(access_code)  # Senha inicial pode ser o próprio código
        db.session.add(emp_user)
        db.session.flush()

        # Criação do perfil da empresa
        new_company = CompanyProfile(
            user_id=emp_user.id,
            name=name,
            cnpj=formatted_c,
            access_code=access_code,
            is_authorized=True,
            is_blocked=False,
            sector=sector,
            location=location,
            contact_email=email,
            headline=f'Empresa Parceira Oficial do SENAI em {sector}',
            description=f'Empresa {name} integrada ao ecossistema Nexa SENAI para fomento de estágios, carreiras e inovação industrial.'
        )
        db.session.add(new_company)
        db.session.commit()

        flash(f'Empresa "{name}" autorizada com sucesso! Código de acesso gerado: {access_code}', 'success')
        return redirect(url_for('admin.companies'))

    all_companies = CompanyProfile.query.order_by(CompanyProfile.created_at.desc()).all()
    return render_template('admin/companies.html', companies=all_companies)


@admin_bp.route('/empresas/<int:company_id>/toggle-status', methods=['POST'])
@login_required
@role_required('admin')
def toggle_company_status(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.is_blocked = not company.is_blocked
    company.user.is_active = not company.is_blocked
    db.session.commit()

    status_str = "bloqueada" if company.is_blocked else "desbloqueada/ativa"
    flash(f'Empresa {company.name} foi {status_str} com sucesso.', 'info')
    return redirect(url_for('admin.companies'))


@admin_bp.route('/empresas/<int:company_id>/redefinir-codigo', methods=['POST'])
@login_required
@role_required('admin')
def reset_company_code(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    new_code = generate_company_code()
    company.access_code = new_code
    company.user.set_password(new_code)
    db.session.commit()

    flash(f'Novo código de acesso para a empresa {company.name}: {new_code}', 'success')
    return redirect(url_for('admin.companies'))


@admin_bp.route('/usuarios')
@login_required
@role_required('admin')
def users_list():
    students = StudentProfile.query.all()
    companies = CompanyProfile.query.all()
    return render_template('admin/users.html', students=students, companies=companies)


@admin_bp.route('/usuarios/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == g.current_user.id:
        flash('Você não pode desativar seu próprio usuário administrador.', 'danger')
        return redirect(url_for('admin.users_list'))

    user.is_active = not user.is_active
    db.session.commit()
    flash(f'Usuário {user.display_name} foi {"reativado" if user.is_active else "bloqueado"}.', 'info')
    return redirect(url_for('admin.users_list'))


@admin_bp.route('/vagas')
@login_required
@role_required('admin')
def jobs_list():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template('admin/jobs.html', jobs=jobs)


@admin_bp.route('/vagas/<int:job_id>/deletar', methods=['POST'])
@login_required
@role_required('admin')
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    title = job.title
    db.session.delete(job)
    db.session.commit()
    flash(f'Vaga "{title}" removida com sucesso.', 'info')
    return redirect(url_for('admin.jobs_list'))


@admin_bp.route('/publicacoes/<int:post_id>/deletar', methods=['POST'])
@login_required
@role_required('admin')
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Publicação removida pela moderação administrativa.', 'info')
    return redirect(request.referrer or url_for('admin.dashboard'))
