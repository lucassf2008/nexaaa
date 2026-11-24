import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, g, abort
from werkzeug.utils import secure_filename
from models import (
    db, User, CompanyProfile, Job, Application, StudentProfile, Notification
)
from auth import login_required

company_bp = Blueprint('company', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@company_bp.route('/perfil/empresa')
@login_required
def my_company_profile():
    user = g.current_user
    if user.role == 'empresa' and user.company_profile:
        return redirect(url_for('company.profile_view', company_id=user.company_profile.id))
    # Se outro perfil estiver navegando pelo menu
    first_company = CompanyProfile.query.filter_by(is_authorized=True).first()
    if first_company:
        return redirect(url_for('company.profile_view', company_id=first_company.id))
    flash('Nenhuma empresa encontrada.', 'warning')
    return redirect(url_for('main.feed'))


@company_bp.route('/empresa/<int:company_id>')
def profile_view(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    is_owner = (g.current_user and g.current_user.id == company.user_id)
    is_following = False

    if g.current_user:
        is_following = any(f.follower_id == g.current_user.id for f in company.followers)

    # Vagas da empresa
    jobs = company.jobs.all()

    return render_template(
        'profile_company.html',
        company=company,
        jobs=jobs,
        is_owner=is_owner,
        is_following=is_following
    )


@company_bp.route('/empresa/editar', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = g.current_user
    if user.role != 'empresa' or not user.company_profile:
        flash('Acesso restrito ao perfil corporativo.', 'danger')
        return redirect(url_for('main.feed'))

    company = user.company_profile

    if request.method == 'POST':
        company.name = request.form.get('name', company.name).strip()
        company.headline = request.form.get('headline', company.headline).strip()
        company.description = request.form.get('description', company.description).strip()
        company.sector = request.form.get('sector', company.sector).strip()
        company.location = request.form.get('location', company.location).strip()
        company.employee_count = request.form.get('employee_count', company.employee_count).strip()
        company.website = request.form.get('website', company.website).strip()
        company.contact_email = request.form.get('contact_email', company.contact_email).strip()
        company.contact_phone = request.form.get('contact_phone', company.contact_phone).strip()
        company.facebook = request.form.get('facebook', company.facebook).strip()
        company.instagram = request.form.get('instagram', company.instagram).strip()
        company.twitter = request.form.get('twitter', company.twitter).strip()
        company.linkedin = request.form.get('linkedin', company.linkedin).strip()

        # Upload de logo
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"company_logo_{company.id}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                company.logo_url = f"/static/uploads/{filename}"

        # Upload de banner
        if 'banner' in request.files:
            file = request.files['banner']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"company_banner_{company.id}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                company.banner_url = f"/static/uploads/{filename}"

        db.session.commit()
        flash('Perfil empresarial atualizado com sucesso!', 'success')
        return redirect(url_for('company.profile_view', company_id=company.id))

    return render_template('edit_company_profile.html', company=company)


@company_bp.route('/empresa/vagas/nova', methods=['GET', 'POST'])
@login_required
def create_job():
    user = g.current_user
    if user.role != 'empresa' or not user.company_profile:
        flash('Apenas empresas autorizadas podem publicar vagas.', 'danger')
        return redirect(url_for('jobs.list_jobs'))

    company = user.company_profile

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()
        area = request.form.get('area', 'Desenvolvimento de software').strip()
        job_type = request.form.get('job_type', 'Estágio').strip()
        modality = request.form.get('modality', 'Presencial').strip()
        location = request.form.get('location', company.location).strip()
        salary = request.form.get('salary', '').strip()
        benefits = request.form.get('benefits', '').strip()
        vacancies = request.form.get('vacancies', '1').strip()
        experience_level = request.form.get('experience_level', 'Estágio').strip()

        if not title or not description:
            flash('Título e descrição da vaga são obrigatórios.', 'danger')
            return render_template('company_new_job.html', form_data=request.form)

        job = Job(
            company_id=company.id,
            title=title,
            description=description,
            requirements=requirements or None,
            area=area,
            job_type=job_type,
            modality=modality,
            location=location,
            salary=salary or None,
            benefits=benefits or None,
            vacancies=int(vacancies) if vacancies.isdigit() else 1,
            experience_level=experience_level,
            image_url=company.logo_url or '/static/images/job_default.jpg'
        )
        db.session.add(job)
        db.session.commit()

        # Notificar seguidores da empresa sobre a nova vaga
        for follow in company.followers:
            notif = Notification(
                user_id=follow.follower_id,
                title=f"Nova vaga em {company.name}",
                message=f"{company.name} publicou a vaga: '{job.title}'. Confira agora!",
                link=url_for('jobs.job_detail', job_id=job.id)
            )
            db.session.add(notif)
        db.session.commit()

        flash(f'Vaga "{job.title}" publicada com sucesso!', 'success')
        return redirect(url_for('company.profile_view', company_id=company.id))

    return render_template('company_new_job.html', company=company)


@company_bp.route('/empresa/vagas/<int:job_id>/candidatos')
@login_required
def job_candidates(job_id):
    user = g.current_user
    job = Job.query.get_or_404(job_id)

    # Apenas a dona da vaga ou admin
    if user.role != 'admin' and (user.role != 'empresa' or user.company_profile.id != job.company_id):
        flash('Você não tem permissão para visualizar estes candidatos.', 'danger')
        return redirect(url_for('main.feed'))

    status_filter = request.args.get('status')
    candidates_query = job.applications.order_by(Application.created_at.desc())
    if status_filter:
        candidates_query = candidates_query.filter_by(status=status_filter)
    applications = candidates_query.all()

    return render_template(
        'company_candidates.html',
        job=job,
        applications=applications,
        current_status=status_filter or 'todos'
    )


@company_bp.route('/empresa/candidatura/<int:app_id>/status', methods=['POST'])
@login_required
def update_application_status(app_id):
    application = Application.query.get_or_404(app_id)
    user = g.current_user

    if user.role != 'admin' and (user.role != 'empresa' or user.company_profile.id != application.job.company_id):
        abort(403)

    new_status = request.form.get('status')
    feedback_notes = request.form.get('notes', '').strip()

    valid_statuses = ['recebida', 'em_analise', 'entrevista', 'aprovada', 'rejeitada']
    if new_status in valid_statuses:
        application.status = new_status
        if feedback_notes:
            application.notes = feedback_notes

        # Notificar aluno sobre a mudança de status
        status_labels = {
            'recebida': 'Recebida',
            'em_analise': 'Em análise',
            'entrevista': 'Convocação para Entrevista',
            'aprovada': 'Aprovada!',
            'rejeitada': 'Encerrada'
        }
        notif = Notification(
            user_id=application.student.user_id,
            title='Atualização de Candidatura',
            message=f"Seu status na vaga '{application.job.title}' mudou para: {status_labels.get(new_status, new_status)}.",
            link=url_for('jobs.job_detail', job_id=application.job.id)
        )
        db.session.add(notif)
        db.session.commit()
        flash('Status da candidatura atualizado com sucesso!', 'success')

    return redirect(url_for('company.job_candidates', job_id=application.job_id))
