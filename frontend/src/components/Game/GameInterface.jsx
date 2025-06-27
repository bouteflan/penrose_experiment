/**
 * Composant GameInterface - Interface principale du jeu REMOTE
 * Orchestre l'affichage du bureau virtuel, de Tom et des interactions
 */
import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Stores
import { useGameStore } from '../../stores/gameStore';
import { useOSStore } from '../../stores/osStore';
import { useTomStore } from '../../stores/tomStore';

// Composants
import VirtualDesktop from './OS/VirtualDesktop';
import TomConsole from './Tom/TomConsole';
import SystemTray from './OS/SystemTray';
import SecurityAlert from './UI/SecurityAlert';
import CorruptionOverlay from './Effects/CorruptionOverlay';
import DebugPanel from './Debug/DebugPanel';

// Hooks
import { useWebSocketIntegration } from '../../services/websocketService';
import { useAudioService } from '../../services/audioService';

// Styles
import './GameInterface.css';

const GameInterface = ({ sessionId, config, wsService, audioService }) => {
  // Refs
  const containerRef = useRef(null);
  const lastActionTimeRef = useRef(Date.now());
  
  // État local
  const [isFullyLoaded, setIsFullyLoaded] = useState(false);
  const [showSecurityAlert, setShowSecurityAlert] = useState(false);
  const [playerName, setPlayerName] = useState(null);
  
  // Stores
  const gameStore = useGameStore();
  const osStore = useOSStore();
  const tomStore = useTomStore();
  
  // Services
  const audio = useAudioService();

  /**
   * Initialisation des composants quand tous les stores sont prêts
   */
  useEffect(() => {
    const checkInitialization = () => {
      if (gameStore.isInitialized && osStore.isInitialized && tomStore.isInitialized) {
        setIsFullyLoaded(true);
        
        // Activer l'audio après interaction utilisateur
        if (!audio.isInitialized) {
          audio.enable();
        }
        
        // Afficher l'alerte de sécurité après un court délai
        setTimeout(() => {
          setShowSecurityAlert(true);
        }, 2000);
      }
    };
    
    checkInitialization();
  }, [gameStore.isInitialized, osStore.isInitialized, tomStore.isInitialized, audio]);

  /**
   * Integration WebSocket avec les stores
   */
  useEffect(() => {
    if (!wsService) return;

    const cleanupFunctions = [
      // Intégration Game Store
      wsService.addListener('session_status', (data) => {
        if (data.status === 'ended') {
          gameStore.endSession(data.ending_type, data.ending_data);
        }
      }),

      // Intégration OS Store
      wsService.addListener('corruption_update', (data) => {
        osStore.applyCorruption(data.corruption_data);
      }),

      wsService.addListener('os_state_update', (data) => {
        osStore._loadOSState(data.os_state);
      }),

      // Intégration Tom Store
      wsService.addListener('tom_message_generated', (data) => {
        tomStore.handleGeneratedMessage(data.message_data);
      }),

      wsService.addListener('tom_status', (data) => {
        if (data.status === 'disconnected') {
          tomStore.simulateDisconnection();
        }
      })
    ];

    return () => {
      cleanupFunctions.forEach(cleanup => cleanup());
    };
  }, [wsService, gameStore, osStore, tomStore]);

  /**
   * Surveillance des actions utilisateur pour détecter l'inactivité
   */
  useEffect(() => {
    let hesitationTimer = null;

    const resetHesitationTimer = () => {
      if (hesitationTimer) {
        clearTimeout(hesitationTimer);
      }
      
      lastActionTimeRef.current = Date.now();
      
      // Démarrer un nouveau timer d'hésitation
      hesitationTimer = setTimeout(() => {
        const hesitationDuration = Date.now() - lastActionTimeRef.current;
        
        if (hesitationDuration > 5000 && gameStore.isActive) { // Plus de 5 secondes
          gameStore.recordHesitation(hesitationDuration);
          tomStore.recordPlayerHesitation({ duration: hesitationDuration });
        }
      }, 5000);
    };

    const handleUserActivity = () => {
      resetHesitationTimer();
    };

    // Écouter les événements d'activité
    document.addEventListener('mousedown', handleUserActivity);
    document.addEventListener('keydown', handleUserActivity);
    document.addEventListener('mousemove', handleUserActivity);

    // Démarrer le timer initial
    resetHesitationTimer();

    return () => {
      if (hesitationTimer) {
        clearTimeout(hesitationTimer);
      }
      document.removeEventListener('mousedown', handleUserActivity);
      document.removeEventListener('keydown', handleUserActivity);
      document.removeEventListener('mousemove', handleUserActivity);
    };
  }, [gameStore, tomStore]);

  /**
   * Gestionnaire d'action joueur générique
   */
  const handlePlayerAction = (actionData) => {
    const actionId = gameStore.recordAction(actionData);
    
    // Enregistrer dans Tom pour contexte
    tomStore.recordPlayerAction({
      ...actionData,
      action_id: actionId
    });

    // Jouer un son selon le type d'action
    switch (actionData.type) {
      case 'file_delete':
        audio.playAlert();
        break;
      case 'file_click':
        audio.playClick();
        break;
      case 'corruption_detected':
        audio.playCorruption();
        break;
      default:
        audio.playClick();
    }
    
    console.log('🎮 Action joueur:', actionData.type);
  };

  /**
   * Gestionnaire de personnalisation initiale
   */
  const handlePersonalizationComplete = (personalizationData) => {
    const { playerName: name } = personalizationData;
    
    setPlayerName(name);
    tomStore.setPlayerName(name);
    osStore.updatePersonalization({ playerName: name });
    
    setShowSecurityAlert(false);
    
    console.log('👤 Personnalisation terminée:', name);
  };

  /**
   * Gestionnaire pour l'alerte de sécurité
   */
  const handleSecurityAlertClose = () => {
    setShowSecurityAlert(false);
    
    // Si pas de nom défini, démarrer avec un nom par défaut
    if (!playerName) {
      handlePersonalizationComplete({ playerName: 'Joueur' });
    }
  };

  // Rendu de chargement
  if (!isFullyLoaded) {
    return (
      <div className="game-interface-loading">
        <div className="loading-content">
          <div className="loading-spinner">
            <div className="spinner-dots">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
          </div>
          <p>Initialisation du système...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="game-interface" ref={containerRef}>
      {/* Bureau virtuel - Composant principal */}
      <VirtualDesktop
        onPlayerAction={handlePlayerAction}
        playerName={playerName}
      />

      {/* Console Tom - Interface de chat */}
      <TomConsole
        onPlayerAction={handlePlayerAction}
      />

      {/* Barre système */}
      <SystemTray
        onPlayerAction={handlePlayerAction}
      />

      {/* Overlays et effets */}
      <AnimatePresence>
        {/* Alerte de sécurité initiale */}
        {showSecurityAlert && (
          <SecurityAlert
            onPersonalizationComplete={handlePersonalizationComplete}
            onClose={handleSecurityAlertClose}
          />
        )}

        {/* Overlay de corruption */}
        {osStore.corruptionLevel > 0.1 && (
          <CorruptionOverlay
            corruptionLevel={osStore.corruptionLevel}
            effects={osStore.corruptionEffects}
          />
        )}
      </AnimatePresence>

      {/* Panel de debug (développement) */}
      {config.debug && gameStore.showDebug && (
        <DebugPanel
          sessionId={sessionId}
          onPlayerAction={handlePlayerAction}
        />
      )}

      {/* Styles dynamiques pour la corruption */}
      <style jsx>{`
        .game-interface {
          filter: ${osStore.corruptionLevel > 0.3 ? 'hue-rotate(${osStore.corruptionLevel * 180}deg)' : 'none'};
          ${osStore.corruptionLevel > 0.5 ? 'animation: screen-glitch 0.1s infinite;' : ''}
        }
        
        @keyframes screen-glitch {
          0% { transform: translateX(0); }
          25% { transform: translateX(-2px); }
          50% { transform: translateX(2px); }
          75% { transform: translateX(-1px); }
          100% { transform: translateX(0); }
        }
      `}</style>
    </div>
  );
};

export default GameInterface;
