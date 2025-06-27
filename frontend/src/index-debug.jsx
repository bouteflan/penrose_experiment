/**
 * Version de diagnostic de index.jsx
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import AppDebug from './App-debug';
import './styles/index.css';

console.log('🚀 index-debug.jsx : Démarrage du diagnostic REMOTE');

// Configuration de diagnostic
const debugConfig = {
  version: '1.0.0-debug',
  environment: 'development',
  apiUrl: 'http://localhost:8000',
  wsUrl: 'ws://localhost:8000',
  debug: true
};

console.log('📋 Configuration de diagnostic:', debugConfig);

// Vérifications préliminaires
console.log('🔍 Vérifications préliminaires:');
console.log('- React:', typeof React);
console.log('- ReactDOM:', typeof ReactDOM);
console.log('- document.getElementById("root"):', document.getElementById('root'));

// Gestion des erreurs globales pour le diagnostic
window.addEventListener('error', (event) => {
  console.error('🚨 Erreur globale capturée:', {
    message: event.message,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    error: event.error
  });
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('🚨 Promesse rejetée non gérée:', event.reason);
});

// Test de création de l'application React
try {
  console.log('⚛️ Création de la racine React...');
  const root = ReactDOM.createRoot(document.getElementById('root'));
  
  console.log('📦 Rendu de l\'application de diagnostic...');
  root.render(
    <React.StrictMode>
      <AppDebug config={debugConfig} />
    </React.StrictMode>
  );
  
  console.log('✅ Application de diagnostic démarrée avec succès');
  
  // Cacher l'écran de chargement
  setTimeout(() => {
    if (window.hideLoadingScreen) {
      console.log('🎭 Masquage de l\'écran de chargement...');
      window.hideLoadingScreen();
    }
  }, 500);
  
} catch (error) {
  console.error('❌ Erreur fatale lors du démarrage:', error);
  
  // Affichage d'erreur de fallback
  document.getElementById('root').innerHTML = `
    <div style="
      display: flex;
      align-items: center;
      justify-content: center;
      height: 100vh;
      background: #1a1b23;
      color: white;
      font-family: system-ui;
      text-align: center;
      padding: 20px;
    ">
      <div>
        <h1 style="color: #e17055;">❌ Erreur fatale</h1>
        <p>Impossible de démarrer l'application de diagnostic.</p>
        <details style="margin: 20px 0; text-align: left;">
          <summary style="cursor: pointer;">Détails de l'erreur</summary>
          <pre style="
            background: #2c2d35;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
            overflow: auto;
            max-width: 500px;
          ">${error.toString()}\n\n${error.stack || 'Pas de stack trace'}</pre>
        </details>
        <div style="margin-top: 20px;">
          <p><strong>Solutions suggérées :</strong></p>
          <ul style="text-align: left; max-width: 400px; margin: 10px auto;">
            <li>Vérifiez que le serveur de développement est démarré</li>
            <li>Exécutez <code>npm install</code> pour installer les dépendances</li>
            <li>Redémarrez le serveur avec <code>npm run dev</code></li>
            <li>Vérifiez la console du navigateur (F12)</li>
          </ul>
        </div>
        <button onclick="window.location.reload()" style="
          margin-top: 20px;
          padding: 10px 20px;
          background: #6c5ce7;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
        ">
          Recharger la page
        </button>
      </div>
    </div>
  `;
}
