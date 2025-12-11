"""
Service de gestion des fichiers uploadés
"""

import os
import uuid
import magic
from werkzeug.utils import secure_filename
from PIL import Image

# Extensions autorisées avec leurs types MIME
ALLOWED_FILES = {
    # Documents
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'odt': 'application/vnd.oasis.opendocument.text',
    'rtf': 'application/rtf',

    # Images
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'webp': 'image/webp',
    'bmp': 'image/bmp',
    'svg': 'image/svg+xml',

    # Vidéos
    'mp4': 'video/mp4',
    'avi': 'video/x-msvideo',
    'mov': 'video/quicktime',
    'mkv': 'video/x-matroska',
    'wmv': 'video/x-ms-wmv',
    'webm': 'video/webm',

    # Scripts
    'ps1': 'text/plain',
    'sh': 'text/x-shellscript',
    'bat': 'text/plain',
    'py': 'text/x-python',

    # Config
    'ini': 'text/plain',
    'conf': 'text/plain',
    'xml': 'application/xml',
    'json': 'application/json',
    'yaml': 'text/plain',
    'yml': 'text/plain',

    # Autres
    'txt': 'text/plain',
    'log': 'text/plain',
    'md': 'text/markdown',
    'zip': 'application/zip',
    'rar': 'application/x-rar-compressed',
    '7z': 'application/x-7z-compressed',
}


class FileServiceError(Exception):
    """Exception pour les erreurs du service de fichiers"""
    pass


class FileService:
    """
    Service de gestion des fichiers uploadés
    """

    def __init__(self, upload_folder='/var/www/kb_basedoc/storage', max_size=50 * 1024 * 1024):
        """
        Initialise le service de fichiers

        Args:
            upload_folder: Dossier racine pour les uploads
            max_size: Taille maximale en bytes (défaut: 50 MB)
        """
        self.upload_folder = upload_folder
        self.max_size = max_size

        # Créer le dossier si inexistant
        os.makedirs(self.upload_folder, exist_ok=True)

    def is_allowed_file(self, filename):
        """
        Vérifie si le fichier est autorisé selon l'extension

        Args:
            filename: Nom du fichier

        Returns:
            True si autorisé, False sinon
        """
        if '.' not in filename:
            return False

        extension = filename.rsplit('.', 1)[1].lower()
        return extension in ALLOWED_FILES

    def validate_mime_type(self, file):
        """
        Valide le type MIME réel du fichier (anti-spoofing)

        Args:
            file: Objet fichier

        Returns:
            True si valide, False sinon

        Raises:
            FileServiceError: Si validation échoue
        """
        try:
            # Lire les premiers 1024 bytes pour détection
            header = file.read(1024)
            file.seek(0)  # Revenir au début

            # Détecter le type MIME réel
            mime_type = magic.from_buffer(header, mime=True)

            # Vérifier si le type MIME est dans les types autorisés
            allowed_mimes = list(ALLOWED_FILES.values())

            # Certains types MIME peuvent varier, être plus permissif
            if mime_type in allowed_mimes:
                return True

            # Accepter aussi text/plain pour les scripts
            if mime_type == 'text/plain' and file.filename.split('.')[-1] in ['ps1', 'sh', 'bat', 'py', 'ini', 'conf', 'txt', 'log', 'yaml', 'yml']:
                return True

            # Accepter octet-stream pour certains types binaires
            if mime_type == 'application/octet-stream' and file.filename.split('.')[-1] in ['zip', 'rar', '7z']:
                return True

            return False

        except Exception as e:
            raise FileServiceError(f"Erreur validation MIME: {str(e)}")

    def validate_file(self, file):
        """
        Validation complète d'un fichier

        Args:
            file: Objet fichier Flask

        Returns:
            Dict avec informations du fichier si valide

        Raises:
            FileServiceError: Si validation échoue
        """
        if not file:
            raise FileServiceError("Aucun fichier fourni")

        if not file.filename:
            raise FileServiceError("Nom de fichier manquant")

        # Vérifier l'extension
        if not self.is_allowed_file(file.filename):
            extension = file.filename.rsplit('.', 1)[1] if '.' in file.filename else 'inconnu'
            raise FileServiceError(f"Type de fichier non autorisé: .{extension}")

        # Vérifier le type MIME
        if not self.validate_mime_type(file):
            raise FileServiceError("Type de fichier invalide (type MIME non autorisé)")

        # Vérifier la taille
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            raise FileServiceError(f"Fichier trop volumineux (max: {max_mb:.0f} MB)")

        if file_size == 0:
            raise FileServiceError("Fichier vide")

        # Informations du fichier
        extension = file.filename.rsplit('.', 1)[1].lower()

        return {
            'original_filename': file.filename,
            'extension': extension,
            'size': file_size,
            'mime_type': ALLOWED_FILES.get(extension, 'application/octet-stream')
        }

    def save_file(self, file, procedure_id):
        """
        Sauvegarde un fichier uploadé

        Args:
            file: Objet fichier Flask
            procedure_id: ID de la procédure

        Returns:
            Dict avec informations du fichier sauvegardé

        Raises:
            FileServiceError: Si sauvegarde échoue
        """
        # Valider le fichier
        file_info = self.validate_file(file)

        # Créer le dossier pour la procédure
        procedure_folder = os.path.join(self.upload_folder, 'procedures', str(procedure_id))
        os.makedirs(procedure_folder, exist_ok=True)

        # Générer un nom de fichier unique
        unique_filename = self._generate_unique_filename(file_info['original_filename'])

        # Chemin complet
        file_path = os.path.join(procedure_folder, unique_filename)

        # Sécuriser le nom de fichier
        safe_filename = secure_filename(unique_filename)
        file_path = os.path.join(procedure_folder, safe_filename)

        # Sauvegarder le fichier
        try:
            file.save(file_path)
        except Exception as e:
            raise FileServiceError(f"Erreur lors de la sauvegarde: {str(e)}")

        # Optimiser si c'est une image
        if file_info['extension'] in ['png', 'jpg', 'jpeg', 'webp', 'bmp']:
            self._optimize_image(file_path)

        return {
            'filename': safe_filename,
            'original_filename': file_info['original_filename'],
            'file_type': file_info['extension'],
            'file_size': file_info['size'],
            'storage_path': file_path
        }

    def delete_file(self, file_path):
        """
        Supprime un fichier

        Args:
            file_path: Chemin du fichier à supprimer
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)

                # Supprimer le dossier s'il est vide
                folder = os.path.dirname(file_path)
                if not os.listdir(folder):
                    os.rmdir(folder)

        except Exception as e:
            raise FileServiceError(f"Erreur lors de la suppression: {str(e)}")

    def _generate_unique_filename(self, original_filename):
        """
        Génère un nom de fichier unique

        Args:
            original_filename: Nom original du fichier

        Returns:
            Nom unique
        """
        # Extraire l'extension
        extension = ''
        if '.' in original_filename:
            extension = '.' + original_filename.rsplit('.', 1)[1].lower()

        # Générer UUID
        unique_id = str(uuid.uuid4())

        # Nom sécurisé original (sans extension)
        safe_name = secure_filename(original_filename.rsplit('.', 1)[0])

        # Limiter la longueur
        if len(safe_name) > 50:
            safe_name = safe_name[:50]

        # Combiner
        unique_filename = f"{safe_name}_{unique_id}{extension}"

        return unique_filename

    def _optimize_image(self, file_path):
        """
        Optimise une image (compression, redimensionnement si trop grande)

        Args:
            file_path: Chemin de l'image
        """
        try:
            img = Image.open(file_path)

            # Redimensionner si trop grande (max 2000px de largeur)
            max_width = 2000
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.LANCZOS)

            # Sauvegarder avec compression
            img.save(file_path, optimize=True, quality=85)

        except Exception:
            # Si optimisation échoue, ce n'est pas bloquant
            pass

    def get_file_icon(self, extension):
        """
        Retourne l'icône emoji pour un type de fichier

        Args:
            extension: Extension du fichier

        Returns:
            Emoji
        """
        icons = {
            'pdf': '📄',
            'doc': '📄',
            'docx': '📄',
            'odt': '📄',
            'rtf': '📄',
            'png': '🖼️',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'gif': '🖼️',
            'webp': '🖼️',
            'bmp': '🖼️',
            'svg': '🖼️',
            'mp4': '🎬',
            'avi': '🎬',
            'mov': '🎬',
            'mkv': '🎬',
            'wmv': '🎬',
            'webm': '🎬',
            'ps1': '💾',
            'sh': '💾',
            'bat': '💾',
            'py': '💾',
            'ini': '⚙️',
            'conf': '⚙️',
            'xml': '⚙️',
            'json': '⚙️',
            'yaml': '⚙️',
            'yml': '⚙️',
            'txt': '📝',
            'log': '📝',
            'md': '📝',
            'zip': '📦',
            'rar': '📦',
            '7z': '📦',
        }

        return icons.get(extension.lower(), '📄')
