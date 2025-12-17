"""
Service d'export pour procédures (PDF et DOCX)
"""

import io
from datetime import datetime
from html import unescape
from bs4 import BeautifulSoup


class ExportService:
    """Service pour exporter des procédures en PDF et DOCX"""

    @staticmethod
    def generate_pdf(procedure):
        """
        Génère un PDF à partir d'une procédure

        Args:
            procedure: Instance Procedure

        Returns:
            BytesIO contenant le PDF
        """
        try:
            from weasyprint import HTML, CSS
            from flask import render_template_string
        except ImportError:
            raise ImportError("WeasyPrint n'est pas installé. Installez-le avec: pip install weasyprint")

        # Template HTML pour le PDF
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ procedure.title }}</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'DejaVu Sans', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1f2937;
        }
        h1 {
            color: #06b6d4;
            border-bottom: 3px solid #06b6d4;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
            font-size: 24pt;
        }
        h2 {
            color: #0891b2;
            margin-top: 1.5rem;
            font-size: 16pt;
        }
        h3 {
            color: #0e7490;
            margin-top: 1rem;
            font-size: 14pt;
        }
        .metadata {
            background: #f3f4f6;
            border-left: 4px solid #06b6d4;
            padding: 1rem;
            margin-bottom: 1.5rem;
            page-break-inside: avoid;
        }
        .metadata-item {
            margin-bottom: 0.5rem;
        }
        .metadata-label {
            font-weight: bold;
            color: #4b5563;
        }
        .metadata-value {
            color: #1f2937;
        }
        .description {
            background: #f9fafb;
            border-left: 4px solid #10b981;
            padding: 1rem;
            margin-bottom: 1.5rem;
            font-style: italic;
        }
        .content {
            margin-top: 1.5rem;
        }
        .content pre {
            background: #f3f4f6;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            padding: 1rem;
            overflow-x: auto;
            font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
            font-size: 9pt;
        }
        .content code {
            background: #f3f4f6;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
            font-size: 9pt;
        }
        .content table {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }
        .content table th,
        .content table td {
            border: 1px solid #d1d5db;
            padding: 0.5rem;
            text-align: left;
        }
        .content table th {
            background: #f3f4f6;
            font-weight: bold;
        }
        .content ul, .content ol {
            margin-left: 1.5rem;
        }
        .content li {
            margin-bottom: 0.25rem;
        }
        .footer {
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 2px solid #e5e7eb;
            font-size: 9pt;
            color: #6b7280;
            text-align: center;
        }
        .tags {
            margin-top: 1rem;
        }
        .tag {
            display: inline-block;
            background: #e0f2fe;
            color: #0891b2;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            margin-right: 0.5rem;
            font-size: 9pt;
        }
    </style>
</head>
<body>
    <h1>{{ procedure.title }}</h1>

    <div class="metadata">
        <div class="metadata-item">
            <span class="metadata-label">ID:</span>
            <span class="metadata-value">PROC-{{ "%04d"|format(procedure.id) }}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Catégorie:</span>
            <span class="metadata-value">{{ procedure.category.name }}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Créé par:</span>
            <span class="metadata-value">{{ procedure.creator.full_name if procedure.creator else 'Inconnu' }}</span>
        </div>
        <div class="metadata-item">
            <span class="metadata-label">Dernière modification:</span>
            <span class="metadata-value">{{ procedure.updated_at.strftime('%d/%m/%Y %H:%M') }}</span>
        </div>
        {% if procedure.estimated_time %}
        <div class="metadata-item">
            <span class="metadata-label">Temps estimé:</span>
            <span class="metadata-value">{{ procedure.estimated_time }} minutes</span>
        </div>
        {% endif %}
    </div>

    {% if procedure.description %}
    <div class="description">
        <strong>Description:</strong><br>
        {{ procedure.description }}
    </div>
    {% endif %}

    {% if procedure.tags %}
    <div class="tags">
        <strong>Tags:</strong>
        {% for tag in procedure.tags %}
        <span class="tag">{{ tag.name }}</span>
        {% endfor %}
    </div>
    {% endif %}

    <div class="content">
        <h2>Procédure</h2>
        {{ procedure.content|safe }}
    </div>

    <div class="footer">
        Généré le {{ now.strftime('%d/%m/%Y à %H:%M') }} - KB Support Basedoc
    </div>
</body>
</html>
"""

        # Rendre le template
        html_content = render_template_string(
            html_template,
            procedure=procedure,
            now=datetime.utcnow()
        )

        # Générer le PDF
        pdf_file = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)

        return pdf_file

    @staticmethod
    def generate_docx(procedure):
        """
        Génère un DOCX à partir d'une procédure

        Args:
            procedure: Instance Procedure

        Returns:
            BytesIO contenant le DOCX
        """
        try:
            from docx import Document
            from docx.shared import Inches, Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
        except ImportError:
            raise ImportError("python-docx n'est pas installé. Installez-le avec: pip install python-docx")

        # Créer le document
        doc = Document()

        # Titre
        title = doc.add_heading(procedure.title, 0)
        title.alignment = WD_ALIGN_PARAGRAPH.LEFT

        # Métadonnées
        doc.add_heading('Informations', level=2)

        metadata_table = doc.add_table(rows=4 + (1 if procedure.estimated_time else 0), cols=2)
        metadata_table.style = 'Light Grid Accent 1'

        row_idx = 0

        # ID
        row = metadata_table.rows[row_idx]
        row.cells[0].text = 'ID'
        row.cells[1].text = f'PROC-{procedure.id:04d}'
        row_idx += 1

        # Catégorie
        row = metadata_table.rows[row_idx]
        row.cells[0].text = 'Catégorie'
        row.cells[1].text = procedure.category.name
        row_idx += 1

        # Créé par
        row = metadata_table.rows[row_idx]
        row.cells[0].text = 'Créé par'
        row.cells[1].text = procedure.creator.full_name if procedure.creator else 'Inconnu'
        row_idx += 1

        # Dernière modification
        row = metadata_table.rows[row_idx]
        row.cells[0].text = 'Dernière modification'
        row.cells[1].text = procedure.updated_at.strftime('%d/%m/%Y %H:%M')
        row_idx += 1

        # Temps estimé (optionnel)
        if procedure.estimated_time:
            row = metadata_table.rows[row_idx]
            row.cells[0].text = 'Temps estimé'
            row.cells[1].text = f'{procedure.estimated_time} minutes'

        doc.add_paragraph()

        # Description
        if procedure.description:
            doc.add_heading('Description', level=2)
            doc.add_paragraph(procedure.description)
            doc.add_paragraph()

        # Tags
        if procedure.tags:
            doc.add_heading('Tags', level=2)
            tags_text = ', '.join([tag.name for tag in procedure.tags])
            doc.add_paragraph(tags_text)
            doc.add_paragraph()

        # Contenu
        doc.add_heading('Procédure', level=2)

        # Parser le HTML et convertir en texte formaté
        ExportService._html_to_docx(procedure.content, doc)

        # Footer
        doc.add_paragraph()
        footer = doc.add_paragraph()
        footer_run = footer.add_run(f'Généré le {datetime.utcnow().strftime("%d/%m/%Y à %H:%M")} - KB Support Basedoc')
        footer_run.font.size = Pt(9)
        footer_run.font.color.rgb = RGBColor(128, 128, 128)
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Sauvegarder dans BytesIO
        docx_file = io.BytesIO()
        doc.save(docx_file)
        docx_file.seek(0)

        return docx_file

    @staticmethod
    def _html_to_docx(html_content, doc):
        """
        Convertit du HTML en contenu DOCX

        Args:
            html_content: Contenu HTML
            doc: Document python-docx
        """
        from docx.shared import Pt, RGBColor

        # Parser le HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Traiter chaque élément
        for element in soup.descendants:
            if element.name == 'h1':
                doc.add_heading(element.get_text(), level=1)
            elif element.name == 'h2':
                doc.add_heading(element.get_text(), level=2)
            elif element.name == 'h3':
                doc.add_heading(element.get_text(), level=3)
            elif element.name == 'p':
                text = element.get_text().strip()
                if text:
                    para = doc.add_paragraph(text)
            elif element.name == 'ul':
                for li in element.find_all('li', recursive=False):
                    doc.add_paragraph(li.get_text().strip(), style='List Bullet')
            elif element.name == 'ol':
                for li in element.find_all('li', recursive=False):
                    doc.add_paragraph(li.get_text().strip(), style='List Number')
            elif element.name == 'pre' or element.name == 'code':
                text = element.get_text()
                if text.strip():
                    para = doc.add_paragraph(text)
                    para_format = para.paragraph_format
                    para_format.left_indent = Pt(20)
                    for run in para.runs:
                        run.font.name = 'Courier New'
                        run.font.size = Pt(9)
            elif element.name == 'strong' or element.name == 'b':
                # Gras (géré dans le contexte du paragraphe parent)
                pass
            elif element.name == 'em' or element.name == 'i':
                # Italique (géré dans le contexte du paragraphe parent)
                pass
