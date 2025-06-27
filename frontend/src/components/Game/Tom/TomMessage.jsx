/**
 * Composant TomMessage - Affiche un message individuel de Tom
 * Adapte le style selon le type de message et la phase du jeu
 */
import React, { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import './TomMessage.css';

const TomMessage = ({ 
  message, 
  isLatest, 
  onClick, 
  gamePhase 
}) => {
  // Refs
  const messageRef = useRef(null);
  
  // État local
  const [isVisible, setIsVisible] = useState(false);
  
  // Observer pour l'animation d'apparition
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );
    
    if (messageRef.current) {
      observer.observe(messageRef.current);
    }
    
    return () => observer.disconnect();
  }, []);

  /**
   * Obtient l'icône selon le type de message
   */
  const getMessageIcon = () => {
    const iconMap = {
      'welcome': '👋',
      'instruction': '📋',
      'instruction_with_trust': '🤝',
      'concern': '😟',
      'encouragement': '💪',
      'urgency': '⚡',
      'technical': '⚙️',
      'reassurance': '😌',
      'warning': '⚠️',
      'system_error': '❌',
      'fallback': '🤔'
    };
    
    return iconMap[message.type] || '💬';
  };

  /**
   * Obtient les classes CSS selon le type et le contexte
   */
  const getMessageClasses = () => {
    const classes = ['tom-message'];
    
    // Type de message
    classes.push(`message-${message.type}`);
    
    // Phase du jeu
    classes.push(`phase-${gamePhase}`);
    
    // Message le plus récent
    if (isLatest) classes.push('latest');
    
    // Niveau émotionnel
    const emotional = message.emotional_context;
    if (emotional) {
      if (emotional.urgency > 0.7) classes.push('urgent');
      if (emotional.empathy > 0.7) classes.push('empathetic');
      if (emotional.trust_building > 0.7) classes.push('trust-building');
      if (emotional.concern > 0.7) classes.push('concerned');
    }
    
    return classes.join(' ');
  };

  /**
   * Formatte le timestamp
   */
  const formatTimestamp = () => {
    const date = new Date(message.timestamp);
    return date.toLocaleTimeString('fr-FR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  /**
   * Analyse le contenu pour détecter les instructions
   */
  const parseMessageContent = () => {
    const content = message.content;
    
    // Détecter les instructions (mots-clés en gras)
    const instructionKeywords = [
      'Clique', 'Glisse', 'Déplace', 'Supprime', 'Renomme', 
      'Ouvre', 'Ferme', 'Sélectionne', 'Copie', 'Colle'
    ];
    
    let parsedContent = content;
    
    instructionKeywords.forEach(keyword => {
      const regex = new RegExp(`\\b(${keyword}[^.!?]*[.!?])`, 'gi');
      parsedContent = parsedContent.replace(regex, '<strong class="instruction">$1</strong>');
    });
    
    return { __html: parsedContent };
  };

  /**
   * Style de corruption selon la phase
   */
  const getCorruptionStyle = () => {
    if (gamePhase === 'rupture' && Math.random() > 0.7) {
      return {
        filter: `hue-rotate(${Math.random() * 60 - 30}deg)`,
        animation: `text-glitch ${0.5 + Math.random()}s infinite`
      };
    }
    return {};
  };

  return (
    <motion.div
      ref={messageRef}
      className={getMessageClasses()}
      style={getCorruptionStyle()}
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ 
        opacity: isVisible ? 1 : 0, 
        y: isVisible ? 0 : 20, 
        scale: isVisible ? 1 : 0.95 
      }}
      transition={{ 
        duration: 0.3, 
        ease: 'easeOut',
        delay: isLatest ? 0.1 : 0
      }}
      whileHover={{ scale: 1.02 }}
      onClick={() => onClick && onClick(message.id)}
    >
      {/* Header du message */}
      <div className="message-header">
        <div className="message-avatar">
          <span className="avatar-icon">{getMessageIcon()}</span>
        </div>
        
        <div className="message-meta">
          <span className="sender-name">Tom</span>
          <span className="message-time">{formatTimestamp()}</span>
        </div>
        
        {/* Indicateurs contextuels */}
        <div className="message-indicators">
          {message.emotional_context?.urgency > 0.7 && (
            <span className="indicator urgent" title="Urgent">⚡</span>
          )}
          {message.emotional_context?.trust_building > 0.7 && (
            <span className="indicator trust" title="Construction de confiance">🤝</span>
          )}
          {message.emotional_context?.empathy > 0.7 && (
            <span className="indicator empathy" title="Empathique">💙</span>
          )}
        </div>
      </div>

      {/* Contenu du message */}
      <div className="message-content">
        <div 
          className="message-text"
          dangerouslySetInnerHTML={parseMessageContent()}
        />
        
        {/* Digressions (si présentes) */}
        {message.digressions && message.digressions.length > 0 && (
          <div className="message-digressions">
            {message.digressions.map((digression, index) => (
              <div key={index} className="digression">
                <em>{digression}</em>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer du message */}
      <div className="message-footer">
        {/* Type de message pour debug */}
        {process.env.NODE_ENV === 'development' && (
          <span className="message-type-debug">{message.type}</span>
        )}
        
        {/* Indicateur de contexte émotionnel */}
        {message.emotional_context && (
          <div className="emotional-context">
            {Object.entries(message.emotional_context)
              .filter(([_, value]) => value > 0.5)
              .map(([emotion, intensity]) => (
                <span 
                  key={emotion} 
                  className={`emotion-tag ${emotion}`}
                  style={{ opacity: intensity }}
                >
                  {emotion}
                </span>
              ))
            }
          </div>
        )}
      </div>

      {/* Effet de highlight pour nouveau message */}
      {isLatest && (
        <motion.div
          className="new-message-highlight"
          initial={{ opacity: 0.5 }}
          animate={{ opacity: 0 }}
          transition={{ duration: 2 }}
        />
      )}
    </motion.div>
  );
};

export default TomMessage;
