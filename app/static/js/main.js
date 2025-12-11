/**
 * KB Support Basedoc - JavaScript principal
 * Gère les interactions de base de l'application
 */

document.addEventListener('DOMContentLoaded', function() {
    initSearchAutocomplete();
    initFlashMessages();
    initTooltips();
});

/**
 * Auto-complétion de recherche
 */
function initSearchAutocomplete() {
    const searchInput = document.getElementById('global-search');
    const suggestionsContainer = document.getElementById('search-suggestions');

    if (!searchInput || !suggestionsContainer) return;

    let searchTimeout;

    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);

        const query = this.value.trim();

        if (query.length < 3) {
            suggestionsContainer.classList.remove('active');
            return;
        }

        searchTimeout = setTimeout(() => {
            fetchSearchSuggestions(query);
        }, 300);
    });

    // Fermer les suggestions si on clique ailleurs
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.classList.remove('active');
        }
    });
}

/**
 * Récupérer les suggestions de recherche
 */
async function fetchSearchSuggestions(query) {
    const suggestionsContainer = document.getElementById('search-suggestions');

    try {
        const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
        const suggestions = await response.json();

        if (suggestions.length > 0) {
            displaySearchSuggestions(suggestions);
            suggestionsContainer.classList.add('active');
        } else {
            suggestionsContainer.classList.remove('active');
        }
    } catch (error) {
        console.error('Erreur chargement suggestions:', error);
    }
}

/**
 * Afficher les suggestions de recherche
 */
function displaySearchSuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('search-suggestions');

    const html = suggestions.map(suggestion => `
        <a href="${suggestion.url}" class="search-suggestion-item">
            <div style="font-weight: 600;">${highlightQuery(suggestion.title)}</div>
            <div style="font-size: 0.75rem; color: #9ca3af;">${suggestion.category}</div>
        </a>
    `).join('');

    suggestionsContainer.innerHTML = html;
}

/**
 * Surligner la requête dans les suggestions
 */
function highlightQuery(text) {
    const searchInput = document.getElementById('global-search');
    const query = searchInput.value.trim();

    if (!query) return text;

    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<span style="color: #06b6d4;">$1</span>');
}

/**
 * Gestion des flash messages
 */
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash');

    flashMessages.forEach(flash => {
        // Auto-fermeture après 5 secondes
        setTimeout(() => {
            flash.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => flash.remove(), 300);
        }, 5000);
    });
}

// Animation slideOut pour flash messages
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

/**
 * Tooltips (simple)
 */
function initTooltips() {
    const elements = document.querySelectorAll('[data-tooltip]');

    elements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.dataset.tooltip;

            document.body.appendChild(tooltip);

            const rect = this.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
            tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
        });

        element.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) tooltip.remove();
        });
    });
}

/**
 * Confirmer une action
 */
function confirmAction(message) {
    return confirm(message);
}

/**
 * Copier dans le presse-papier
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copié dans le presse-papier', 'success');
    } catch (error) {
        console.error('Erreur copie:', error);
        showNotification('Erreur lors de la copie', 'error');
    }
}

/**
 * Afficher une notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">[×]</button>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 5000);
}

/**
 * Formater une date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('fr-FR', options);
}

/**
 * Débounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Export des fonctions utilitaires pour être accessibles globalement
window.confirmAction = confirmAction;
window.copyToClipboard = copyToClipboard;
window.showNotification = showNotification;
window.formatDate = formatDate;
window.debounce = debounce;
window.throttle = throttle;
window.escapeHtml = escapeHtml;
