/**
 * Composant ContextMenu - Menu contextuel du bureau
 * Affiche les options disponibles selon l'élément cliqué
 */
import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import './ContextMenu.css';

const ContextMenu = ({ 
  position, 
  onClose, 
  onAction, 
  target 
}) => {
  // Refs
  const menuRef = useRef(null);

  /**
   * Fermer le menu si clic à l'extérieur
   */
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        onClose();
      }
    };

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  /**
   * Gestionnaire d'action de menu
   */
  const handleMenuAction = (actionType, data = {}) => {
    onAction({
      type: 'context_menu_action',
      action: actionType,
      target: target,
      data,
      is_meta_action: true
    });
    onClose();
  };

  /**
   * Options du menu selon le contexte
   */
  const getMenuOptions = () => {
    // Menu du bureau vide
    if (!target || target.classList?.contains('virtual-desktop')) {
      return [
        {
          icon: '🔄',
          label: 'Actualiser',
          action: () => handleMenuAction('refresh_desktop')
        },
        {
          icon: '📋',
          label: 'Coller',
          action: () => handleMenuAction('paste'),
          disabled: true
        },
        { separator: true },
        {
          icon: '🖼️',
          label: 'Personnaliser le bureau',
          action: () => handleMenuAction('personalize_desktop')
        },
        {
          icon: '⚙️',
          label: 'Paramètres d\'affichage',
          action: () => handleMenuAction('display_settings')
        }
      ];
    }

    // Menu pour fichier/dossier
    if (target.classList?.contains('desktop-file') || target.classList?.contains('desktop-folder')) {
      const isFile = target.classList?.contains('desktop-file');
      
      return [
        {
          icon: '👁️',
          label: 'Ouvrir',
          action: () => handleMenuAction('open')
        },
        { separator: true },
        {
          icon: '✂️',
          label: 'Couper',
          action: () => handleMenuAction('cut')
        },
        {
          icon: '📋',
          label: 'Copier',
          action: () => handleMenuAction('copy')
        },
        { separator: true },
        {
          icon: '🏷️',
          label: 'Renommer',
          action: () => handleMenuAction('rename')
        },
        {
          icon: '🗑️',
          label: 'Supprimer',
          action: () => handleMenuAction('delete'),
          dangerous: true
        },
        { separator: true },
        {
          icon: '🔍',
          label: 'Propriétés',
          action: () => handleMenuAction('properties'),
          highlighted: isFile // Mettre en évidence pour les fichiers
        }
      ];
    }

    // Menu par défaut
    return [
      {
        icon: '❓',
        label: 'Action indisponible',
        disabled: true
      }
    ];
  };

  const menuOptions = getMenuOptions();

  return (
    <motion.div
      ref={menuRef}
      className="context-menu"
      style={{
        left: position.x,
        top: position.y
      }}
      initial={{ opacity: 0, scale: 0.9, y: -10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: -10 }}
      transition={{ duration: 0.15 }}
    >
      <div className="context-menu-content">
        {menuOptions.map((option, index) => {
          if (option.separator) {
            return <div key={index} className="menu-separator" />;
          }

          return (
            <button
              key={index}
              className={`menu-item ${option.disabled ? 'disabled' : ''} ${option.dangerous ? 'dangerous' : ''} ${option.highlighted ? 'highlighted' : ''}`}
              onClick={option.action}
              disabled={option.disabled}
            >
              <span className="menu-icon">{option.icon}</span>
              <span className="menu-label">{option.label}</span>
              {option.shortcut && (
                <span className="menu-shortcut">{option.shortcut}</span>
              )}
            </button>
          );
        })}
      </div>
    </motion.div>
  );
};

export default ContextMenu;
