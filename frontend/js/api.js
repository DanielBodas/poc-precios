// Prioridad: 1. Variable manual, 2. Endpoint /config.js, 3. Fallback inteligente
const API_URL = window.BACKEND_URL || (window.location.port === "5500" ? "http://127.0.0.1:8000" : "");

const ApiService = {
    async getPrecios() {
        const res = await fetch(`${API_URL}/precios`);
        if (!res.ok) throw new Error("Error al obtener precios");
        return await res.json();
    },

    async createPrecio(datos) {
        const res = await fetch(`${API_URL}/precios`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datos)
        });
        if (!res.ok) throw new Error("Error al crear precio");
        return await res.json();
    },

    async getCatalogProductos() {
        const res = await fetch(`${API_URL}/catalog/productos`);
        return await res.json();
    },

    async getCatalogSupermercados() {
        const res = await fetch(`${API_URL}/catalog/supermercados`);
        return await res.json();
    },

    async getCatalogMarcas() {
        const res = await fetch(`${API_URL}/catalog/marcas`);
        return await res.json();
    },

    async getCatalogCategorias() {
        const res = await fetch(`${API_URL}/catalog/categorias`);
        return await res.json();
    },

    // Create Methods
    async createCategoria(nombre) {
        return fetch(`${API_URL}/catalog/categorias`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre })
        }).then(res => res.json());
    },

    async createMarca(nombre) {
        return fetch(`${API_URL}/catalog/marcas`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre })
        }).then(res => res.json());
    },

    async createSupermercado(nombre) {
        return fetch(`${API_URL}/catalog/supermercados`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre })
        }).then(res => res.json());
    },

    async createProducto(nombre, categoria_id) {
        return fetch(`${API_URL}/catalog/productos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre, categoria_id: parseInt(categoria_id) })
        }).then(res => res.json());
    },

    // Delete Methods
    async deleteCategoria(id) {
        return fetch(`${API_URL}/catalog/categorias/${id}`, { method: "DELETE" });
    },

    async deleteMarca(id) {
        return fetch(`${API_URL}/catalog/marcas/${id}`, { method: "DELETE" });
    },

    async deleteSupermercado(id) {
        return fetch(`${API_URL}/catalog/supermercados/${id}`, { method: "DELETE" });
    },

    async deleteProducto(id) {
        return fetch(`${API_URL}/catalog/productos/${id}`, { method: "DELETE" });
    },

    async deletePrecio(id) {
        return fetch(`${API_URL}/precios/${id}`, { method: "DELETE" });
    }
};

window.ApiService = ApiService;
