/**
 * Composant principal de l'application REMOTE
 * Gère l'état global et le routing de l'application
 */
import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Génération d'ID unique simple
const generateId = () => `id_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

// Stores Zustand
import { useGameStore } from './stores/gameStore';
import { useOSStore } from './stores/osStore';
import { useTomStore } from './stores/tomStore';

// Services
import { WebSocketService } from './services/websocketService';
import { AudioService } from './services/audioService';

// Composants
import GameInterface from './components/Game/GameInterface';
import LoadingSpinner from './components/UI/LoadingSpinner';
import ErrorBoundary from './components/UI/ErrorBoundary';

// Styles
import './styles/app.css';

// Configuration par défaut
const defaultConfig = {
  wsUrl: 'ws://localhost:8000/ws',
  debug: process.env.NODE_ENV === 'development',
  environment: process.env.NODE_ENV || 'development'
};

const App = ({ config = defaultConfig }) => {
  const [isInitialized, setIsInitialized] = useState(false);
  const [initError, setInitError] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  // Stores Zustand
  const gameStore = useGameStore();
  const osStore = useOSStore();
  const tomStore = useTomStore();

  // Services
  const [wsService, setWsService] = useState(null);
  const [audioService, setAudioService] = useState(null);

  /**
   * Initialise l'application
   */
  const initializeApp = useCallback(async () => {
    try {
      console.log('🚀 Initialisation de REMOTE...');
      
      // Générer un ID de session unique
      const newSessionId = generateId();
      setSessionId(newSessionId);
      
      // Initialiser les services
      const ws = new WebSocketService(config.wsUrl);
      const audio = new AudioService();
      
      setWsService(ws);
      setAudioService(audio);
      
      // Initialiser les stores avec les services
      gameStore.initialize({
        sessionId: newSessionId,
        config,
        wsService: ws,
        audioService: audio
      });
      
      osStore.initialize({
        sessionId: newSessionId,
        wsService: ws
      });
      
      tomStore.initialize({
        sessionId: newSessionId,
        wsService: ws,
        audioService: audio
      });
      
      console.log('✅ Application initialisée');
      setIsInitialized(true);
      
    } catch (error) {
      console.error('❌ Erreur initialisation:', error);
      setInitError(error);
    }
  }, [config, gameStore, osStore, tomStore]);

  /**
   * Nettoyage à la fermeture
   */
  const cleanup = useCallback(() => {
    console.log('🧹 Nettoyage de l\'application...');
    
    if (wsService) {
      wsService.disconnect();
    }
    
    if (audioService) {
      audioService.cleanup();
    }
    
    gameStore.cleanup();
    osStore.cleanup();
    tomStore.cleanup();
  }, [wsService, audioService, gameStore, osStore, tomStore]);

  /**
   * Gestionnaire de fermeture de fenêtre
   */
  const handleBeforeUnload = useCallback((event) => {
    // Avertir si une session de jeu est en cours
    if (gameStore.isActive) {
      const message = 'Une session de jeu est en cours. Êtes-vous sûr de vouloir quitter ?';
      event.returnValue = message;
      return message;
    }
  }, [gameStore.isActive]);

  /**
   * Gestionnaire d'erreur globale
   */
  const handleError = useCallback((error, errorInfo) => {
    console.error('Erreur dans l\'application:', error, errorInfo);
    
    // En production, envoyer à un service de monitoring
    if (config.environment === 'production') {
      // TODO: Intégration monitoring
    }
  }, [config.environment]);

  // Initialisation au montage
  useEffect(() => {
    initializeApp();
    
    // Gestionnaires d'événements
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    // Nettoyage au démontage
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      cleanup();
    };
  }, [initializeApp, handleBeforeUnload, cleanup]);

  // Gestion des raccourcis clavier globaux
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Empêcher les raccourcis de développement pendant le jeu
      if (gameStore.isActive) {
        if (event.key === 'F12' || 
            (event.ctrlKey && event.shiftKey && event.key === 'I')) {
          event.preventDefault();
        }
      }
      
      // Raccourcis de debug (développement seulement)
      if (config.debug && event.ctrlKey && event.shiftKey) {
        switch (event.key) {
          case 'D':
            // Toggle debug overlay
            gameStore.toggleDebug();
            event.preventDefault();
            break;
          case 'R':
            // Reset session
            if (confirm('Réinitialiser la session ?')) {
              gameStore.resetSession();
            }
            event.preventDefault();
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [gameStore, config.debug]);

  // Rendu conditionnel selon l'état d'initialisation
  if (initError) {
    return (
      <div className="app-error">
        <div className="error-content">
          <h1>Erreur d'initialisation</h1>
          <p>Une erreur s'est produite lors du démarrage de l'application.</p>
          <details>
            <summary>Détails techniques</summary>
            <pre>{initError.toString()}</pre>
          </details>
          <button onClick={() => window.location.reload()}>
            Recharger la page
          </button>
        </div>
      </div>
    );
  }

  if (!isInitialized) {
    return (
      <div className="app-loading">
        <LoadingSpinner message="Initialisation de REMOTE..." />
      </div>
    );
  }

  return (
    <ErrorBoundary onError={handleError}>
      <div className="app">
        <AnimatePresence mode="wait">
          <motion.div
            key="game-interface"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="app-content"
          >
            <GameInterface 
              sessionId={sessionId}
              config={config}
              wsService={wsService}
              audioService={audioService}
            />
          </motion.div>
        </AnimatePresence>
      </div>
    </ErrorBoundary>
  );
};

export default App;
