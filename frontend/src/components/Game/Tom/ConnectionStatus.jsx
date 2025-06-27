/**
 * Composant ConnectionStatus - Affiche l'état de connexion avec Tom
 * Indicateur visuel de la qualité de la connexion
 */
import React from 'react';
import { motion } from 'framer-motion';
import './ConnectionStatus.css';

const ConnectionStatus = ({ 
  isConnected, 
  quality = 'good', // 'excellent', 'good', 'poor', 'disconnected'
  latency = 0,
  showDetails = false 
}) => {

  /**
   * Obtient la couleur selon l'état de connexion
   */
  const getStatusColor = () => {
    if (!isConnected) return '#e17055';
    
    switch (quality) {
      case 'excellent': return '#00b894';
      case 'good': return '#6c5ce7';
      case 'poor': return '#fdcb6e';
      default: return '#636e72';
    }
  };

  /**
   * Obtient l'icône selon l'état
   */
  const getStatusIcon = () => {
    if (!isConnected) return '❌';
    
    switch (quality) {
      case 'excellent': return '🟢';
      case 'good': return '🔵';
      case 'poor': return '🟡';
      default: return '⚪';
    }
  };

  /**
   * Obtient le texte de statut
   */
  const getStatusText = () => {
    if (!isConnected) return 'Déconnecté';
    
    switch (quality) {
      case 'excellent': return 'Excellente';
      case 'good': return 'Bonne';
      case 'poor': return 'Faible';
      default: return 'Inconnue';
    }
  };

  /**
   * Barres de signal animées
   */
  const SignalBars = () => {
    const bars = isConnected ? 
      (quality === 'excellent' ? 4 : quality === 'good' ? 3 : quality === 'poor' ? 2 : 1) : 0;

    return (
      <div className="signal-bars">
        {[1, 2, 3, 4].map(bar => (
          <motion.div
            key={bar}
            className={`signal-bar ${bar <= bars ? 'active' : 'inactive'}`}
            initial={{ height: 0 }}
            animate={{ 
              height: bar <= bars ? `${bar * 25}%` : '10%',
              opacity: bar <= bars ? 1 : 0.3
            }}
            transition={{ 
              duration: 0.3, 
              delay: bar * 0.1 
            }}
          />
        ))}
      </div>
    );
  };

  /**
   * Point de statut pulsant
   */
  const StatusDot = () => (
    <motion.div
      className="status-dot"
      style={{ backgroundColor: getStatusColor() }}
      animate={isConnected ? {
        scale: [1, 1.2, 1],
        opacity: [0.8, 1, 0.8]
      } : {
        scale: 1,
        opacity: 0.6
      }}
      transition={isConnected ? {
        duration: 2,
        repeat: Infinity,
        ease: 'easeInOut'
      } : {}}
    />
  );

  return (
    <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'} quality-${quality}`}>
      {showDetails ? (
        // Mode détaillé avec barres de signal
        <div className="status-detailed">
          <div className="status-header">
            <StatusDot />
            <span className="status-label">
              {getStatusText()}
            </span>
          </div>
          
          <div className="signal-container">
            <SignalBars />
          </div>
          
          {latency > 0 && (
            <div className="latency-info">
              <span className="latency-value">{latency}ms</span>
            </div>
          )}
        </div>
      ) : (
        // Mode compact avec icône simple
        <div className="status-compact">
          <StatusDot />
          {showDetails && (
            <span className="status-text">{getStatusText()}</span>
          )}
        </div>
      )}

      {/* Tooltip au survol */}
      <div className="status-tooltip">
        <div className="tooltip-content">
          <div className="tooltip-header">
            <span className="tooltip-icon">{getStatusIcon()}</span>
            <span className="tooltip-title">Connexion {getStatusText()}</span>
          </div>
          
          {isConnected && (
            <div className="tooltip-details">
              <div>Qualité: {getStatusText()}</div>
              {latency > 0 && <div>Latence: {latency}ms</div>}
              <div>Statut: En ligne</div>
            </div>
          )}
          
          {!isConnected && (
            <div className="tooltip-details">
              <div>Connexion interrompue</div>
              <div>Tentative de reconnexion...</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConnectionStatus;
