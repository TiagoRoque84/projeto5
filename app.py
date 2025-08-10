
from flask import Flask
from config import Config
from extensions import db, login_manager, migrate
from models import User, DocumentType
import os
from apscheduler.schedulers.background import BackgroundScheduler
from alerts import send_alerts

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    migrate.init_app(app, db)

    from blueprints.auth.routes import auth_bp
    from blueprints.main.routes import main_bp
    from blueprints.companies.routes import companies_bp
    from blueprints.documents.routes import documents_bp
    from blueprints.hr.routes import hr_bp
    from blueprints.admin.routes import admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(companies_bp, url_prefix="/empresas")
    app.register_blueprint(documents_bp, url_prefix="/documentos")
    app.register_blueprint(hr_bp, url_prefix="/rh")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.context_processor
    def inject_today():
        from datetime import date
        return {"today": date.today()}

    # Scheduler diário 08:00
    try:
        sched = BackgroundScheduler(daemon=True, timezone='America/Sao_Paulo')
        sched.add_job(lambda: app.app_context().push() or send_alerts(), 'cron', hour=8, minute=0)
        sched.start()
    except Exception as e:
        print('[scheduler] não iniciado:', e)

    @app.cli.command("init-data")
    def init_data():
        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", role="admin", active=True)
            admin.set_password("admin123")
            db.session.add(admin)
        base_types = ["Licença Ambiental", "Certificado de Regularidade", "Certidão Negativa", "Contrato Social"]
        for t in base_types:
            if not DocumentType.query.filter_by(nome=t).first():
                db.session.add(DocumentType(nome=t))
        db.session.commit()
        print("Dados iniciais criados. Usuário: admin / Senha: admin123")
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
