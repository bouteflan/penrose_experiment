/**
 * Version de diagnostic de App.jsx pour identifier les problèmes
 */
import React, { useState, useEffect, useCallback } from 'react';

// Test des imports
console.log('🚀 App-debug.jsx : Chargement...');

let gameStoreImported = false;
let osStoreImported = false;
let tomStoreImported = false;
let servicesImported = false;
let componentsImported = false;

// Test import des stores
try {
  const { useGameStore } = await import('./stores/gameStore');
  gameStoreImported = true;
  console.log('✅ gameStore importé');
} catch (error) {
  console.error('❌ Erreur import gameStore:', error);
}

try {
  const { useOSStore } = await import('./stores/osStore');
  osStoreImported = true;
  console.log('✅ osStore importé');
} catch (error) {
  console.error('❌ Erreur import osStore:', error);
}

try {
  const { useTomStore } = await import('./stores/tomStore');
  tomStoreImported = true;
  console.log('✅ tomStore importé');
} catch (error) {
  console.error('❌ Erreur import tomStore:', error);
}

// Test import des services
try {
  const { WebSocketService } = await import('./services/websocketService');
  const { AudioService } = await import('./services/audioService');
  servicesImported = true;
  console.log('✅ Services importés');
} catch (error) {
  console.error('❌ Erreur import services:', error);
}

// Test import des composants
try {
  const GameInterface = await import('./components/Game/GameInterface');
  const LoadingSpinner = await import('./components/UI/LoadingSpinner');
  const ErrorBoundary = await import('./components/UI/ErrorBoundary');
  componentsImported = true;
  console.log('✅ Composants importés');
} catch (error) {
  console.error('❌ Erreur import composants:', error);
}

const AppDebug = ({ config = {} }) => {
  const [initStatus, setInitStatus] = useState('loading');
  const [errors, setErrors] = useState([]);
  
  useEffect(() => {
    console.log('🔍 App-debug : useEffect initial');
    
    const checkDependencies = async () => {
      const status = {
        stores: gameStoreImported && osStoreImported && tomStoreImported,
        services: servicesImported,
        components: componentsImported
      };
      
      console.log('📊 Status des dépendances:', status);
      
      if (status.stores && status.services && status.components) {
        setInitStatus('ready');
        console.log('✅ Toutes les dépendances sont OK');
      } else {
        setInitStatus('error');
        const errorList = [];
        if (!status.stores) errorList.push('Stores Zustand');
        if (!status.services) errorList.push('Services WebSocket/Audio');
        if (!status.components) errorList.push('Composants React');
        setErrors(errorList);
        console.error('❌ Dépendances manquantes:', errorList);
      }
    };
    
    checkDependencies();
  }, []);
  
  // Rendu de diagnostic
  if (initStatus === 'loading') {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100vh',
        flexDirection: 'column',
        fontFamily: 'system-ui',
        backgroundColor: '#1a1b23',
        color: 'white'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h1>🔍 Diagnostic REMOTE</h1>
          <p>Vérification des dépendances...</p>
          <div style={{ 
            width: '40px', 
            height: '40px', 
            border: '3px solid #333',
            borderTop: '3px solid #6c5ce7',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '20px auto'
          }} />
        </div>
        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    );
  }
  
  if (initStatus === 'error') {
    return (
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        height: '100vh',
        flexDirection: 'column',
        fontFamily: 'system-ui',
        backgroundColor: '#1a1b23',
        color: 'white',
        padding: '20px'
      }}>
        <div style={{ textAlign: 'center', maxWidth: '600px' }}>
          <h1>❌ Erreur de chargement</h1>
          <p>Problèmes détectés avec les dépendances:</p>
          <ul style={{ textAlign: 'left', color: '#e17055' }}>
            {errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
          
          <div style={{ marginTop: '30px', textAlign: 'left' }}>
            <h3>Solutions suggérées:</h3>
            <ol>
              <li>Vérifiez que le serveur de développement est démarré : <code>npm run dev</code></li>
              <li>Installez les dépendances : <code>npm install</code></li>
              <li>Vérifiez la console du navigateur (F12) pour plus de détails</li>
              <li>Redémarrez le serveur de développement</li>
            </ol>
          </div>
          
          <button 
            onClick={() => window.location.reload()}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              backgroundColor: '#6c5ce7',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            Recharger la page
          </button>
        </div>
      </div>
    );
  }
  
  // Si tout est OK, afficher un message de succès
  return (
    <div style={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      height: '100vh',
      flexDirection: 'column',
      fontFamily: 'system-ui',
      backgroundColor: '#1a1b23',
      color: 'white'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1>✅ Diagnostic réussi</h1>
        <p>Toutes les dépendances sont chargées correctement.</p>
        <p>Le problème vient probablement de l'initialisation des stores ou des services.</p>
        
        <div style={{ marginTop: '30px', textAlign: 'left', maxWidth: '500px' }}>
          <h3>Prochaines étapes :</h3>
          <ol>
            <li>Remplacer App-debug.jsx par App.jsx normal</li>
            <li>Ajouter des console.log dans les stores initialize()</li>
            <li>Vérifier la connexion WebSocket</li>
            <li>Tester l'initialisation des services</li>
          </ol>
        </div>
        
        <button 
          onClick={() => {
            console.log('🔄 Diagnostic terminé - Passez à App.jsx normal');
            // Ici on pourrait rediriger vers l'app normale
          }}
          style={{
            marginTop: '20px',
            padding: '10px 20px',
            backgroundColor: '#00b894',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Diagnostic terminé
        </button>
      </div>
    </div>
  );
};

export default AppDebug;
