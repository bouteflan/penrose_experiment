/**
 * Composant SecurityAlert - Alerte de sécurité initiale
 * Première interaction avec le joueur, déclenche l'arrivée de Tom
 */
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './SecurityAlert.css';

const SecurityAlert = ({ 
  onPersonalizationComplete, 
  onClose 
}) => {
  // État local
  const [step, setStep] = useState('alert'); // 'alert', 'personalization', 'confirmed'
  const [playerName, setPlayerName] = useState('');

  /**
   * Gestionnaire d'acceptation de l'alerte
   */
  const handleAcceptAlert = () => {
    setStep('personalization');
  };

  /**
   * Gestionnaire de soumission du nom
   */
  const handleSubmitName = () => {
    if (playerName.trim()) {
      setStep('confirmed');
      
      setTimeout(() => {
        onPersonalizationComplete({
          playerName: playerName.trim()
        });
      }, 1500);
    }
  };

  /**
   * Gestionnaire de fermeture directe
   */
  const handleDirectClose = () => {
    onClose();
  };

  /**
   * Rendu de l'alerte de sécurité
   */
  const renderSecurityAlert = () => (
    <motion.div
      className="security-alert-content"
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="alert-header">
        <div className="alert-icon">🛡️</div>
        <h2>ALERTE DE SÉCURITÉ</h2>
        <button 
          className="alert-close"
          onClick={handleDirectClose}
          aria-label="Fermer"
        >
          ×
        </button>
      </div>

      {/* Contenu */}
      <div className="alert-body">
        <div className="alert-message">
          <p className="alert-primary">
            <strong>Activité suspecte détectée</strong>
          </p>
          <p>
            Notre système a identifié des comportements anormaux sur votre ordinateur. 
            Un processus inconnu semble accéder à vos fichiers personnels.
          </p>
          
          <div className="threat-details">
            <div className="threat-item">
              <span className="threat-level high">🔴</span>
              <span>Accès non autorisé aux documents</span>
            </div>
            <div className="threat-item">
              <span className="threat-level medium">🟡</span>
              <span>Connexions réseau suspectes</span>
            </div>
            <div className="threat-item">
              <span className="threat-level low">🟢</span>
              <span>Système partiellement sécurisé</span>
            </div>
          </div>

          <p className="alert-recommendation">
            <strong>Action recommandée :</strong> Un technicien spécialisé va vous assister 
            pour sécuriser votre système. Restez connecté et suivez ses instructions.
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="alert-actions">
        <button 
          className="btn-secondary"
          onClick={handleDirectClose}
        >
          Ignorer (Non recommandé)
        </button>
        <button 
          className="btn-primary"
          onClick={handleAcceptAlert}
        >
          Obtenir de l'aide
        </button>
      </div>
    </motion.div>
  );

  /**
   * Rendu de la personnalisation
   */
  const renderPersonalization = () => (
    <motion.div
      className="personalization-content"
      initial={{ x: 300, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="alert-header">
        <div className="alert-icon">👤</div>
        <h2>Configuration de l'assistance</h2>
      </div>

      {/* Contenu */}
      <div className="alert-body">
        <p>
          Pour personnaliser votre expérience d'assistance, notre technicien 
          aimerait connaître votre nom ou pseudonyme.
        </p>
        
        <div className="name-input-container">
          <label htmlFor="playerName">Comment souhaitez-vous être appelé ?</label>
          <input
            id="playerName"
            type="text"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            placeholder="Votre nom ou pseudonyme"
            maxLength={20}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleSubmitName();
              }
            }}
            autoFocus
          />
        </div>

        <p className="privacy-note">
          <em>Cette information restera confidentielle et sera utilisée 
          uniquement pour améliorer la communication.</em>
        </p>
      </div>

      {/* Actions */}
      <div className="alert-actions">
        <button 
          className="btn-secondary"
          onClick={() => setStep('alert')}
        >
          Retour
        </button>
        <button 
          className="btn-primary"
          onClick={handleSubmitName}
          disabled={!playerName.trim()}
        >
          Continuer
        </button>
      </div>
    </motion.div>
  );

  /**
   * Rendu de la confirmation
   */
  const renderConfirmation = () => (
    <motion.div
      className="confirmation-content"
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div className="alert-header">
        <div className="alert-icon">✅</div>
        <h2>Connexion en cours...</h2>
      </div>

      {/* Contenu */}
      <div className="alert-body">
        <div className="connection-status">
          <div className="loading-animation">
            <div className="loading-dot"></div>
            <div className="loading-dot"></div>
            <div className="loading-dot"></div>
          </div>
          <p>
            Merci <strong>{playerName}</strong> ! 
            Notre technicien Tom se connecte à votre session...
          </p>
          <p className="status-text">
            Établissement de la connexion sécurisée...
          </p>
        </div>
      </div>
    </motion.div>
  );

  return (
    <div className="security-alert-overlay">
      <div className="security-alert-modal">
        <AnimatePresence mode="wait">
          {step === 'alert' && (
            <motion.div key="alert">
              {renderSecurityAlert()}
            </motion.div>
          )}
          {step === 'personalization' && (
            <motion.div key="personalization">
              {renderPersonalization()}
            </motion.div>
          )}
          {step === 'confirmed' && (
            <motion.div key="confirmation">
              {renderConfirmation()}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default SecurityAlert;
