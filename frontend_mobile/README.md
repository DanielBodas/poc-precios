# PriceTracker Pro - Versión Móvil

Esta carpeta contiene el proyecto de Capacitor para compilar PriceTracker Pro como una aplicación nativa para Android e iOS.

## Requisitos Previos

- [Node.js](https://nodejs.org/) (v18 o superior)
- [Android Studio](https://developer.android.com/studio) (para Android)
- [Xcode](https://developer.apple.com/xcode/) (para iOS, solo en macOS)

## Instalación

1. Entra en esta carpeta:
   ```bash
   cd frontend_mobile
   ```

2. Instala las dependencias:
   ```bash
   npm install
   ```

## Configuración del Backend

Antes de compilar, edita el archivo `www/config.js` y asegúrate de que `window.BACKEND_URL` apunte a tu servidor de producción (ej. Render, Heroku, etc.).

```javascript
window.BACKEND_URL = 'https://tu-backend.onrender.com';
```

## Compilación para Android

1. Añade la plataforma Android (solo la primera vez):
   ```bash
   npx cap add android
   ```

2. Sincroniza los archivos web:
   ```bash
   npm run sync
   ```

3. Abre el proyecto en Android Studio:
   ```bash
   npm run open:android
   ```

4. Desde Android Studio, pulsa "Run" para instalar la app en un emulador o dispositivo físico.

## Compilación para iOS (Solo macOS)

1. Añade la plataforma iOS (solo la primera vez):
   ```bash
   npx cap add ios
   ```

2. Sincroniza los archivos web:
   ```bash
   npm run sync
   ```

3. Abre el proyecto en Xcode:
   ```bash
   npm run open:ios
   ```

4. Desde Xcode, selecciona tu dispositivo y pulsa "Run".

## Notas Adicionales

- Si realizas cambios en el código web (carpeta `www/`), debes ejecutar `npm run sync` para que se reflejen en las plataformas nativas.
- Para usar Google Login en móvil, es posible que necesites configurar [Deep Linking](https://capacitorjs.com/docs/guides/deep-links) y el plugin de [Capacitor Google Auth](https://github.com/CodetrixStudio/CapacitorGoogleAuth).
