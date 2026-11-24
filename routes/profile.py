import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, g, abort
from werkzeug.utils import secure_filename
from models import (
    db, User, StudentProfile, Experience, Skill, Education, Project, Certificate, Connection, Message
)
from auth import login_required

profile_bp = Blueprint('profile', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@profile_bp.route('/perfil/aluno')
@login_required
def my_student_profile():
    user = g.current_user
    if user.role == 'aluno' and user.student_profile:
        return redirect(url_for('profile.student_profile', student_id=user.student_profile.id))
    # Se for empresa ou admin navegando
    first_student = StudentProfile.query.first()
    if first_student:
        return redirect(url_for('profile.student_profile', student_id=first_student.id))
    flash('Nenhum perfil de aluno encontrado.', 'warning')
    return redirect(url_for('main.feed'))


@profile_bp.route('/perfil/aluno/<int:student_id>')
@login_required
def student_profile(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    is_owner = (g.current_user.id == student.user_id)

    # Status de conexão com o perfil visualizado
    connection_status = None
    if not is_owner:
        conn = Connection.query.filter(
            ((Connection.requester_id == g.current_user.id) & (Connection.addressee_id == student.user_id)) |
            ((Connection.requester_id == student.user_id) & (Connection.addressee_id == g.current_user.id))
        ).first()
        if conn:
            connection_status = conn.status

    # Mensagens recentes para a coluna lateral (Desktop 1 - Novas Mensagens)
    # Busca as conversas mais recentes do usuário logado
    recent_messages = []
    # Coleta usuários com quem o usuário atual conversou
    all_msgs = Message.query.filter(
        (Message.sender_id == g.current_user.id) | (Message.receiver_id == g.current_user.id)
    ).order_by(Message.created_at.desc()).all()

    seen_contacts = set()
    for m in all_msgs:
        other_user = m.receiver if m.sender_id == g.current_user.id else m.sender
        if other_user.id not in seen_contacts and other_user.id != g.current_user.id:
            seen_contacts.add(other_user.id)
            recent_messages.append({
                'user': other_user,
                'last_message': m.content,
                'time': m.created_at.strftime('%H:%M'),
                'is_unread': (not m.is_read and m.receiver_id == g.current_user.id)
            })
            if len(recent_messages) >= 6:
                break

    # Se não houver conversas, sugere contatos do SENAI para preencher o visual do mockup
    suggested_contacts = []
    if len(recent_messages) < 4:
        suggested_students = StudentProfile.query.filter(StudentProfile.id != student.id).limit(5).all()
        for s in suggested_students:
            if s.user_id not in seen_contacts and s.user_id != g.current_user.id:
                suggested_contacts.append({
                    'user': s.user,
                    'last_message': 'Olá! Vamos nos conectar no Nexa SENAI?',
                    'time': 'Hoje',
                    'is_unread': False
                })

    return render_template(
        'profile_student.html',
        student=student,
        is_owner=is_owner,
        connection_status=connection_status,
        recent_messages=recent_messages,
        suggested_contacts=suggested_contacts
    )


@profile_bp.route('/perfil/aluno/editar', methods=['GET', 'POST'])
@login_required
def edit_student_profile():
    user = g.current_user
    if user.role != 'aluno' or not user.student_profile:
        flash('Acesso negado. Apenas o aluno proprietário pode editar seu perfil.', 'danger')
        return redirect(url_for('main.feed'))

    student = user.student_profile

    if request.method == 'POST':
        student.full_name = request.form.get('full_name', student.full_name).strip()
        student.headline = request.form.get('headline', student.headline).strip()
        student.about_me = request.form.get('about_me', student.about_me).strip()
        student.phone = request.form.get('phone', student.phone).strip()
        student.city = request.form.get('city', student.city).strip()
        student.state = request.form.get('state', student.state).strip()
        student.senai_course = request.form.get('senai_course', student.senai_course).strip()
        student.course_status = request.form.get('course_status', student.course_status).strip()
        student.professional_area = request.form.get('professional_area', student.professional_area).strip()

        # Upload de avatar
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"avatar_student_{student.id}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                student.avatar_url = f"/static/uploads/{filename}"

        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('profile.student_profile', student_id=student.id))

    return render_template('edit_student_profile.html', student=student)


@profile_bp.route('/perfil/aluno/experiencia/adicionar', methods=['POST'])
@login_required
def add_experience():
    user = g.current_user
    if user.role != 'aluno' or not user.student_profile:
        abort(403)

    company = request.form.get('company', '').strip()
    role = request.form.get('role', '').strip()
    period = request.form.get('period', '').strip()
    description = request.form.get('description', '').strip()

    if company and role:
        exp = Experience(
            student_id=user.student_profile.id,
            company=company,
            role=role,
            period=period or 'Período não informado',
            description=description or None
        )
        db.session.add(exp)
        db.session.commit()
        flash('Experiência adicionada com sucesso!', 'success')

    return redirect(url_for('profile.student_profile', student_id=user.student_profile.id))


@profile_bp.route('/perfil/aluno/experiencia/<int:exp_id>/deletar', methods=['POST'])
@login_required
def delete_experience(exp_id):
    user = g.current_user
    exp = Experience.query.get_or_404(exp_id)
    if exp.student_id != user.student_profile.id:
        abort(403)
    db.session.delete(exp)
    db.session.commit()
    flash('Experiência removida.', 'info')
    return redirect(url_for('profile.student_profile', student_id=user.student_profile.id))


@profile_bp.route('/perfil/aluno/competencia/adicionar', methods=['POST'])
@login_required
def add_skill():
    user = g.current_user
    if user.role != 'aluno' or not user.student_profile:
        abort(403)

    name = request.form.get('name', '').strip()
    level = request.form.get('level', 'Intermediário').strip()

    if name:
        skill = Skill(
            student_id=user.student_profile.id,
            name=name,
            level=level
        )
        db.session.add(skill)
        db.session.commit()
        flash(f'Competência "{name}" adicionada ao perfil!', 'success')

    return redirect(url_for('profile.student_profile', student_id=user.student_profile.id))


@profile_bp.route('/perfil/aluno/competencia/<int:skill_id>/deletar', methods=['POST'])
@login_required
def delete_skill(skill_id):
    user = g.current_user
    skill = Skill.query.get_or_404(skill_id)
    if skill.student_id != user.student_profile.id:
        abort(403)
    db.session.delete(skill)
    db.session.commit()
    flash('Competência removida.', 'info')
    return redirect(url_for('profile.student_profile', student_id=user.student_profile.id))


@profile_bp.route('/perfil/aluno/projeto/adicionar', methods=['POST'])
@login_required
def add_project():
    user = g.current_user
    if user.role != 'aluno' or not user.student_profile:
        abort(403)

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    technologies = request.form.get('technologies', '').strip()
    link_url = request.form.get('link_url', '').strip()

    if title:
        proj = Project(
            student_id=user.student_profile.id,
            title=title,
            description=description,
            technologies=technologies,
            link_url=link_url or None
        )
        db.session.add(proj)
        db.session.commit()
        flash('Projeto adicionado com sucesso!', 'success')

    return redirect(url_for('profile.student_profile', student_id=user.student_profile.id))


@profile_bp.route('/perfil/aluno/projeto/<int:proj_id>/deletar', methods=['POST'])
@login_required
def delete_project(proj_id):
    user = g.current_user
    proj = Project.query.get_or_404(proj_id)
    if proj.student_id != user.student_profile.id:
        abort(403)
    db.session.delete(proj)
    db.session.commit()
    flash('Projeto removido.', 'info')
    return redirect(url_for('profile.student_profile', student_id=user.student_profile.id))
