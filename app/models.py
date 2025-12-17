"""
Modèles de données pour KB Support Basedoc
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """
    Callback pour Flask-Login

    Args:
        user_id: ID de l'utilisateur

    Returns:
        Instance User ou None
    """
    return User.query.get(int(user_id))


# Table d'association pour les tags
procedure_tags = db.Table('procedure_tags',
    db.Column('procedure_id', db.Integer, db.ForeignKey('procedures.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    db.Column('is_ai_generated', db.Boolean, default=False),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)


class User(UserMixin, db.Model):
    """Modèle Utilisateur"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relations
    procedures = db.relationship('Procedure', backref='creator', lazy='dynamic', foreign_keys='Procedure.created_by')
    versions = db.relationship('ProcedureVersion', backref='author', lazy='dynamic', foreign_keys='ProcedureVersion.changed_by')

    def set_password(self, password):
        """
        Définit le mot de passe hashé

        Args:
            password: Mot de passe en clair
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Vérifie le mot de passe

        Args:
            password: Mot de passe à vérifier

        Returns:
            True si correct, False sinon
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Category(db.Model):
    """Modèle Catégorie"""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    short_name = db.Column(db.String(10), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    display_order = db.Column(db.Integer, default=0)
    color_code = db.Column(db.String(7))  # Format: #06b6d4
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    procedures = db.relationship('Procedure', backref='category', lazy='dynamic')

    def get_full_path(self):
        """
        Retourne le chemin complet de la catégorie

        Returns:
            String "Parent > Enfant"
        """
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def __repr__(self):
        return f'<Category {self.name}>'


class Procedure(db.Model):
    """Modèle Procédure"""

    __tablename__ = 'procedures'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)
    description = db.Column(db.Text)
    estimated_time = db.Column(db.Integer)  # En minutes
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = db.Column(db.Boolean, default=False, index=True)
    useful_count = db.Column(db.Integer, default=0)  # Compteur de votes "utile"

    # Relations
    tags = db.relationship('Tag', secondary=procedure_tags, backref=db.backref('procedures', lazy='dynamic'))
    attachments = db.relationship('Attachment', backref='procedure', lazy='dynamic', cascade='all, delete-orphan')
    versions = db.relationship('ProcedureVersion', backref='procedure', lazy='dynamic', cascade='all, delete-orphan', order_by='ProcedureVersion.version_number.desc()')

    def get_latest_version_number(self):
        """
        Retourne le numéro de la dernière version

        Returns:
            Numéro de version (int) ou 0 si aucune version
        """
        latest = self.versions.first()
        return latest.version_number if latest else 0

    def create_version(self, user_id):
        """
        Crée une nouvelle version de la procédure

        Args:
            user_id: ID de l'utilisateur qui modifie
        """
        version_number = self.get_latest_version_number() + 1

        version = ProcedureVersion(
            procedure_id=self.id,
            version_number=version_number,
            content=self.content,
            changed_by=user_id
        )

        db.session.add(version)

    def increment_useful(self):
        """Incrémente le compteur 'utile'"""
        self.useful_count += 1

    def __repr__(self):
        return f'<Procedure {self.id}: {self.title[:30]}...>'


class Script(db.Model):
    """Modèle Script - Espace collaboratif pour partager des scripts"""

    __tablename__ = 'scripts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False, index=True)
    description = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), nullable=False, index=True)  # PowerShell, Bash, Python, etc.
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    verification_notes = db.Column(db.Text)
    ai_suggestions = db.Column(db.Text)  # Suggestions de l'IA stockées en JSON
    status = db.Column(db.String(20), default='draft', index=True)  # draft, published, archived

    # Relations
    author = db.relationship('User', backref='scripts', foreign_keys=[author_id])

    def __repr__(self):
        return f'<Script {self.id}: {self.title[:30]}...>'


class FAQ(db.Model):
    """Modèle FAQ - Questions Fréquemment Posées"""

    __tablename__ = 'faqs'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False, index=True)
    answer = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True, index=True)
    view_count = db.Column(db.Integer, default=0)
    helpful_count = db.Column(db.Integer, default=0)

    # Relations
    category = db.relationship('Category', backref='faqs')
    author = db.relationship('User', backref='faqs', foreign_keys=[created_by])

    def increment_view(self):
        """Incrémente le compteur de vues"""
        self.view_count += 1

    def increment_helpful(self):
        """Incrémente le compteur 'utile'"""
        self.helpful_count += 1

    def __repr__(self):
        return f'<FAQ {self.id}: {self.question[:30]}...>'


class Software(db.Model):
    """Modèle Logiciel - Outils et logiciels utiles"""

    __tablename__ = 'software'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_free = db.Column(db.Boolean, default=True)
    platform = db.Column(db.String(100))  # Windows, Linux, Mac, Web, etc.
    useful_count = db.Column(db.Integer, default=0)

    # Relations
    category = db.relationship('Category', backref='software')
    contributor = db.relationship('User', backref='software', foreign_keys=[added_by])

    def increment_useful(self):
        """Incrémente le compteur 'utile'"""
        self.useful_count += 1

    def __repr__(self):
        return f'<Software {self.id}: {self.name}>'


class Tag(db.Model):
    """Modèle Tag"""

    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def increment_usage(self):
        """Incrémente le compteur d'utilisation"""
        self.usage_count += 1

    def decrement_usage(self):
        """Décrémente le compteur d'utilisation"""
        if self.usage_count > 0:
            self.usage_count -= 1

    @classmethod
    def get_or_create(cls, tag_name):
        """
        Récupère ou crée un tag

        Args:
            tag_name: Nom du tag

        Returns:
            Instance Tag
        """
        tag = cls.query.filter_by(name=tag_name).first()

        if not tag:
            tag = cls(name=tag_name)
            db.session.add(tag)

        return tag

    def __repr__(self):
        return f'<Tag {self.name}>'


class Attachment(db.Model):
    """Modèle Fichier Joint"""

    __tablename__ = 'attachments'

    id = db.Column(db.Integer, primary_key=True)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedures.id', ondelete='CASCADE'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)  # Nom stocké (unique)
    original_filename = db.Column(db.String(255), nullable=False)  # Nom original
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.BigInteger)  # En bytes
    storage_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_file_extension(self):
        """
        Retourne l'extension du fichier

        Returns:
            Extension (ex: 'pdf', 'ps1')
        """
        return self.original_filename.rsplit('.', 1)[1].lower() if '.' in self.original_filename else ''

    def get_size_human_readable(self):
        """
        Retourne la taille en format lisible

        Returns:
            String (ex: '2.5 MB')
        """
        size = self.file_size

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0

        return f"{size:.1f} TB"

    def __repr__(self):
        return f'<Attachment {self.original_filename}>'


class ProcedureVersion(db.Model):
    """Modèle Version de Procédure"""

    __tablename__ = 'procedure_versions'

    id = db.Column(db.Integer, primary_key=True)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedures.id', ondelete='CASCADE'), nullable=False, index=True)
    version_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Index composite pour performance
    __table_args__ = (
        db.Index('idx_procedure_version', 'procedure_id', 'version_number'),
    )

    def __repr__(self):
        return f'<ProcedureVersion {self.procedure_id} v{self.version_number}>'


class Setting(db.Model):
    """Modèle Configuration"""

    __tablename__ = 'settings'

    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get(cls, key, default=None):
        """
        Récupère une valeur de configuration

        Args:
            key: Clé de configuration
            default: Valeur par défaut si non trouvée

        Returns:
            Valeur de configuration ou default
        """
        setting = cls.query.get(key)
        return setting.value if setting else default

    @classmethod
    def set(cls, key, value):
        """
        Définit une valeur de configuration

        Args:
            key: Clé de configuration
            value: Valeur à stocker
        """
        setting = cls.query.get(key)

        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = cls(key=key, value=value)
            db.session.add(setting)

        db.session.commit()

    def __repr__(self):
        return f'<Setting {self.key}={self.value}>'


class ActionLog(db.Model):
    """Modèle Audit Log - Historique des actions"""

    __tablename__ = 'action_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)  # create, update, delete, archive, restore
    entity_type = db.Column(db.String(50), nullable=False, index=True)  # procedure, script, faq, software, user, category
    entity_id = db.Column(db.Integer, nullable=False, index=True)
    entity_name = db.Column(db.String(500))  # Nom de l'entité pour faciliter la lecture
    details = db.Column(db.Text)  # JSON avec détails de la modification
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relations
    user = db.relationship('User', backref='action_logs', foreign_keys=[user_id])

    # Index composite pour les requêtes fréquentes
    __table_args__ = (
        db.Index('idx_entity_lookup', 'entity_type', 'entity_id'),
        db.Index('idx_user_action', 'user_id', 'action_type'),
        db.Index('idx_date_action', 'created_at', 'action_type'),
    )

    @classmethod
    def log_action(cls, action_type, entity_type, entity_id, entity_name=None, details=None, user_id=None, request_obj=None):
        """
        Enregistre une action dans le log

        Args:
            action_type: Type d'action (create, update, delete, etc.)
            entity_type: Type d'entité (procedure, script, etc.)
            entity_id: ID de l'entité
            entity_name: Nom de l'entité (optionnel)
            details: Détails supplémentaires en JSON (optionnel)
            user_id: ID de l'utilisateur (optionnel)
            request_obj: Objet Flask request pour IP et user agent (optionnel)

        Returns:
            Instance ActionLog créée
        """
        log_entry = cls(
            user_id=user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            details=details
        )

        if request_obj:
            log_entry.ip_address = request_obj.remote_addr
            log_entry.user_agent = request_obj.headers.get('User-Agent', '')[:500]

        db.session.add(log_entry)
        # Note: db.session.commit() doit être appelé par l'appelant

        return log_entry

    def get_action_icon(self):
        """Retourne une icône pour le type d'action"""
        icons = {
            'create': '➕',
            'update': '✏️',
            'delete': '🗑️',
            'archive': '📦',
            'restore': '♻️',
            'login': '🔐',
            'logout': '🚪',
            'useful': '👍',
            'comment': '💬',
            'export': '📥'
        }
        return icons.get(self.action_type, '📝')

    def get_action_label(self):
        """Retourne un label lisible pour le type d'action"""
        labels = {
            'create': 'Création',
            'update': 'Modification',
            'delete': 'Suppression',
            'archive': 'Archivage',
            'restore': 'Restauration',
            'login': 'Connexion',
            'logout': 'Déconnexion',
            'useful': 'Vote utile',
            'comment': 'Commentaire',
            'export': 'Export'
        }
        return labels.get(self.action_type, self.action_type)

    def get_entity_label(self):
        """Retourne un label lisible pour le type d'entité"""
        labels = {
            'procedure': 'Procédure',
            'script': 'Script',
            'faq': 'FAQ',
            'software': 'Logiciel',
            'user': 'Utilisateur',
            'category': 'Catégorie',
            'comment': 'Commentaire',
            'tag': 'Tag'
        }
        return labels.get(self.entity_type, self.entity_type)

    def __repr__(self):
        return f'<ActionLog {self.action_type} {self.entity_type} #{self.entity_id}>'


class Comment(db.Model):
    """Modèle Commentaire - Discussions sous les procédures"""

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedures.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id', ondelete='CASCADE'), nullable=True, index=True)  # Pour les réponses
    content = db.Column(db.Text, nullable=False)
    is_edited = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    procedure = db.relationship('Procedure', backref=db.backref('comments', lazy='dynamic', cascade='all, delete-orphan'))
    user = db.relationship('User', backref='comments', foreign_keys=[user_id])
    parent = db.relationship('Comment', remote_side=[id], backref=db.backref('replies', lazy='dynamic'))

    # Index composite
    __table_args__ = (
        db.Index('idx_procedure_created', 'procedure_id', 'created_at'),
    )

    def get_replies_count(self):
        """Retourne le nombre de réponses"""
        return self.replies.count()

    def is_reply(self):
        """Vérifie si c'est une réponse à un autre commentaire"""
        return self.parent_id is not None

    def __repr__(self):
        return f'<Comment #{self.id} on Procedure #{self.procedure_id}>'
