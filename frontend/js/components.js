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
                    <i data-lucide="bar-chart-2"></i>
                    <span>Análisis</span>
                </a>
                <a href="add.html" class="nav-link ${window.location.pathname.endsWith('add.html') ? 'active' : ''}">
                    <i data-lucide="plus-circle"></i>
                    <span>Nuevo Precio</span>
                </a>
                <a href="/catalog" class="nav-link ${window.location.pathname === '/catalog' ? 'active' : ''}">
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
