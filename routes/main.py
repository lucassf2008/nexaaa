import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
from models import (
    db, User, StudentProfile, CompanyProfile, Job, Post, Comment, Like, Follow, Connection, Notification
)
from auth import login_required

main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@main_bp.route('/')
@main_bp.route('/feed')
def feed():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = db.session.get(User, session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    # Filtro opcional por categoria
    category = request.args.get('categoria')
    posts_query = Post.query.order_by(Post.created_at.desc())
    if category:
        posts_query = posts_query.filter_by(category=category)
    posts = posts_query.all()

    # Sugestões de networking para o usuário atual
    suggested_students = []
    if user.role == 'aluno':
        # Sugere outros alunos de áreas semelhantes ou cursos SENAI
        suggested_students = StudentProfile.query.filter(
            StudentProfile.user_id != user.id
        ).limit(5).all()
    else:
        suggested_students = StudentProfile.query.limit(5).all()

    suggested_companies = CompanyProfile.query.filter_by(is_authorized=True, is_blocked=False).limit(4).all()

    # IDs de posts curtidos pelo usuário logado
    liked_post_ids = {like.post_id for like in Like.query.filter_by(user_id=user.id).all()}

    # IDs de empresas seguidas
    followed_company_ids = {follow.company_id for follow in Follow.query.filter_by(follower_id=user.id).all()}

    return render_template(
        'feed.html',
        posts=posts,
        suggested_students=suggested_students,
        suggested_companies=suggested_companies,
        liked_post_ids=liked_post_ids,
        followed_company_ids=followed_company_ids,
        current_category=category or 'todas'
    )


@main_bp.route('/post/novo', methods=['POST'])
@login_required
def create_post():
    user = db.session.get(User, session['user_id'])
    content = request.form.get('content', '').strip()
    category = request.form.get('category', 'novidades')
    title = request.form.get('title', '').strip()

    if not content:
        flash('O conteúdo da publicação não pode ser vazio.', 'warning')
        return redirect(url_for('main.feed'))

    image_url = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(f"post_{user.id}_{file.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_url = f"/static/uploads/{filename}"

    post = Post(
        user_id=user.id,
        title=title or None,
        content=content,
        category=category,
        image_url=image_url
    )
    db.session.add(post)
    db.session.commit()

    flash('Publicação compartilhada com sucesso na rede Nexa SENAI!', 'success')
    return redirect(url_for('main.feed'))


@main_bp.route('/post/<int:post_id>/comentar', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()
    if not content:
        flash('O comentário não pode ser vazio.', 'warning')
        return redirect(url_for('main.feed'))

    comment = Comment(
        post_id=post.id,
        user_id=session['user_id'],
        content=content
    )
    db.session.add(comment)

    # Notificação ao autor do post (se não for o mesmo)
    if post.user_id != session['user_id']:
        notif = Notification(
            user_id=post.user_id,
            title='Novo comentário na sua publicação',
            message=f"{g.current_user.display_name} comentou no seu post.",
            link=url_for('main.feed')
        )
        db.session.add(notif)

    db.session.commit()
    flash('Comentário publicado!', 'success')
    return redirect(url_for('main.feed'))


@main_bp.route('/post/<int:post_id>/curtir', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = session['user_id']
    existing_like = Like.query.filter_by(post_id=post.id, user_id=user_id).first()

    liked = False
    if existing_like:
        db.session.delete(existing_like)
    else:
        new_like = Like(post_id=post.id, user_id=user_id)
        db.session.add(new_like)
        liked = True
    db.session.commit()

    likes_count = post.likes.count()
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'liked': liked, 'likes_count': likes_count})
    return redirect(url_for('main.feed'))


@main_bp.route('/empresa/<int:company_id>/seguir', methods=['POST'])
@login_required
def toggle_follow(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    user_id = session['user_id']

    follow = Follow.query.filter_by(follower_id=user_id, company_id=company.id).first()
    following = False
    if follow:
        db.session.delete(follow)
    else:
        new_follow = Follow(follower_id=user_id, company_id=company.id)
        db.session.add(new_follow)
        following = True
    db.session.commit()

    followers_count = company.followers.count()
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'following': following, 'followers_count': followers_count})
    
    flash(f"Você {'agora está seguindo' if following else 'deixou de seguir'} a empresa {company.name}.", 'info')
    return redirect(request.referrer or url_for('company.profile_view', company_id=company.id))


@main_bp.route('/conectar/<int:target_user_id>', methods=['POST'])
@login_required
def send_connection_request(target_user_id):
    user_id = session['user_id']
    if user_id == target_user_id:
        flash('Você não pode se conectar consigo mesmo.', 'warning')
        return redirect(request.referrer or url_for('main.feed'))

    existing = Connection.query.filter(
        ((Connection.requester_id == user_id) & (Connection.addressee_id == target_user_id)) |
        ((Connection.requester_id == target_user_id) & (Connection.addressee_id == user_id))
    ).first()

    if existing:
        flash('Já existe uma solicitação ou conexão com este usuário.', 'info')
        return redirect(request.referrer or url_for('main.feed'))

    conn = Connection(
        requester_id=user_id,
        addressee_id=target_user_id,
        status='aceita'  # Aceite direto para fluidez de networking ou pendente
    )
    db.session.add(conn)

    # Notificação
    notif = Notification(
        user_id=target_user_id,
        title='Nova Conexão Profissional',
        message=f"{g.current_user.display_name} conectou-se a você no Nexa SENAI.",
        link=url_for('profile.student_profile', student_id=g.current_user.student_profile.id if g.current_user.student_profile else 1)
    )
    db.session.add(notif)
    db.session.commit()

    flash('Conexão realizada com sucesso!', 'success')
    return redirect(request.referrer or url_for('main.feed'))


@main_bp.route('/busca')
@login_required
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('main.feed'))

    jobs = Job.query.filter(
        (Job.title.ilike(f'%{query}%')) |
        (Job.description.ilike(f'%{query}%')) |
        (Job.area.ilike(f'%{query}%'))
    ).all()

    companies = CompanyProfile.query.filter(
        (CompanyProfile.name.ilike(f'%{query}%')) |
        (CompanyProfile.sector.ilike(f'%{query}%')) |
        (CompanyProfile.headline.ilike(f'%{query}%'))
    ).all()

    students = StudentProfile.query.filter(
        (StudentProfile.full_name.ilike(f'%{query}%')) |
        (StudentProfile.senai_course.ilike(f'%{query}%')) |
        (StudentProfile.professional_area.ilike(f'%{query}%'))
    ).all()

    return render_template('search_results.html', query=query, jobs=jobs, companies=companies, students=students)


@main_bp.route('/baixar-projeto')
def download_project_zip():
    zip_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'nexa_senai.zip'))
    if not os.path.exists(zip_path):
        import shutil
        project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        zip_path = shutil.make_archive(os.path.join(os.path.dirname(project_dir), 'nexa_senai'), 'zip', project_dir)
    return send_file(zip_path, as_attachment=True, download_name='nexa_senai.zip')
