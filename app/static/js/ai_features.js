/**
 * Fonctionnalités IA côté client pour KB Support Basedoc
 * Gère les appels aux API IA (tags, reformulation, mise en page)
 */

class AIFeatures {
    constructor() {
        this.apiBaseUrl = '/api/ai';
        this.loadingOverlay = null;
        this.modals = {};

        this.init();
    }

    /**
     * Initialisation
     */
    init() {
        this.createLoadingOverlay();
        this.attachEventListeners();
    }

    /**
     * Créer l'overlay de loading
     */
    createLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'ai-loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p id="loading-text">Traitement en cours...</p>
            </div>
        `;
        document.body.appendChild(overlay);
        this.loadingOverlay = overlay;
    }

    /**
     * Attacher les event listeners
     */
    attachEventListeners() {
        // Bouton génération tags
        const btnGenerateTags = document.getElementById('btn-generate-tags');
        if (btnGenerateTags) {
            btnGenerateTags.addEventListener('click', () => this.generateTags());
        }

        // Bouton reformulation
        const btnReformulate = document.getElementById('btn-reformulate');
        if (btnReformulate) {
            btnReformulate.addEventListener('click', () => this.reformulateContent());
        }

        // Bouton mise en page
        const btnLayout = document.getElementById('btn-layout');
        if (btnLayout) {
            btnLayout.addEventListener('click', () => this.layoutContent());
        }
    }

    /**
     * Afficher le loading
     */
    showLoading(message = 'Traitement en cours...') {
        document.getElementById('loading-text').textContent = message;
        this.loadingOverlay.classList.add('active');
    }

    /**
     * Masquer le loading
     */
    hideLoading() {
        this.loadingOverlay.classList.remove('active');
    }

    /**
     * Afficher une notification
     */
    showNotification(message, type = 'info') {
        // Créer notification toast
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">[×]</button>
        `;

        // Ajouter au body
        document.body.appendChild(notification);

        // Auto-suppression après 5 secondes
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    /**
     * Générer des tags automatiquement
     */
    async generateTags() {
        const titleInput = document.getElementById('procedure-title');
        const contentEditor = this.getEditorContent();

        if (!titleInput || !contentEditor) {
            this.showNotification('Éléments de formulaire non trouvés', 'error');
            return;
        }

        const title = titleInput.value.trim();
        const content = contentEditor.trim();

        if (!title) {
            this.showNotification('Le titre est requis', 'error');
            return;
        }

        if (!content || content.length < 50) {
            this.showNotification('Le contenu doit contenir au moins 50 caractères', 'error');
            return;
        }

        this.showLoading('Génération des tags IA...');

        try {
            const response = await fetch(`${this.apiBaseUrl}/generate-tags`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    content: content,
                    min_tags: 4,
                    max_tags: 8
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erreur lors de la génération des tags');
            }

            if (data.success) {
                this.displayTagsSuggestions(data.tags);
                this.showNotification(`${data.count} tags générés avec succès`, 'success');
            } else {
                throw new Error(data.error || 'Erreur inconnue');
            }

        } catch (error) {
            console.error('Erreur génération tags:', error);
            this.showNotification(
                error.message || 'Erreur lors de la génération des tags',
                'error'
            );
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Afficher les suggestions de tags
     */
    displayTagsSuggestions(tags) {
        const modal = this.createTagsSuggestionsModal(tags);
        document.body.appendChild(modal);
        this.modals.tagsSuggestions = modal;
    }

    /**
     * Créer le modal de suggestions de tags
     */
    createTagsSuggestionsModal(tags) {
        const modal = document.createElement('div');
        modal.className = 'modal tags-suggestions-modal active';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>🤖 Tags suggérés par l'IA</h2>
                    <button class="btn-close" onclick="aiFeatures.closeTagsSuggestionsModal()">[×]</button>
                </div>
                <div class="modal-body">
                    <p>Sélectionnez les tags à ajouter :</p>
                    <div class="tags-suggestions">
                        ${tags.map((tag, index) => `
                            <label class="tag-suggestion">
                                <input type="checkbox"
                                       id="tag-${index}"
                                       value="${tag}"
                                       checked>
                                <span class="tag-label">[${tag}]</span>
                            </label>
                        `).join('')}
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="aiFeatures.closeTagsSuggestionsModal()">
                        [ANNULER]
                    </button>
                    <button class="btn-primary" onclick="aiFeatures.acceptSelectedTags()">
                        [✓ AJOUTER LES TAGS SÉLECTIONNÉS]
                    </button>
                </div>
            </div>
        `;
        return modal;
    }

    /**
     * Fermer le modal de suggestions de tags
     */
    closeTagsSuggestionsModal() {
        if (this.modals.tagsSuggestions) {
            this.modals.tagsSuggestions.remove();
            delete this.modals.tagsSuggestions;
        }
    }

    /**
     * Accepter les tags sélectionnés
     */
    acceptSelectedTags() {
        const checkboxes = document.querySelectorAll('.tags-suggestions input[type="checkbox"]:checked');
        const selectedTags = Array.from(checkboxes).map(cb => cb.value);

        // Ajouter les tags au formulaire
        this.addTagsToForm(selectedTags);

        this.showNotification(`${selectedTags.length} tags ajoutés`, 'success');
        this.closeTagsSuggestionsModal();
    }

    /**
     * Ajouter des tags au formulaire
     */
    addTagsToForm(tags) {
        const tagsContainer = document.getElementById('tags-container');
        if (!tagsContainer) return;

        tags.forEach(tag => {
            // Vérifier si le tag n'existe pas déjà
            const existingTags = Array.from(tagsContainer.querySelectorAll('.tag-item'))
                .map(item => item.dataset.tag);

            if (!existingTags.includes(tag)) {
                const tagElement = document.createElement('div');
                tagElement.className = 'tag-item';
                tagElement.dataset.tag = tag;
                tagElement.innerHTML = `
                    <span class="tag-name">[${tag}]</span>
                    <button type="button" class="tag-remove" onclick="this.parentElement.remove()">[×]</button>
                    <input type="hidden" name="tags[]" value="${tag}">
                `;
                tagsContainer.appendChild(tagElement);
            }
        });
    }

    /**
     * Reformuler le contenu
     */
    async reformulateContent() {
        const titleInput = document.getElementById('procedure-title');
        const contentEditor = this.getEditorContent();

        if (!titleInput || !contentEditor) {
            this.showNotification('Éléments de formulaire non trouvés', 'error');
            return;
        }

        const title = titleInput.value.trim();
        const content = contentEditor.trim();

        if (!content || content.length < 50) {
            this.showNotification('Le contenu doit contenir au moins 50 caractères', 'error');
            return;
        }

        this.showLoading('Reformulation du contenu avec l\'IA...');

        try {
            const response = await fetch(`${this.apiBaseUrl}/reformulate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    content: content
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erreur lors de la reformulation');
            }

            if (data.success) {
                this.displayReformulationModal(content, data.reformulated_content);
            } else {
                throw new Error(data.error || 'Erreur inconnue');
            }

        } catch (error) {
            console.error('Erreur reformulation:', error);
            this.showNotification(
                error.message || 'Erreur lors de la reformulation',
                'error'
            );
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Afficher le modal de reformulation
     */
    displayReformulationModal(original, reformulated) {
        const modal = this.createReformulationModal(original, reformulated);
        document.body.appendChild(modal);
        this.modals.reformulation = modal;
    }

    /**
     * Créer le modal de reformulation
     */
    createReformulationModal(original, reformulated) {
        const modal = document.createElement('div');
        modal.className = 'modal reformulation-modal active';
        modal.innerHTML = `
            <div class="modal-content modal-large">
                <div class="modal-header">
                    <h2>✨ Reformulation IA</h2>
                    <button class="btn-close" onclick="aiFeatures.closeReformulationModal()">[×]</button>
                </div>
                <div class="modal-body">
                    <div class="comparison">
                        <div class="original-content">
                            <h3>Original</h3>
                            <div class="content-box">
                                <pre>${this.escapeHtml(original)}</pre>
                            </div>
                        </div>
                        <div class="arrow">→</div>
                        <div class="reformulated-content">
                            <h3>Reformulé</h3>
                            <div class="content-box" id="reformulated-preview">
                                ${this.markdownToHtml(reformulated)}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="aiFeatures.closeReformulationModal()">
                        [ANNULER]
                    </button>
                    <button class="btn-primary" onclick="aiFeatures.applyReformulation('${this.escapeForAttribute(reformulated)}')">
                        [✓ APPLIQUER]
                    </button>
                </div>
            </div>
        `;
        return modal;
    }

    /**
     * Fermer le modal de reformulation
     */
    closeReformulationModal() {
        if (this.modals.reformulation) {
            this.modals.reformulation.remove();
            delete this.modals.reformulation;
        }
    }

    /**
     * Appliquer la reformulation
     */
    applyReformulation(reformulatedContent) {
        // Décoder le contenu
        const content = this.decodeAttribute(reformulatedContent);

        this.setEditorContent(content);
        this.showNotification('Contenu reformulé appliqué', 'success');
        this.closeReformulationModal();
    }

    /**
     * Réorganiser la mise en page
     */
    async layoutContent() {
        const titleInput = document.getElementById('procedure-title');
        const contentEditor = this.getEditorContent();

        if (!titleInput || !contentEditor) {
            this.showNotification('Éléments de formulaire non trouvés', 'error');
            return;
        }

        const title = titleInput.value.trim();
        const content = contentEditor.trim();

        if (!content || content.length < 50) {
            this.showNotification('Le contenu doit contenir au moins 50 caractères', 'error');
            return;
        }

        // Récupérer les options
        const options = {
            use_emojis: document.getElementById('opt-emoji')?.checked ?? true,
            structure_sections: document.getElementById('opt-sections')?.checked ?? true,
            number_steps: document.getElementById('opt-steps')?.checked ?? true,
            add_troubleshooting: document.getElementById('opt-troubleshoot')?.checked ?? true
        };

        this.showLoading('Réorganisation de la mise en page...');

        try {
            const response = await fetch(`${this.apiBaseUrl}/layout`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    content: content,
                    options: options
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erreur lors de la réorganisation');
            }

            if (data.success) {
                this.displayLayoutModal(content, data.layout_content);
            } else {
                throw new Error(data.error || 'Erreur inconnue');
            }

        } catch (error) {
            console.error('Erreur mise en page:', error);
            this.showNotification(
                error.message || 'Erreur lors de la réorganisation',
                'error'
            );
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Afficher le modal de mise en page
     */
    displayLayoutModal(original, layout) {
        const modal = this.createLayoutModal(original, layout);
        document.body.appendChild(modal);
        this.modals.layout = modal;
    }

    /**
     * Créer le modal de mise en page
     */
    createLayoutModal(original, layout) {
        const modal = document.createElement('div');
        modal.className = 'modal layout-modal active';
        modal.innerHTML = `
            <div class="modal-content modal-large">
                <div class="modal-header">
                    <h2>📐 Mise en page IA</h2>
                    <button class="btn-close" onclick="aiFeatures.closeLayoutModal()">[×]</button>
                </div>
                <div class="modal-body">
                    <div class="comparison">
                        <div class="before-layout">
                            <h3>Avant</h3>
                            <div class="content-box">
                                <pre>${this.escapeHtml(original)}</pre>
                            </div>
                        </div>
                        <div class="arrow">→</div>
                        <div class="after-layout">
                            <h3>Après</h3>
                            <div class="content-box" id="layout-preview">
                                ${this.markdownToHtml(layout)}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="aiFeatures.closeLayoutModal()">
                        [ANNULER]
                    </button>
                    <button class="btn-primary" onclick="aiFeatures.applyLayout('${this.escapeForAttribute(layout)}')">
                        [✓ APPLIQUER MISE EN PAGE]
                    </button>
                </div>
            </div>
        `;
        return modal;
    }

    /**
     * Fermer le modal de mise en page
     */
    closeLayoutModal() {
        if (this.modals.layout) {
            this.modals.layout.remove();
            delete this.modals.layout;
        }
    }

    /**
     * Appliquer la mise en page
     */
    applyLayout(layoutContent) {
        // Décoder le contenu
        const content = this.decodeAttribute(layoutContent);

        this.setEditorContent(content);
        this.showNotification('Mise en page appliquée', 'success');
        this.closeLayoutModal();
    }

    /**
     * Récupérer le contenu de l'éditeur
     * Compatible avec TinyMCE, Quill, ou textarea simple
     */
    getEditorContent() {
        // TinyMCE
        if (typeof tinymce !== 'undefined') {
            const editor = tinymce.get('procedure-content');
            if (editor) return editor.getContent();
        }

        // Quill
        if (typeof Quill !== 'undefined') {
            const editor = document.querySelector('.ql-editor');
            if (editor) return editor.innerHTML;
        }

        // Textarea simple
        const textarea = document.getElementById('procedure-content');
        if (textarea) return textarea.value;

        return '';
    }

    /**
     * Définir le contenu de l'éditeur
     */
    setEditorContent(content) {
        // TinyMCE
        if (typeof tinymce !== 'undefined') {
            const editor = tinymce.get('procedure-content');
            if (editor) {
                editor.setContent(content);
                return;
            }
        }

        // Quill
        if (typeof Quill !== 'undefined') {
            const editor = document.querySelector('.ql-editor');
            if (editor) {
                editor.innerHTML = content;
                return;
            }
        }

        // Textarea simple
        const textarea = document.getElementById('procedure-content');
        if (textarea) {
            textarea.value = content;
        }
    }

    /**
     * Convertir markdown en HTML (simple)
     */
    markdownToHtml(markdown) {
        // Basique, à améliorer avec une vraie lib markdown si besoin
        let html = markdown;

        // Headers
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Italic
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Code blocks
        html = html.replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>');

        // Inline code
        html = html.replace(/`(.*?)`/g, '<code>$1</code>');

        // Line breaks
        html = html.replace(/\n/g, '<br>');

        return html;
    }

    /**
     * Échapper HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Échapper pour attribut HTML
     */
    escapeForAttribute(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/'/g, '&#39;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    /**
     * Décoder attribut HTML
     */
    decodeAttribute(text) {
        const div = document.createElement('div');
        div.innerHTML = text;
        return div.textContent;
    }
}

// Instance globale
let aiFeatures;

// Initialiser au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    aiFeatures = new AIFeatures();
});
