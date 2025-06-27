/**
 * Point d'entrée principal de l'application REMOTE
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';

// Configuration globale de l'application
const config = {
  version: '1.0.0',
  environment: import.meta.env.MODE || 'development',
  debug: import.meta.env.DEV || false,
  // En développement, utiliser le proxy Vite pour WebSocket
  apiUrl: import.meta.env.DEV ? '/api' : 'http://localhost:8000/api',
  wsUrl: import.meta.env.DEV ? 'ws://localhost:5173' : 'ws://localhost:8000',
};

// Merge avec window.REMOTE_CONFIG si existant
if (window.REMOTE_CONFIG) {
  Object.assign(config, window.REMOTE_CONFIG);
}

// Log de démarrage
console.log(`🎮 REMOTE v${config.version} (${config.environment})`);
console.log(`📡 WebSocket URL: ${config.wsUrl}`);
console.log(`🌐 API URL: ${config.apiUrl}`);

// Gestion des erreurs globales
window.addEventListener('error', (event) => {
  console.error('❌ Erreur globale:', event.error);
  
  // En production, envoyer les erreurs à un service de monitoring
  if (config.environment === 'production') {
    // Intégration future avec Sentry ou autre
  }
});

// Gestion des erreurs de promesses non capturées
window.addEventListener('unhandledrejection', (event) => {
  console.error('❌ Promesse rejetée non gérée:', event.reason);
  event.preventDefault(); // Empêche l'affichage de l'erreur dans la console
});

// Fonction de démarrage de l'application
function startApp() {
  const container = document.getElementById('root');
  
  if (!container) {
    console.error('❌ Élément #root non trouvé dans le DOM');
    return;
  }

  // Création de l'application React
  const root = ReactDOM.createRoot(container);

  // Render de l'application avec gestion d'erreur
  try {
    root.render(
      <React.StrictMode>
        <App config={config} />
      </React.StrictMode>
    );
    
    console.log('✅ Application REMOTE initialisée');
    
  } catch (error) {
    console.error('❌ Erreur démarrage application:', error);
    
    // Affichage d'erreur de fallback
    container.innerHTML = `
      <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        background: #1a1b23;
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      ">
        <div style="text-align: center; max-width: 500px; padding: 2rem;">
          <h1 style="color: #e17055; margin-bottom: 1rem;">Erreur de Chargement</h1>
          <p style="color: #a0a0a0; margin-bottom: 2rem;">
            Une erreur s'est produite lors du démarrage de l'application.
          </p>
          <details style="text-align: left; margin-bottom: 2rem;">
            <summary style="cursor: pointer; font-weight: bold; color: #74b9ff;">Détails techniques</summary>
            <pre style="
              background: #2c2d35;
              padding: 1rem;
              border-radius: 4px;
              overflow: auto;
              margin-top: 1rem;
              font-size: 0.875rem;
              color: #fdcb6e;
            ">${error.toString()}</pre>
          </details>
          <button onclick="window.location.reload()" style="
            background: #6c5ce7;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
          ">
            Recharger la page
          </button>
        </div>
      </div>
    `;
  }
}

// Démarrer l'application
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', startApp);
} else {
  startApp();
}

// Cacher l'écran de chargement une fois React monté
setTimeout(() => {
  if (window.hideLoadingScreen) {
    window.hideLoadingScreen();
  }
}, 100);
