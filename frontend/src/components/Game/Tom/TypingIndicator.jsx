/**
 * Composant TypingIndicator - Affiche l'animation de frappe de Tom
 * Simule une frappe humaine avec texte progressif (Condition B)
 */
import React from 'react';
import { motion } from 'framer-motion';
import './TypingIndicator.css';

const TypingIndicator = ({ 
  typingProgress, 
  tomName = 'Tom',
  showFullAnimation = true 
}) => {

  /**
   * Composant de points animés
   */
  const TypingDots = () => (
    <div className="typing-dots">
      <motion.div
        className="dot"
        animate={{ 
          scale: [1, 1.5, 1],
          opacity: [0.5, 1, 0.5]
        }}
        transition={{ 
          duration: 1.2, 
          repeat: Infinity,
          delay: 0
        }}
      />
      <motion.div
        className="dot"
        animate={{ 
          scale: [1, 1.5, 1],
          opacity: [0.5, 1, 0.5]
        }}
        transition={{ 
          duration: 1.2, 
          repeat: Infinity,
          delay: 0.2
        }}
      />
      <motion.div
        className="dot"
        animate={{ 
          scale: [1, 1.5, 1],
          opacity: [0.5, 1, 0.5]
        }}
        transition={{ 
          duration: 1.2, 
          repeat: Infinity,
          delay: 0.4
        }}
      />
    </div>
  );

  /**
   * Curseur clignotant
   */
  const BlinkingCursor = () => (
    <motion.span
      className="typing-cursor"
      animate={{ opacity: [0, 1, 0] }}
      transition={{ 
        duration: 0.8, 
        repeat: Infinity,
        ease: 'easeInOut'
      }}
    >
      |
    </motion.span>
  );

  return (
    <motion.div
      className="typing-indicator"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
    >
      {/* Header avec avatar et nom */}
      <div className="typing-header">
        <div className="typing-avatar">
          <span className="avatar-icon">👨‍💻</span>
          {/* Indicateur d'activité */}
          <motion.div
            className="activity-pulse"
            animate={{ 
              scale: [1, 1.3, 1],
              opacity: [0.7, 1, 0.7]
            }}
            transition={{ 
              duration: 1, 
              repeat: Infinity 
            }}
          />
        </div>
        
        <div className="typing-meta">
          <span className="typing-name">{tomName}</span>
          <span className="typing-status">tape...</span>
        </div>
      </div>

      {/* Zone de contenu */}
      <div className="typing-content">
        {showFullAnimation && typingProgress ? (
          // Mode texte progressif (Condition B)
          <div className="typing-text-preview">
            <span className="typed-text">{typingProgress}</span>
            <BlinkingCursor />
          </div>
        ) : (
          // Mode points animés simple
          <div className="typing-simple">
            <span className="typing-label">{tomName} tape</span>
            <TypingDots />
          </div>
        )}
      </div>

      {/* Barre de progression simulée */}
      {showFullAnimation && typingProgress && (
        <div className="typing-progress">
          <motion.div
            className="progress-bar"
            initial={{ width: 0 }}
            animate={{ width: '100%' }}
            transition={{ 
              duration: 3, 
              ease: 'easeOut',
              repeat: Infinity
            }}
          />
        </div>
      )}

      {/* Effet de fond pulsant */}
      <motion.div
        className="typing-background-pulse"
        animate={{ 
          background: [
            'rgba(108, 92, 231, 0.05)',
            'rgba(108, 92, 231, 0.1)',
            'rgba(108, 92, 231, 0.05)'
          ]
        }}
        transition={{ 
          duration: 2, 
          repeat: Infinity,
          ease: 'easeInOut'
        }}
      />
    </motion.div>
  );
};

export default TypingIndicator;
