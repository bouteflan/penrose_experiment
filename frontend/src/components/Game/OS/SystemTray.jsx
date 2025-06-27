/**
 * Composant SystemTray - Barre système en bas de l'écran
 * Simule une barre des tâches Windows
 */
import React from 'react';
import { motion } from 'framer-motion';
import { useGameStore } from '../../../stores/gameStore';
import { useOSStore } from '../../../stores/osStore';
import './SystemTray.css';

const SystemTray = ({ onPlayerAction }) => {
  // Stores
  const gameStore = useGameStore();
  const osStore = useOSStore();

  /**
   * Gestionnaire de clic sur application
   */
  const handleAppClick = (appId) => {
    onPlayerAction({
      type: 'taskbar_app_clicked',
      app_id: appId,
      is_meta_action: true
    });
  };

  /**
   * Gestionnaire de clic sur notification
   */
  const handleNotificationClick = (notificationId) => {
    onPlayerAction({
      type: 'notification_clicked',
      notification_id: notificationId,
      is_meta_action: true
    });
  };

  return (
    <motion.div
      className="system-tray"
      initial={{ y: 60 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, delay: 1 }}
    >
      {/* Bouton Start */}
      <div className="start-section">
        <button 
          className="start-button"
          onClick={() => handleAppClick('start_menu')}
        >
          <span className="start-icon">🖥️</span>
        </button>
      </div>

      {/* Applications de la barre des tâches */}
      <div className="apps-section">
        {osStore.taskbar?.apps?.map((appId) => (
          <button
            key={appId}
            className={`taskbar-app ${appId === 'tom_console' ? 'active' : ''}`}
            onClick={() => handleAppClick(appId)}
            title={getAppTitle(appId)}
          >
            <span className="app-icon">{getAppIcon(appId)}</span>
          </button>
        ))}
      </div>

      {/* Zone de notifications */}
      <div className="notification-section">
        {osStore.taskbar?.notifications?.slice(-3).map((notification) => (
          <motion.button
            key={notification.id}
            className={`notification-item ${notification.type || 'info'}`}
            onClick={() => handleNotificationClick(notification.id)}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            whileHover={{ scale: 1.05 }}
          >
            <span className="notification-icon">
              {getNotificationIcon(notification.type)}
            </span>
          </motion.button>
        ))}
      </div>

      {/* Zone système */}
      <div className="system-section">
        {/* Indicateurs système */}
        <div className="system-indicators">
          {/* État de corruption */}
          {osStore.corruptionLevel > 0.1 && (
            <div 
              className="corruption-indicator"
              title={`Corruption: ${(osStore.corruptionLevel * 100).toFixed(1)}%`}
            >
              ⚠️
            </div>
          )}
          
          {/* État réseau */}
          <div 
            className={`network-indicator ${osStore.networkStatus}`}
            title={`Réseau: ${osStore.networkStatus}`}
          >
            📶
          </div>
          
          {/* Performance système */}
          <div 
            className="performance-indicator"
            title={`Performance: ${(osStore.systemPerformance * 100).toFixed(0)}%`}
          >
            {osStore.systemPerformance > 0.8 ? '🟢' : 
             osStore.systemPerformance > 0.6 ? '🟡' : '🔴'}
          </div>
        </div>

        {/* Horloge système */}
        <div className="system-clock">
          <div className="clock-time">
            {new Date().toLocaleTimeString('fr-FR', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
          <div className="clock-date">
            {new Date().toLocaleDateString('fr-FR', {
              day: '2-digit',
              month: '2-digit'
            })}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

/**
 * Retourne le titre d'une application
 */
const getAppTitle = (appId) => {
  const titles = {
    'file_explorer': 'Explorateur de fichiers',
    'tom_console': 'Console Tom',
    'system_monitor': 'Moniteur système',
    'security_center': 'Centre de sécurité'
  };
  return titles[appId] || appId;
};

/**
 * Retourne l'icône d'une application
 */
const getAppIcon = (appId) => {
  const icons = {
    'file_explorer': '📁',
    'tom_console': '💬',
    'system_monitor': '📊',
    'security_center': '🛡️'
  };
  return icons[appId] || '❓';
};

/**
 * Retourne l'icône d'une notification
 */
const getNotificationIcon = (type) => {
  const icons = {
    'info': 'ℹ️',
    'warning': '⚠️',
    'error': '❌',
    'success': '✅',
    'security': '🛡️'
  };
  return icons[type] || 'ℹ️';
};

export default SystemTray;
