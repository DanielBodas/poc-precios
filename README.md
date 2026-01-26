# PriceTracker Pro 🚀

Una aplicación profesional y moderna para realizar el seguimiento de precios en diferentes supermercados.

## Características

- ✨ **Interfaz Premium**: Diseño moderno con efectos de glassmorphism y animaciones fluidas.
- 🌓 **Modo Adaptativo**: Preparado para temas claros y oscuros.
- ⚡ **Backend Robusto**: Desarrollado con **FastAPI** y **SQLAlchemy**.
- 📱 **Responsive**: Totalmente optimizado para dispositivos móviles y escritorio.
- 🔍 **Validación de Datos**: Esquemas Pydantic para asegurar la integridad de la información.

## Tecnologías Utilizadas

- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), JavaScript (ES6+).
- **Backend**: Python 3.x, FastAPI, SQLAlchemy, SQLite.
- **Iconografía**: Lucide Icons.
- **Tipografía**: Outfit (via Google Fonts).

## Instalación y Uso

### Requisitos
- Python 3.8+
- Los paquetes listados en `backend/requirements.txt`

### Ejecución del Backend
```bash
uvicorn backend.main:app --reload
```

### Ejecución del Frontend
Simplemente abre `frontend/index.html` en tu navegador o utiliza un servidor local (como Live Server).

## Estructura del Proyecto

```text
mercado_web/
├── backend/
│   ├── database.py    # Configuración de SQLAlchemy
│   ├── main.py        # Endpoints y lógica de la API
│   ├── models.py      # Modelos de base de datos
│   └── schemas.py     # Esquemas de Pydantic
├── frontend/
│   ├── index.html     # Estructura de la aplicación
│   ├── index.css      # Sistema de diseño y estilos
│   └── script.js      # Lógica de cliente y comunicación con API
└── precios.db         # Base de datos SQLite
```
