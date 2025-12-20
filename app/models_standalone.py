"""
Modèles de données simplifiés pour KB Support Basedoc Standalone
Version mono-utilisateur sans fonctionnalités complexes
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Callback pour Flask-Login"""
    return User.query.get(int(user_id))


# Table d'association pour les tags
procedure_tags = db.Table('procedure_tags',
    db.Column('procedure_id', db.Integer, db.ForeignKey('procedures.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

script_tags = db.Table('script_tags',
    db.Column('script_id', db.Integer, db.ForeignKey('scripts.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

faq_tags = db.Table('faq_tags',
    db.Column('faq_id', db.Integer, db.ForeignKey('faqs.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class User(UserMixin, db.Model):
    """Modèle Utilisateur simplifié pour standalone"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Définit le mot de passe hashé"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)


class Tag(db.Model):
    """Tags pour organiser le contenu"""

    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    color = db.Column(db.String(7), default='#00ff88')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Tag {self.name}>'


class Procedure(db.Model):
    """Procédures IT"""

    __tablename__ = 'procedures'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)

    # Métadonnées
    is_published = db.Column(db.Boolean, default=True, index=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relations
    tags = db.relationship('Tag', secondary=procedure_tags, backref=db.backref('procedures', lazy='dynamic'))
    attachments = db.relationship('Attachment', backref='procedure', lazy='dynamic', cascade='all, delete-orphan')

    # Index pour la recherche full-text
    __table_args__ = (
        db.Index('idx_procedure_search', 'title', 'content', postgresql_using='gin'),
    )

    def __repr__(self):
        return f'<Procedure {self.title}>'


class Script(db.Model):
    """Scripts PowerShell/Bash/Python"""

    __tablename__ = 'scripts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    description = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(20), nullable=False, index=True)  # powershell, bash, python

    # Métadonnées
    status = db.Column(db.String(20), default='published', index=True)  # draft, published
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relations
    tags = db.relationship('Tag', secondary=script_tags, backref=db.backref('scripts', lazy='dynamic'))

    def __repr__(self):
        return f'<Script {self.title}>'


class FAQ(db.Model):
    """Questions/Réponses"""

    __tablename__ = 'faqs'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False, index=True)
    answer = db.Column(db.Text, nullable=False)

    # Métadonnées
    is_published = db.Column(db.Boolean, default=True, index=True)
    view_count = db.Column(db.Integer, default=0)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relations
    tags = db.relationship('Tag', secondary=faq_tags, backref=db.backref('faqs', lazy='dynamic'))

    def __repr__(self):
        return f'<FAQ {self.question[:50]}>'


class Software(db.Model):
    """Catalogue de logiciels"""

    __tablename__ = 'software'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    version = db.Column(db.String(50))
    publisher = db.Column(db.String(255))
    license_type = db.Column(db.String(100))
    license_key = db.Column(db.Text)
    download_url = db.Column(db.String(500))
    documentation_url = db.Column(db.String(500))
    notes = db.Column(db.Text)

    # Métadonnées
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Software {self.name}>'


class Attachment(db.Model):
    """Pièces jointes pour les procédures"""

    __tablename__ = 'attachments'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)

    # Relations
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedures.id'))

    # Métadonnées
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Attachment {self.original_filename}>'


class Setting(db.Model):
    """Paramètres de configuration"""

    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get(key, default=None):
        """Récupère une valeur de paramètre"""
        setting = Setting.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def set(key, value, description=None):
        """Définit une valeur de paramètre"""
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = Setting(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
        return setting

    def __repr__(self):
        return f'<Setting {self.key}>'
