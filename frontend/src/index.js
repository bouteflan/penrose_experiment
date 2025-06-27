/**
 * Point d'entrée principal de l'application REMOTE
 * Configure React et lance l'application
 */
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';

// Import des styles globaux
import './styles/app.css';

// Configuration pour le développement
if (import.meta.env.DEV) {
  console.log('🎮 REMOTE - Mode Développement');
  console.log('Environment:', import.meta.env.MODE);
}

// Fonction principale de démarrage
function startApp() {
  const container = document.getElementById('root');
  
  if (!container) {
    console.error('❌ Élément #root non trouvé dans le DOM');
    return;
  }
  
  // Créer la racine React 18
  const root = createRoot(container);
  
  // Configuration par défaut pour l'application
  const appConfig = {
    wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
    apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    debug: import.meta.env.DEV,
    environment: import.meta.env.MODE || 'development'
  };
  
  // Rendu de l'application
  try {
    root.render(
      <React.StrictMode>
        <App config={appConfig} />
      </React.StrictMode>
    );
    
    console.log('✅ Application REMOTE démarrée');
    
    // Marquer l'application comme chargée
    setTimeout(() => {
      document.body.classList.add('app-loaded');
    }, 500);
    
  } catch (error) {
    console.error('❌ Erreur démarrage application:', error);
    
    // Affichage d'erreur de fallback
    container.innerHTML = `
      <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100vh;
        background: #f8f9fa;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      ">
        <div style="text-align: center; max-width: 500px; padding: 2rem;">
          <h1 style="color: #dc3545; margin-bottom: 1rem;">Erreur de Chargement</h1>
          <p style="color: #6c757d; margin-bottom: 2rem;">
            Une erreur s'est produite lors du démarrage de l'application.
          </p>
          <details style="text-align: left; margin-bottom: 2rem;">
            <summary style="cursor: pointer; font-weight: bold;">Détails techniques</summary>
            <pre style="
              background: #f8f9fa;
              padding: 1rem;
              border-radius: 4px;
              overflow: auto;
              margin-top: 1rem;
              font-size: 0.875rem;
            ">${error.toString()}</pre>
          </details>
          <button onclick="window.location.reload()" style="
            background: #007bff;
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

// Attendre que le DOM soit prêt
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', startApp);
} else {
  // DOM déjà prêt
  startApp();
}

// Gestion des erreurs globales non gérées
window.addEventListener('error', (event) => {
  console.error('❌ Erreur globale:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('❌ Promesse rejetée non gérée:', event.reason);
});
