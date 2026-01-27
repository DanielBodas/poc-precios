// Prioridad: 1. Variable de entorno (via /config.js), 2. Desarrollo local, 3. Rutas relativas
const API_URL = window.BACKEND_URL || ((window.location.port === "5500" || window.location.port === "5501") ? "http://127.0.0.1:8000" : "");

const ApiService = {
    async getPrecios() {
        const res = await fetch(`${API_URL}/precios`);
        return await res.json();
    },

    async getPrecio(id) {
        const res = await fetch(`${API_URL}/precios/${id}`);
        return await res.json();
    },

    async getPrecioHistorial(prodId) {
        const res = await fetch(`${API_URL}/precios/producto/${prodId}`);
        return await res.json();
    },

    async createPrecio(datos) {
        const res = await fetch(`${API_URL}/precios`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datos)
        });
        return await res.json();
    },

    async updatePrecio(id, datos) {
        const res = await fetch(`${API_URL}/precios/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datos)
        });
        return await res.json();
    },

    async deletePrecio(id) {
        return fetch(`${API_URL}/precios/${id}`, { method: "DELETE" });
    },

    // Catálogo
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

    async getCatalogUnidades() {
        const res = await fetch(`${API_URL}/catalog/unidades`);
        return await res.json();
    },

    // Create & Delete Helpers
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

    async createUnidad(nombre) {
        return fetch(`${API_URL}/catalog/unidades`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nombre })
        }).then(res => res.json());
    },

    async createProducto(nombre, categoria_ids, unidad_ids, marca_ids) {
        const response = await fetch(`${API_URL}/catalog/productos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                nombre,
                categoria_ids: (categoria_ids || []).map(id => parseInt(id)),
                unidad_ids: (unidad_ids || []).map(id => parseInt(id)),
                marca_ids: (marca_ids || []).map(id => parseInt(id))
            })
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`Error ${response.status}: ${error}`);
        }

        return await response.json();
    },

    async deleteCategoria(id) { return fetch(`${API_URL}/catalog/categorias/${id}`, { method: "DELETE" }); },
    async deleteMarca(id) { return fetch(`${API_URL}/catalog/marcas/${id}`, { method: "DELETE" }); },
    async deleteSupermercado(id) { return fetch(`${API_URL}/catalog/supermercados/${id}`, { method: "DELETE" }); },
    async deleteUnidad(id) { return fetch(`${API_URL}/catalog/unidades/${id}`, { method: "DELETE" }); },
    async deleteProducto(id) { return fetch(`${API_URL}/catalog/productos/${id}`, { method: "DELETE" }); },

    // Relaciones específicas
    async linkCategoria(producto_id, categoria_id) {
        return fetch(`${API_URL}/catalog/productos/${producto_id}/categorias/${categoria_id}`, {
            method: "POST"
        }).then(res => res.json());
    },

    async unlinkCategoria(producto_id, categoria_id) {
        return fetch(`${API_URL}/catalog/productos/${producto_id}/categorias/${categoria_id}`, {
            method: "DELETE"
        }).then(res => res.json());
    },

    async linkUnidad(producto_id, unidad_id) {
        return fetch(`${API_URL}/catalog/productos/${producto_id}/unidades/${unidad_id}`, {
            method: "POST"
        }).then(res => res.json());
    },

    async unlinkUnidad(producto_id, unidad_id) {
        return fetch(`${API_URL}/catalog/productos/${producto_id}/unidades/${unidad_id}`, {
            method: "DELETE"
        }).then(res => res.json());
    },

    async linkMarca(producto_id, marca_id) {
        return fetch(`${API_URL}/catalog/productos/${producto_id}/marcas/${marca_id}`, {
            method: "POST"
        }).then(res => res.json());
    },

    async unlinkMarca(producto_id, marca_id) {
        return fetch(`${API_URL}/catalog/productos/${producto_id}/marcas/${marca_id}`, {
            method: "DELETE"
        }).then(res => res.json());
    }
};

window.API_URL = API_URL;
window.ApiService = ApiService;
