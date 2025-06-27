/**
 * Composant DebugPanel - Panel de debug pour le développement
 * Affiche les informations de debug et permet de tester les fonctionnalités
 */
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useGameStore } from '../../../stores/gameStore';
import { useOSStore } from '../../../stores/osStore';
import { useTomStore } from '../../../stores/tomStore';
import './DebugPanel.css';

const DebugPanel = ({ 
  sessionId, 
  onPlayerAction 
}) => {
  // État local
  const [activeTab, setActiveTab] = useState('game');
  const [isMinimized, setIsMinimized] = useState(false);
  
  // Stores
  const gameStore = useGameStore();
  const osStore = useOSStore();
  const tomStore = useTomStore();

  /**
   * Actions de debug
   */
  const debugActions = {
    // Actions de jeu
    resetSession: () => gameStore.resetSession(),
    endSession: (type) => gameStore.endSession(type),
    changePhase: (phase) => gameStore.updatePhase(phase),
    
    // Actions OS
    simulateCorruption: () => osStore.simulateCorruption(),
    addNotification: () => osStore.addNotification({
      type: 'warning',
      title: 'Test',
      message: 'Notification de test'
    }),
    openTestWindow: () => osStore.openWindow({
      type: 'system_info',
      title: 'Fenêtre de test',
      position: { x: 200, y: 150 }
    }),
    
    // Actions Tom
    sendTestMessage: () => tomStore.sendTestMessage(),
    updateTrust: (delta) => tomStore.updateTrustLevel(delta),
    setTyping: (typing) => tomStore.isTyping = typing
  };

  /**
   * Rendu de l'onglet Game
   */
  const renderGameTab = () => (
    <div className="debug-tab-content">
      <div className="debug-section">
        <h4>État de la session</h4>
        <div className="debug-info">
          <div><strong>ID:</strong> {sessionId}</div>
          <div><strong>État:</strong> {gameStore.isActive ? 'Active' : 'Inactive'}</div>
          <div><strong>Phase:</strong> {gameStore.currentPhase}</div>
          <div><strong>Temps:</strong> {Math.round(gameStore.timeElapsed)}s</div>
          <div><strong>Actions:</strong> {gameStore.totalActions}</div>
          <div><strong>Obéissance:</strong> {(gameStore.getObedienceRate() * 100).toFixed(1)}%</div>
        </div>
      </div>

      <div className="debug-section">
        <h4>Actions de jeu</h4>
        <div className="debug-buttons">
          <button onClick={() => debugActions.resetSession()}>
            Reset Session
          </button>
          <button onClick={() => debugActions.endSession('debug_end')}>
            End Session
          </button>
        </div>
        
        <div className="debug-buttons">
          <button onClick={() => debugActions.changePhase('adhesion')}>
            Phase Adhésion
          </button>
          <button onClick={() => debugActions.changePhase('dissonance')}>
            Phase Dissonance
          </button>
          <button onClick={() => debugActions.changePhase('rupture')}>
            Phase Rupture
          </button>
        </div>
      </div>

      <div className="debug-section">
        <h4>Métriques temps réel</h4>
        <div className="debug-metrics">
          <div className="metric">
            <span className="metric-label">Hésitations:</span>
            <span className="metric-value">{gameStore.hesitationEvents}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Méta-actions:</span>
            <span className="metric-value">{gameStore.metaActions}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Corruption incidents:</span>
            <span className="metric-value">{gameStore.corruptionIncidents}</span>
          </div>
        </div>
      </div>
    </div>
  );

  /**
   * Rendu de l'onglet OS
   */
  const renderOSTab = () => (
    <div className="debug-tab-content">
      <div className="debug-section">
        <h4>État du système</h4>
        <div className="debug-info">
          <div><strong>Corruption:</strong> {(osStore.corruptionLevel * 100).toFixed(1)}%</div>
          <div><strong>Performance:</strong> {(osStore.systemPerformance * 100).toFixed(0)}%</div>
          <div><strong>Réseau:</strong> {osStore.networkStatus}</div>
          <div><strong>Fichiers:</strong> {osStore.files?.length || 0}</div>
          <div><strong>Fenêtres:</strong> {osStore.windows?.length || 0}</div>
        </div>
      </div>

      <div className="debug-section">
        <h4>Actions OS</h4>
        <div className="debug-buttons">
          <button onClick={() => debugActions.simulateCorruption()}>
            Simuler Corruption
          </button>
          <button onClick={() => debugActions.addNotification()}>
            Test Notification
          </button>
          <button onClick={() => debugActions.openTestWindow()}>
            Ouvrir Fenêtre
          </button>
        </div>
      </div>

      <div className="debug-section">
        <h4>Corruption actuelle</h4>
        <div className="corruption-display">
          <div className="corruption-bar">
            <div 
              className="corruption-fill"
              style={{ width: `${osStore.corruptionLevel * 100}%` }}
            />
          </div>
          <div className="corruption-effects">
            {osStore.corruptionEffects?.slice(-3).map((effect, index) => (
              <div key={index} className="effect-item">
                {effect.type} ({effect.intensity?.toFixed(2)})
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  /**
   * Rendu de l'onglet Tom
   */
  const renderTomTab = () => (
    <div className="debug-tab-content">
      <div className="debug-section">
        <h4>État de Tom</h4>
        <div className="debug-info">
          <div><strong>Messages:</strong> {tomStore.messages?.length || 0}</div>
          <div><strong>Typing:</strong> {tomStore.isTyping ? 'Oui' : 'Non'}</div>
          <div><strong>Connecté:</strong> {tomStore.isConnected ? 'Oui' : 'Non'}</div>
          <div><strong>Confiance:</strong> {((tomStore.conversationContext?.trust_level || 0) * 100).toFixed(1)}%</div>
          <div><strong>Stress:</strong> {tomStore.conversationContext?.stress_level || 'normal'}</div>
        </div>
      </div>

      <div className="debug-section">
        <h4>Actions Tom</h4>
        <div className="debug-buttons">
          <button onClick={() => debugActions.sendTestMessage()}>
            Message Test
          </button>
          <button onClick={() => debugActions.updateTrust(0.1)}>
            Augmenter Confiance
          </button>
          <button onClick={() => debugActions.updateTrust(-0.1)}>
            Diminuer Confiance
          </button>
        </div>
      </div>

      <div className="debug-section">
        <h4>Métriques Tom</h4>
        <div className="debug-metrics">
          <div className="metric">
            <span className="metric-label">Messages totaux:</span>
            <span className="metric-value">{tomStore.metrics?.total_messages || 0}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Auto-révélations:</span>
            <span className="metric-value">{tomStore.metrics?.self_disclosures_made || 0}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Marqueurs émotionnels:</span>
            <span className="metric-value">{tomStore.metrics?.emotional_markers_used || 0}</span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <motion.div
      className={`debug-panel ${isMinimized ? 'minimized' : ''}`}
      initial={{ opacity: 0, x: 300 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="debug-header">
        <h3>🔧 Debug Panel</h3>
        <div className="debug-controls">
          <button 
            className="debug-control"
            onClick={() => setIsMinimized(!isMinimized)}
          >
            {isMinimized ? '🔼' : '🔽'}
          </button>
          <button 
            className="debug-control"
            onClick={() => gameStore.toggleDebug()}
          >
            ✕
          </button>
        </div>
      </div>

      {/* Contenu */}
      {!isMinimized && (
        <div className="debug-content">
          {/* Onglets */}
          <div className="debug-tabs">
            <button 
              className={`debug-tab ${activeTab === 'game' ? 'active' : ''}`}
              onClick={() => setActiveTab('game')}
            >
              Game
            </button>
            <button 
              className={`debug-tab ${activeTab === 'os' ? 'active' : ''}`}
              onClick={() => setActiveTab('os')}
            >
              OS
            </button>
            <button 
              className={`debug-tab ${activeTab === 'tom' ? 'active' : ''}`}
              onClick={() => setActiveTab('tom')}
            >
              Tom
            </button>
          </div>

          {/* Contenu des onglets */}
          <div className="debug-tabs-content">
            {activeTab === 'game' && renderGameTab()}
            {activeTab === 'os' && renderOSTab()}
            {activeTab === 'tom' && renderTomTab()}
          </div>
        </div>
      )}

      {/* Footer avec infos rapides */}
      <div className="debug-footer">
        <span>FPS: --</span>
        <span>Mem: --MB</span>
        <span>WS: {osStore.wsService ? '🟢' : '🔴'}</span>
      </div>
    </motion.div>
  );
};

export default DebugPanel;
