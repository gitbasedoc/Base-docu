"""
Routes pour la gestion des fichiers et uploads
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import uuid

from app.services.file_service import FileService

files_bp = Blueprint('files', __name__, url_prefix='/files')


@files_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    """
    Upload d'image pour l'éditeur WYSIWYG
    Supporte le drag & drop
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400

    # Vérifier que c'est une image
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

    if file_ext not in allowed_extensions:
        return jsonify({'error': f'Extension non autorisée. Utilisez: {", ".join(allowed_extensions)}'}), 400

    # Vérifier la taille (max 10MB pour les images)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    max_size = 10 * 1024 * 1024  # 10 MB
    if file_size > max_size:
        return jsonify({'error': 'Image trop volumineuse (max 10 MB)'}), 400

    try:
        # Générer un nom de fichier unique
        unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"

        # Créer le répertoire s'il n'existe pas
        upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'storage'), 'images')
        os.makedirs(upload_dir, exist_ok=True)

        # Sauvegarder le fichier
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)

        # URL accessible publiquement
        image_url = f"/uploads/images/{unique_filename}"

        return jsonify({
            'success': True,
            'location': image_url,
            'filename': unique_filename
        }), 200

    except Exception as e:
        current_app.logger.error(f"Erreur upload image: {str(e)}")
        return jsonify({'error': 'Erreur lors de l\'upload'}), 500


@files_bp.route('/import-document', methods=['POST'])
@login_required
def import_document():
    """
    Import d'un document PDF ou Word
    Extrait le texte et le retourne pour insertion dans l'éditeur
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400

    # Vérifier l'extension
    allowed_extensions = {'pdf', 'doc', 'docx'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

    if file_ext not in allowed_extensions:
        return jsonify({'error': f'Extension non autorisée. Utilisez: PDF, DOC, DOCX'}), 400

    try:
        # Sauvegarder temporairement
        temp_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'storage'), 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        temp_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        temp_path = os.path.join(temp_dir, temp_filename)
        file.save(temp_path)

        # Extraire le contenu selon le type
        content = ''
        images = []

        if file_ext == 'pdf':
            content, images = extract_pdf_content(temp_path)
        elif file_ext in ['doc', 'docx']:
            content, images = extract_word_content(temp_path)

        # Nettoyer le fichier temporaire
        os.remove(temp_path)

        return jsonify({
            'success': True,
            'content': content,
            'images': images,
            'filename': file.filename
        }), 200

    except Exception as e:
        current_app.logger.error(f"Erreur import document: {str(e)}")
        return jsonify({'error': f'Erreur lors de l\'import: {str(e)}'}), 500


def extract_pdf_content(file_path):
    """
    Extrait le texte et les images d'un PDF avec PyMuPDF
    """
    try:
        import fitz  # PyMuPDF

        images = []

        # Ouvrir le PDF
        doc = fitz.open(file_path)

        html_content = '<h2>Procédure importée</h2>\n'

        # Extraire le texte de chaque page
        for page_num, page in enumerate(doc):
            text = page.get_text()

            if text.strip():
                html_content += f'<h3>Page {page_num + 1}</h3>\n'

                # Diviser en paragraphes
                paragraphs = text.split('\n\n')
                for para in paragraphs:
                    para = para.strip()
                    if para:
                        # Remplacer les sauts de ligne simples par des espaces
                        para = para.replace('\n', ' ')
                        html_content += f'<p>{para}</p>\n'

        doc.close()

        return html_content, images

    except ImportError:
        raise Exception("PyMuPDF n'est pas installé. Installez-le avec: pip install PyMuPDF")
    except Exception as e:
        raise Exception(f"Erreur extraction PDF: {str(e)}")


def extract_word_content(file_path):
    """
    Extrait le texte et les images d'un document Word
    """
    try:
        from docx import Document
        from docx.oxml.text.paragraph import CT_P
        from docx.oxml.table import CT_Tbl
        from docx.table import _Cell, Table
        from docx.text.paragraph import Paragraph

        content = ""
        images = []

        doc = Document(file_path)

        html_content = '<h2>Procédure importée</h2>\n'

        for element in doc.element.body:
            if isinstance(element, CT_P):
                para = Paragraph(element, doc)
                text = para.text.strip()

                if text:
                    # Détecter les titres (texte en gras ou taille > 11)
                    is_heading = False
                    if para.runs:
                        first_run = para.runs[0]
                        if first_run.bold or (first_run.font.size and first_run.font.size.pt > 11):
                            is_heading = True

                    if is_heading:
                        html_content += f'<h3>{text}</h3>\n'
                    else:
                        html_content += f'<p>{text}</p>\n'

            elif isinstance(element, CT_Tbl):
                table = Table(element, doc)
                html_content += '<table border="1" style="border-collapse: collapse; width: 100%;">\n'

                for row in table.rows:
                    html_content += '  <tr>\n'
                    for cell in row.cells:
                        html_content += f'    <td style="padding: 8px;">{cell.text}</td>\n'
                    html_content += '  </tr>\n'

                html_content += '</table>\n'

        return html_content, images

    except ImportError:
        raise Exception("python-docx n'est pas installé. Installez-le avec: pip install python-docx")
    except Exception as e:
        raise Exception(f"Erreur extraction Word: {str(e)}")
