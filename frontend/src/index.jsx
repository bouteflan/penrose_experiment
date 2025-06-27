/**
 * Point d'entrée principal de l'application REMOTE
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';

// Configuration globale de l'application
const config = window.REMOTE_CONFIG || {
  version: '1.0.0',
  environment: 'development',
  apiUrl: 'http://localhost:8000',
  wsUrl: 'ws://localhost:8000',
  debug: true
};

// Log de démarrage
console.log(`🎮 REMOTE v${config.version} (${config.environment})`);

// Gestion des erreurs globales
window.addEventListener('error', (event) => {
  console.error('Erreur globale:', event.error);
  
  // En production, envoyer les erreurs à un service de monitoring
  if (config.environment === 'production') {
    // Intégration future avec Sentry ou autre
  }
});

// Gestion des erreurs de promesses non capturées
window.addEventListener('unhandledrejection', (event) => {
  console.error('Promesse rejetée non gérée:', event.reason);
  event.preventDefault(); // Empêche l'affichage de l'erreur dans la console
});

// Création de l'application React
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render de l'application avec gestion d'erreur
root.render(
  <React.StrictMode>
    <App config={config} />
  </React.StrictMode>
);

// Cacher l'écran de chargement une fois React monté
setTimeout(() => {
  if (window.hideLoadingScreen) {
    window.hideLoadingScreen();
  }
}, 100);
