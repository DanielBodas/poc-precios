function initNavbar() {
    const navHTML = `
    <nav class="main-nav">
        <div class="nav-container">
            <a href="index.html" class="nav-logo">
                <i data-lucide="trending-up"></i>
                <span>PriceTracker Pro</span>
            </a>
            <div class="nav-links">
                <a href="index.html" class="nav-link ${window.location.pathname.endsWith('index.html') || window.location.pathname === '/' ? 'active' : ''}">
                    <i data-lucide="layout-dashboard"></i>
                    <span>Inicio</span>
                </a>
                <a href="add.html" class="nav-link ${window.location.pathname.endsWith('add.html') ? 'active' : ''}">
                    <i data-lucide="plus-circle"></i>
                    <span>Añadir</span>
                </a>
                <a href="compare.html" class="nav-link ${window.location.pathname.endsWith('compare.html') ? 'active' : ''}">
                    <i data-lucide="bar-chart-3"></i>
                    <span>Comparativa</span>
                </a>
                <a href="catalog.html" class="nav-link ${window.location.pathname.endsWith('catalog.html') ? 'active' : ''}">
                    <i data-lucide="settings-2"></i>
                    <span>Gestión</span>
                </a>
            </div>
        </div>
    </nav>
    `;

    document.body.insertAdjacentHTML('afterbegin', navHTML);
    if (window.lucide) {
        window.lucide.createIcons();
    }
}

document.addEventListener("DOMContentLoaded", initNavbar);
