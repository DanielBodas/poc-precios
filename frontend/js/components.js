(function () {
    // 1. Check URL for token (OAuth callback from Backend)
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    if (tokenFromUrl) {
        localStorage.setItem('auth_token', tokenFromUrl);
        // Clean URL so token doesn't persist in browser history
        const newUrl = window.location.pathname;
        window.history.replaceState({}, document.title, newUrl);
    }

    // 2. Auth Guard Logic
    const isLoginPage = window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/');
    const token = localStorage.getItem('auth_token');

    // If we are NOT on login page and have NO token, redirect to login
    if (!isLoginPage && !token) {
        window.location.href = 'index.html';
    }
    // If we ARE on login page and HAVE token, redirect to home
    if (isLoginPage && token) {
        window.location.href = 'home.html';
    }
})();

function initLayout() {
    const path = window.location.pathname;

    // Determine current page status for active link
    const isLogin = path.includes('index.html') || path === '/' || path.endsWith('/');
    if (isLogin) return;

    const isCatalog = path.includes('catalog');
    const isCompare = path.includes('compare');
    const isAdd = path.includes('add');
    const isHome = path.includes('home');

    const isDashboard = isHome || (!isCatalog && !isCompare && !isAdd);

    const existingNav = document.querySelector('nav.main-nav');
    if (existingNav) existingNav.remove();

    const sidebarCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
    if (sidebarCollapsed) {
        document.body.classList.add('sidebar-collapsed');
    }

    // 1. Render Top Navbar
    const navHTML = `
    <nav class="main-nav">
        <div class="nav-container">
            <div style="display:flex; align-items:center; gap:1rem;">
                <button class="menu-toggle" onclick="toggleSidebar()" style="background:transparent; padding:0.5rem; color:var(--text-muted); border:1px solid rgba(0,0,0,0.05); width:auto; border-radius:8px; cursor: pointer;">
                    <i data-lucide="menu" style="width:20px;"></i>
                </button>
                <a href="home.html" class="nav-logo">
                    <i data-lucide="scan-line" class="color-primary"></i>
                    <span>PriceTracker Pro</span>
                </a>
            </div>
            
            <div class="nav-links">
                <a href="add.html" class="nav-link mobile-only" style="background:var(--primary); color:white; padding:0.4rem 0.8rem;">
                    <i data-lucide="plus" style="width:18px;"></i>
                    <span style="font-size:0.9rem;">Nuevo</span>
                </a>
            </div>
        </div>
    </nav>
    `;
    document.body.insertAdjacentHTML('afterbegin', navHTML);

    // 2. Wrap content 
    const layoutContainer = document.querySelector('.layout-container');
    if (layoutContainer) {
        const sidebarHTML = `
        <aside class="sidebar-left">
            <a href="home.html" class="menu-item ${isDashboard ? 'active' : ''}" title="Inicio">
                <i data-lucide="home"></i>
                <span class="menu-text">Inicio</span>
            </a>
            <a href="catalog.html" class="menu-item ${isCatalog ? 'active' : ''}" title="Catálogo Maestro">
                <i data-lucide="database"></i>
                <span class="menu-text">Catálogo Maestro</span>
            </a>
            <a href="compare.html" class="menu-item ${isCompare ? 'active' : ''}" title="Comparador">
                <i data-lucide="bar-chart-2"></i>
                <span class="menu-text">Comparador</span>
            </a>
             <div style="height: 1px; background: rgba(0,0,0,0.05); margin: 1rem 0;"></div>
            <a href="add.html" class="menu-item ${isAdd ? 'active' : ''}" title="Registrar Precio">
                <i data-lucide="plus-circle"></i>
                <span class="menu-text">Registrar Precio</span>
            </a>
            <div style="height: 1px; background: rgba(0,0,0,0.05); margin: 1rem 0;"></div>
            <a href="#" class="menu-item" title="Guardados">
                <i data-lucide="bookmark"></i>
                <span class="menu-text">Guardados</span>
            </a>
             <div style="margin-top:auto;"></div>
               <a href="index.html" onclick="localStorage.removeItem('auth_token');" class="menu-item" style="color:var(--danger);" title="Cerrar Sesión">
                <i data-lucide="log-out"></i>
                <span class="menu-text">Cerrar Sesión</span>
            </a>
        </aside>
        `;
        layoutContainer.insertAdjacentHTML('afterbegin', sidebarHTML);
    }

    if (window.lucide) {
        window.lucide.createIcons();
    }
}

function toggleSidebar() {
    document.body.classList.toggle('sidebar-collapsed');
    const isCollapsed = document.body.classList.contains('sidebar-collapsed');
    localStorage.setItem('sidebar-collapsed', isCollapsed);
}

document.addEventListener("DOMContentLoaded", () => {
    initLayout();
});
