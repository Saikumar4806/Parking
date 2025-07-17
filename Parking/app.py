from flask import Flask
from models.file1 import db, User
from controllers.file1 import auth_bp
from controllers.file2 import main_bp
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    db.init_app(app)

    # Context processor for current year in all templates
    @app.context_processor
    def inject_current_year():
        return dict(current_year=datetime.utcnow().year)

    with app.app_context():
        db.create_all()
        # Ensure admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', role='admin')
            admin.set_password('admin')  # Default admin password
            db.session.add(admin)
            db.session.commit()

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 