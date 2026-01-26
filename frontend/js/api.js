// Detectar si tenemos una URL configurada por el servidor (window.BACKEND_URL)
// O usar el fallback local
const API_URL = window.BACKEND_URL || "http://127.0.0.1:8000";

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
    }
};

window.ApiService = ApiService;
