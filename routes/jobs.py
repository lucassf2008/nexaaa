from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, g
from models import db, User, Job, CompanyProfile, Application, SavedJob, Notification
from auth import login_required

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/vagas')
def list_jobs():
    query_text = request.args.get('q', '').strip()
    selected_types = request.args.getlist('tipo')
    selected_areas = request.args.getlist('area')
    selected_modalities = request.args.getlist('modalidade')
    selected_location = request.args.get('localizacao', '').strip()
    selected_company = request.args.get('empresa', '').strip()
    selected_experience = request.args.get('experiencia', '').strip()

    jobs_query = Job.query.filter_by(status='aberta').order_by(Job.created_at.desc())

    if query_text:
        jobs_query = jobs_query.filter(
            (Job.title.ilike(f'%{query_text}%')) |
            (Job.description.ilike(f'%{query_text}%')) |
            (Job.requirements.ilike(f'%{query_text}%'))
        )

    if selected_types:
        jobs_query = jobs_query.filter(Job.job_type.in_(selected_types))

    if selected_areas:
        jobs_query = jobs_query.filter(Job.area.in_(selected_areas))

    if selected_modalities:
        jobs_query = jobs_query.filter(Job.modality.in_(selected_modalities))

    if selected_location:
        jobs_query = jobs_query.filter(Job.location.ilike(f'%{selected_location}%'))

    if selected_company:
        jobs_query = jobs_query.join(CompanyProfile).filter(CompanyProfile.name.ilike(f'%{selected_company}%'))

    if selected_experience:
        jobs_query = jobs_query.filter(Job.experience_level == selected_experience)

    jobs = jobs_query.all()

    # Informações do usuário logado (candidaturas e vagas salvas)
    applied_job_ids = set()
    saved_job_ids = set()
    if g.current_user and g.current_user.student_profile:
        student = g.current_user.student_profile
        applied_job_ids = {app.job_id for app in student.applications}
        saved_job_ids = {saved.job_id for saved in student.saved_jobs}

    # Listas distintas para popular os filtros dinamicamente
    all_areas = [
        'Desenvolvimento de software', 'Dados', 'Design', 'Eletrônica',
        'Automação industrial', 'Administração', 'Marketing', 'Mecânica', 'Outras áreas'
    ]
    all_types = ['Estágio', 'Emprego efetivo', 'Jovem aprendiz', 'Projeto', 'Freelancer']
    all_modalities = ['Presencial', 'Híbrida', 'Remota']
    all_companies = CompanyProfile.query.filter_by(is_authorized=True).all()

    return render_template(
        'jobs.html',
        jobs=jobs,
        all_areas=all_areas,
        all_types=all_types,
        all_modalities=all_modalities,
        all_companies=all_companies,
        selected_types=selected_types,
        selected_areas=selected_areas,
        selected_modalities=selected_modalities,
        selected_location=selected_location,
        selected_company=selected_company,
        selected_experience=selected_experience,
        query_text=query_text,
        applied_job_ids=applied_job_ids,
        saved_job_ids=saved_job_ids
    )


@jobs_bp.route('/vagas/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    has_applied = False
    is_saved = False
    existing_application = None

    if g.current_user and g.current_user.student_profile:
        student = g.current_user.student_profile
        existing_application = Application.query.filter_by(
            job_id=job.id, student_id=student.id
        ).first()
        has_applied = existing_application is not None
        is_saved = SavedJob.query.filter_by(
            job_id=job.id, student_id=student.id
        ).first() is not None

    return render_template(
        'job_detail.html',
        job=job,
        has_applied=has_applied,
        existing_application=existing_application,
        is_saved=is_saved
    )


@jobs_bp.route('/vagas/<int:job_id>/candidatar', methods=['POST'])
@login_required
def apply_to_job(job_id):
    job = Job.query.get_or_404(job_id)
    user = g.current_user

    if user.role != 'aluno' or not user.student_profile:
        flash('Apenas contas de alunos e ex-alunos podem se candidatar a vagas de emprego.', 'warning')
        return redirect(url_for('jobs.job_detail', job_id=job.id))

    student = user.student_profile

    # Prevenir candidaturas duplicadas
    existing_app = Application.query.filter_by(job_id=job.id, student_id=student.id).first()
    if existing_app:
        flash('Você já se candidatou para esta vaga. Acompanhe o status em Minhas Candidaturas.', 'info')
        return redirect(url_for('jobs.job_detail', job_id=job.id))

    notes = request.form.get('cover_letter', '').strip()

    application = Application(
        job_id=job.id,
        student_id=student.id,
        status='recebida',
        notes=notes or None
    )
    db.session.add(application)

    # Notificar a empresa
    company_user = job.company.user
    if company_user:
        notif = Notification(
            user_id=company_user.id,
            title='Nova Candidatura Recebida',
            message=f"{student.full_name} candidatou-se para a vaga '{job.title}'.",
            link=url_for('company.job_candidates', job_id=job.id)
        )
        db.session.add(notif)

    db.session.commit()
    flash(f'Parabéns! Sua candidatura para a vaga "{job.title}" foi enviada com sucesso.', 'success')
    return redirect(url_for('jobs.job_detail', job_id=job.id))


@jobs_bp.route('/vagas/<int:job_id>/salvar', methods=['POST'])
@login_required
def toggle_save_job(job_id):
    job = Job.query.get_or_404(job_id)
    user = g.current_user

    if user.role != 'aluno' or not user.student_profile:
        flash('Apenas alunos podem salvar vagas favoritas.', 'warning')
        return redirect(url_for('jobs.list_jobs'))

    student = user.student_profile
    saved = SavedJob.query.filter_by(job_id=job.id, student_id=student.id).first()
    is_saved = False

    if saved:
        db.session.delete(saved)
    else:
        new_save = SavedJob(job_id=job.id, student_id=student.id)
        db.session.add(new_save)
        is_saved = True

    db.session.commit()

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'saved': is_saved})

    flash(f"Vaga {'salva nos seus favoritos' if is_saved else 'removida dos favoritos'}.", 'info')
    return redirect(request.referrer or url_for('jobs.list_jobs'))


@jobs_bp.route('/minhas-candidaturas')
@login_required
def my_applications():
    user = g.current_user
    if user.role != 'aluno' or not user.student_profile:
        flash('Apenas alunos possuem registro de candidaturas.', 'warning')
        return redirect(url_for('jobs.list_jobs'))

    student = user.student_profile
    applications = Application.query.filter_by(student_id=student.id).order_by(Application.created_at.desc()).all()
    saved_jobs = [s.job for s in student.saved_jobs]

    return render_template('my_applications.html', applications=applications, saved_jobs=saved_jobs)
