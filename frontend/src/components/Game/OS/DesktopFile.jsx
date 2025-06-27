/**
 * Composant DesktopFile - Représente un fichier sur le bureau virtuel
 * Gère l'affichage, les interactions et les effets de corruption
 */
import React, { useState, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import './DesktopFile.css';

const DesktopFile = ({
  file,
  isSelected,
  onSelect,
  onAction,
  onDragStart,
  onDragEnd,
  corruptionLevel
}) => {
  // État local
  const [isHovered, setIsHovered] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [lastClickTime, setLastClickTime] = useState(0);
  
  // Refs
  const fileRef = useRef(null);
  
  /**
   * Obtient l'icône du fichier selon son type
   */
  const getFileIcon = useCallback(() => {
    const { type, icon, protected: isProtected } = file;
    
    // Fichiers corrompus
    if (corruptionLevel > 0.5 && Math.random() > 0.7) {
      return '❌';
    }
    
    // Icônes par type
    const iconMap = {
      'pdf_file': '📄',
      'word_file': '📝',
      'archive_file': '📦',
      'image_file': '🖼️',
      'video_file': '🎬',
      'audio_file': '🎵',
      'executable': '⚙️',
      'text_file': '📃',
      'spreadsheet': '📊'
    };
    
    let baseIcon = iconMap[icon] || iconMap[type] || '📄';
    
    // Fichiers protégés ont un cadenas
    if (isProtected) {
      baseIcon = '🔒';
    }
    
    return baseIcon;
  }, [file, corruptionLevel]);

  /**
   * Obtient le nom d'affichage du fichier avec corruption
   */
  const getDisplayName = useCallback(() => {
    let name = file.name;
    
    // Corruption du nom de fichier
    if (corruptionLevel > 0.6) {
      const corruptionChars = ['�', '▓', '█', '?', '#', '@'];
      const corruptionChance = (corruptionLevel - 0.6) * 2.5; // 0 à 1 pour les 40% derniers
      
      name = name.split('').map(char => {
        if (Math.random() < corruptionChance * 0.3) {
          return corruptionChars[Math.floor(Math.random() * corruptionChars.length)];
        }
        return char;
      }).join('');
    }
    
    return name;
  }, [file.name, corruptionLevel]);

  /**
   * Gestionnaire de clic
   */
  const handleClick = useCallback((event) => {
    event.stopPropagation();
    
    const now = Date.now();
    const timeDiff = now - lastClickTime;
    setLastClickTime(now);
    
    // Double-clic (moins de 500ms)
    if (timeDiff < 500) {
      onAction('open', file.name);
    } else {
      // Simple clic - sélection
      onSelect(file.name, event.ctrlKey || event.metaKey);
    }
  }, [file.name, onSelect, onAction, lastClickTime]);

  /**
   * Gestionnaire de clic droit
   */
  const handleContextMenu = useCallback((event) => {
    event.preventDefault();
    event.stopPropagation();
    
    // Sélectionner le fichier s'il ne l'est pas
    if (!isSelected) {
      onSelect(file.name, false);
    }
    
    // Le menu contextuel sera géré par le parent
  }, [file.name, isSelected, onSelect]);

  /**
   * Gestionnaires de drag & drop
   */
  const handleDragStart = useCallback((event) => {
    setIsDragging(true);
    onDragStart(file.name, 'file');
    
    // Données de drag
    event.dataTransfer.setData('text/plain', file.name);
    event.dataTransfer.setData('application/json', JSON.stringify(file));
    event.dataTransfer.effectAllowed = 'move';
  }, [file, onDragStart]);

  const handleDragEnd = useCallback(() => {
    setIsDragging(false);
    onDragEnd();
  }, [onDragEnd]);

  /**
   * Style de corruption
   */
  const getCorruptionStyle = useCallback(() => {
    const style = {};
    
    if (corruptionLevel > 0.3) {
      // Désaturation progressive
      const desaturation = Math.min((corruptionLevel - 0.3) * 1.43, 1); // 0 à 1 pour 0.3-1
      style.filter = `saturate(${100 - desaturation * 70}%)`;
    }
    
    if (corruptionLevel > 0.5) {
      // Légère rotation
      const rotation = (corruptionLevel - 0.5) * 10 * (Math.random() - 0.5); // -5 à +5 degrés
      style.transform = `rotate(${rotation}deg)`;
    }
    
    if (corruptionLevel > 0.7) {
      // Effet de glitch
      style.animation = `file-glitch ${1 / corruptionLevel}s infinite`;
    }
    
    return style;
  }, [corruptionLevel]);

  /**
   * Classes CSS dynamiques
   */
  const getClassNames = useCallback(() => {
    const classes = ['desktop-file'];
    
    if (isSelected) classes.push('selected');
    if (isHovered) classes.push('hovered');
    if (isDragging) classes.push('dragging');
    if (file.protected) classes.push('protected');
    
    // Classes de corruption
    if (corruptionLevel > 0.8) classes.push('corruption-critical');
    else if (corruptionLevel > 0.6) classes.push('corruption-high');
    else if (corruptionLevel > 0.3) classes.push('corruption-medium');
    else if (corruptionLevel > 0.1) classes.push('corruption-low');
    
    return classes.join(' ');
  }, [isSelected, isHovered, isDragging, file.protected, corruptionLevel]);

  return (
    <motion.div
      ref={fileRef}
      className={getClassNames()}
      style={{
        position: 'absolute',
        left: file.position?.x || 100,
        top: file.position?.y || 100,
        ...getCorruptionStyle()
      }}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      drag={!file.protected}
      dragMomentum={false}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onClick={handleClick}
      onContextMenu={handleContextMenu}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      title={`${file.name} (${file.size || 'Taille inconnue'})`}
    >
      {/* Icône du fichier */}
      <div className="file-icon">
        <span className="icon-emoji">
          {getFileIcon()}
        </span>
        
        {/* Badge de protection */}
        {file.protected && (
          <span className="protection-badge">🔒</span>
        )}
        
        {/* Indicateur de corruption */}
        {corruptionLevel > 0.4 && (
          <span className="corruption-indicator">⚠️</span>
        )}
      </div>

      {/* Nom du fichier */}
      <div className="file-name">
        <span>{getDisplayName()}</span>
      </div>

      {/* Info-bulle détaillée au survol */}
      {isHovered && (
        <motion.div
          className="file-tooltip"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
        >
          <div className="tooltip-content">
            <div><strong>{file.name}</strong></div>
            <div>Type: {file.type}</div>
            <div>Taille: {file.size || 'Inconnue'}</div>
            {file.protected && <div>🔒 Fichier protégé</div>}
            {corruptionLevel > 0.3 && <div>⚠️ Corruption détectée</div>}
          </div>
        </motion.div>
      )}

      {/* Effet de sélection */}
      {isSelected && (
        <motion.div
          className="selection-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        />
      )}

      {/* Effet de corruption visuelle */}
      {corruptionLevel > 0.6 && (
        <div 
          className="corruption-overlay"
          style={{
            opacity: (corruptionLevel - 0.6) * 2.5,
            background: `linear-gradient(45deg, 
              rgba(255,0,0,0.3) 0%, 
              transparent 25%, 
              rgba(0,255,0,0.3) 50%, 
              transparent 75%, 
              rgba(0,0,255,0.3) 100%)`
          }}
        />
      )}
    </motion.div>
  );
};

export default DesktopFile;
