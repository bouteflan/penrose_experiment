/**
 * Composant TomConsole - Interface de chat avec Tom (Condition B)
 * Simule une interface de support technique avec personnalité humaine
 */
import React, { useEffect, useRef, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Stores
import { useTomStore } from '../../../stores/tomStore';
import { useGameStore } from '../../../stores/gameStore';

// Composants
import TomMessage from './TomMessage';
import TypingIndicator from './TypingIndicator';
import ConnectionStatus from './ConnectionStatus';

// Styles
import './TomConsole.css';

const TomConsole = ({ onPlayerAction }) => {
  // Refs
  const messagesEndRef = useRef(null);
  const consoleRef = useRef(null);
  
  // État local
  const [isMinimized, setIsMinimized] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [scrolledToBottom, setScrolledToBottom] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);
  
  // Stores
  const tomStore = useTomStore();
  const gameStore = useGameStore();
  
  // Données Tom
  const {
    messages,
    isTyping,
    typingProgress,
    isConnected,
    conversationContext,
    tomConfig
  } = tomStore;

  /**
   * Auto-scroll vers le bas quand nouveaux messages
   */
  const scrollToBottom = useCallback((smooth = true) => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: smooth ? 'smooth' : 'instant' 
      });
      setScrolledToBottom(true);
    }
  }, []);

  /**
   * Gérer le scroll manuel
   */
  const handleScroll = useCallback((event) => {
    const { scrollTop, scrollHeight, clientHeight } = event.target;
    const isAtBottom = scrollHeight - scrollTop <= clientHeight + 10;
    setScrolledToBottom(isAtBottom);
    
    // Marquer les messages comme lus si on scroll vers le bas
    if (isAtBottom && unreadCount > 0) {
      setUnreadCount(0);
    }
  }, [unreadCount]);

  /**
   * Nouveau message reçu
   */
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      
      // Auto-scroll si on était déjà en bas
      if (scrolledToBottom) {
        setTimeout(() => scrollToBottom(), 100);
      } else if (lastMessage.sender === 'tom') {
        // Incrémenter les messages non lus
        setUnreadCount(prev => prev + 1);
      }
    }
  }, [messages, scrolledToBottom, scrollToBottom]);

  /**
   * Gestionnaire de minimisation
   */
  const handleToggleMinimize = useCallback(() => {
    setIsMinimized(prev => !prev);
    
    onPlayerAction({
      type: 'tom_console_toggle',
      minimized: !isMinimized,
      is_meta_action: true
    });
    
    // Reset unread count quand on ouvre
    if (isMinimized) {
      setUnreadCount(0);
    }
  }, [isMinimized, onPlayerAction]);

  /**
   * Gestionnaire de fermeture
   */
  const handleClose = useCallback(() => {
    setIsVisible(false);
    
    onPlayerAction({
      type: 'tom_console_close',
      is_meta_action: true
    });
  }, [onPlayerAction]);

  /**
   * Gestionnaire de clic sur message
   */
  const handleMessageClick = useCallback((messageId) => {
    const message = messages.find(m => m.id === messageId);
    
    if (message) {
      onPlayerAction({
        type: 'tom_message_clicked',
        message_id: messageId,
        message_type: message.type,
        is_meta_action: true
      });
    }
  }, [messages, onPlayerAction]);

  /**
   * Calculer le statut de confiance
   */
  const getTrustStatus = useCallback(() => {
    const trustLevel = conversationContext?.trust_level || 0;
    
    if (trustLevel >= 0.8) return { level: 'high', label: 'Confiance élevée', color: '#00b894' };
    if (trustLevel >= 0.6) return { level: 'medium', label: 'Confiance modérée', color: '#fdcb6e' };
    if (trustLevel >= 0.4) return { level: 'low', label: 'Confiance faible', color: '#e17055' };
    return { level: 'critical', label: 'Méfiance', color: '#d63031' };
  }, [conversationContext]);

  /**
   * Classes CSS dynamiques
   */
  const getConsoleClasses = useCallback(() => {
    const classes = ['tom-console'];
    
    if (isMinimized) classes.push('minimized');
    if (!isConnected) classes.push('disconnected');
    if (isTyping) classes.push('typing');
    
    // Classe selon la phase du jeu
    classes.push(`phase-${gameStore.currentPhase}`);
    
    return classes.join(' ');
  }, [isMinimized, isConnected, isTyping, gameStore.currentPhase]);

  // Rendre la console invisible si fermeture
  if (!isVisible) {
    return null;
  }

  const trustStatus = getTrustStatus();

  return (
    <motion.div
      ref={consoleRef}
      className={getConsoleClasses()}
      initial={{ opacity: 0, x: 300 }}
      animate={{ 
        opacity: 1, 
        x: 0,
        height: isMinimized ? 'auto' : '400px'
      }}
      exit={{ opacity: 0, x: 300 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
    >
      {/* Header de la console */}
      <div className="console-header">
        <div className="header-left">
          <div className="tom-avatar">
            <span className="avatar-icon">👨‍💻</span>
            <ConnectionStatus isConnected={isConnected} />
          </div>
          
          <div className="tom-info">
            <div className="tom-name">
              {tomConfig.name} ({tomConfig.role})
            </div>
            <div className="tom-status">
              {isTyping ? 'Tape...' : isConnected ? 'En ligne' : 'Déconnecté'}
            </div>
          </div>
        </div>
        
        <div className="header-right">
          {/* Indicateur de confiance */}
          <div 
            className="trust-indicator"
            style={{ color: trustStatus.color }}
            title={trustStatus.label}
          >
            <span className="trust-icon">🤝</span>
            <span className="trust-level">
              {Math.round((conversationContext?.trust_level || 0) * 100)}%
            </span>
          </div>
          
          {/* Boutons de contrôle */}
          <div className="console-controls">
            <button 
              className="control-button minimize"
              onClick={handleToggleMinimize}
              title={isMinimized ? 'Agrandir' : 'Réduire'}
            >
              {isMinimized ? '🔼' : '🔽'}
            </button>
            
            <button 
              className="control-button close"
              onClick={handleClose}
              title="Fermer"
            >
              ✕
            </button>
          </div>
        </div>
      </div>

      {/* Contenu de la console */}
      <AnimatePresence>
        {!isMinimized && (
          <motion.div
            className="console-content"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {/* Zone des messages */}
            <div 
              className="messages-container"
              onScroll={handleScroll}
            >
              <div className="messages-list">
                <AnimatePresence>
                  {messages.map((message, index) => (
                    <TomMessage
                      key={message.id}
                      message={message}
                      isLatest={index === messages.length - 1}
                      onClick={() => handleMessageClick(message.id)}
                      gamePhase={gameStore.currentPhase}
                    />
                  ))}
                </AnimatePresence>
                
                {/* Indicateur de frappe */}
                {isTyping && (
                  <TypingIndicator
                    typingProgress={typingProgress}
                    tomName={tomConfig.name}
                  />
                )}
                
                {/* Élément pour auto-scroll */}
                <div ref={messagesEndRef} />
              </div>
              
              {/* Bouton scroll to bottom */}
              {!scrolledToBottom && (
                <motion.button
                  className="scroll-to-bottom"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  onClick={() => scrollToBottom()}
                >
                  ↓ {unreadCount > 0 && <span className="unread-badge">{unreadCount}</span>}
                </motion.button>
              )}
            </div>
            
            {/* Zone d'information */}
            <div className="console-footer">
              <div className="connection-info">
                <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`} />
                <span className="status-text">
                  {isConnected ? 'Connexion sécurisée' : 'Connexion interrompue'}
                </span>
              </div>
              
              {gameStore.showDebug && (
                <div className="debug-info">
                  Messages: {messages.length} | Trust: {trustStatus.level}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Badge de notification (quand minimisé) */}
      {isMinimized && unreadCount > 0 && (
        <motion.div
          className="notification-badge"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: 'spring', stiffness: 500 }}
        >
          {unreadCount}
        </motion.div>
      )}
    </motion.div>
  );
};

export default TomConsole;
