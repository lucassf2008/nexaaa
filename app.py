import os
import sys

# Garante que o diretório base esteja sempre no sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, g, session, render_template
from config import Config
from models import db, User, Message, Notification
from seed import seed_database

# Blueprints
from auth import auth_bp
from routes.main import main_bp
from routes.jobs import jobs_bp
from routes.profile import profile_bp
from routes.company import company_bp
from routes.messages import messages_bp
from routes.admin import admin_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Garantir que a pasta de uploads exista
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(admin_bp)

    # Injeção global no contexto de templates
    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')
        if user_id:
            g.current_user = db.session.get(User, user_id)
        else:
            g.current_user = None

    @app.context_processor
    def inject_global_data():
        unread_msgs = 0
        unread_notifs = 0
        notifications = []
        if g.current_user:
            unread_msgs = Message.query.filter_by(
                receiver_id=g.current_user.id,
                is_read=False
            ).count()
            unread_notifs = Notification.query.filter_by(
                user_id=g.current_user.id,
                is_read=False
            ).count()
            notifications = Notification.query.filter_by(
                user_id=g.current_user.id
            ).order_by(Notification.created_at.desc()).limit(5).all()

        return dict(
            current_user=g.current_user,
            unread_msgs_count=unread_msgs,
            unread_notifs_count=unread_notifs,
            recent_notifications=notifications
        )

    # Handlers de erro amigáveis
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # Inicialização do banco de dados e seed automático
    with app.app_context():
        db.create_all()
        seed_database()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
