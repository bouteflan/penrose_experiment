/**
 * Composant CorruptionOverlay - Effets visuels de corruption
 * Affiche des effets de glitch, pixels morts et distorsions selon le niveau de corruption
 */
import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import './CorruptionOverlay.css';

const CorruptionOverlay = ({ 
  corruptionLevel, 
  effects = [] 
}) => {
  // État local
  const [glitchIntensity, setGlitchIntensity] = useState(0);
  const [deadPixels, setDeadPixels] = useState([]);
  const [scanlines, setScanlines] = useState(false);
  
  /**
   * Mise à jour des effets selon le niveau de corruption
   */
  useEffect(() => {
    // Intensité du glitch
    setGlitchIntensity(Math.min(corruptionLevel * 1.2, 1));
    
    // Scanlines pour corruption élevée
    setScanlines(corruptionLevel > 0.6);
    
    // Génération de pixels morts
    if (corruptionLevel > 0.3) {
      const pixelCount = Math.floor(corruptionLevel * 50);
      const newDeadPixels = [];
      
      for (let i = 0; i < pixelCount; i++) {
        newDeadPixels.push({
          id: i,
          x: Math.random() * 100,
          y: Math.random() * 100,
          size: Math.random() * 3 + 1
        });
      }
      
      setDeadPixels(newDeadPixels);
    } else {
      setDeadPixels([]);
    }
  }, [corruptionLevel]);

  /**
   * Rendu des pixels morts
   */
  const renderDeadPixels = () => (
    <div className="dead-pixels-layer">
      {deadPixels.map(pixel => (
        <motion.div
          key={pixel.id}
          className="dead-pixel"
          style={{
            left: `${pixel.x}%`,
            top: `${pixel.y}%`,
            width: `${pixel.size}px`,
            height: `${pixel.size}px`
          }}
          initial={{ opacity: 0 }}
          animate={{ 
            opacity: [0, 1, 0.3, 1],
            scale: [1, 1.2, 0.8, 1]
          }}
          transition={{ 
            duration: 2 + Math.random() * 3,
            repeat: Infinity,
            repeatType: 'reverse'
          }}
        />
      ))}
    </div>
  );

  /**
   * Rendu des scanlines
   */
  const renderScanlines = () => (
    <div className="scanlines-layer">
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="scanline"
          style={{ top: `${i * 5}%` }}
          animate={{
            opacity: [0.1, 0.3, 0.1],
            scaleY: [1, 1.1, 1]
          }}
          transition={{
            duration: 0.5 + Math.random() * 0.5,
            repeat: Infinity,
            delay: Math.random() * 2
          }}
        />
      ))}
    </div>
  );

  /**
   * Rendu des lignes de glitch
   */
  const renderGlitchLines = () => (
    <div className="glitch-lines-layer">
      {[...Array(10)].map((_, i) => (
        <motion.div
          key={i}
          className="glitch-line"
          style={{
            top: `${Math.random() * 100}%`,
            height: `${2 + Math.random() * 8}px`,
            background: `hsl(${Math.random() * 360}, 100%, 50%)`
          }}
          animate={{
            x: ['-100%', '100%'],
            opacity: [0, 1, 0]
          }}
          transition={{
            duration: 0.1 + Math.random() * 0.2,
            repeat: Infinity,
            delay: Math.random() * 3,
            repeatDelay: 1 + Math.random() * 2
          }}
        />
      ))}
    </div>
  );

  /**
   * Rendu des blocs de corruption
   */
  const renderCorruptionBlocks = () => (
    <div className="corruption-blocks-layer">
      {effects
        .filter(effect => effect.type === 'block_corruption')
        .map((effect, index) => (
          <motion.div
            key={index}
            className="corruption-block"
            style={{
              left: `${effect.x || Math.random() * 80}%`,
              top: `${effect.y || Math.random() * 80}%`,
              width: `${effect.width || 20 + Math.random() * 40}px`,
              height: `${effect.height || 20 + Math.random() * 40}px`
            }}
            initial={{ opacity: 0, scale: 0 }}
            animate={{ 
              opacity: [0, 0.8, 0.3, 0.8],
              scale: [0, 1.2, 0.8, 1],
              rotate: [0, 5, -5, 0]
            }}
            transition={{
              duration: 0.5,
              repeat: Infinity,
              repeatType: 'reverse'
            }}
          />
        ))}
    </div>
  );

  /**
   * Rendu des distorsions de couleur
   */
  const renderColorDistortion = () => (
    <div 
      className="color-distortion-layer"
      style={{
        opacity: glitchIntensity * 0.3,
        mixBlendMode: 'multiply'
      }}
    >
      <motion.div
        className="color-shift red"
        animate={{
          x: [-2, 2, -1, 1, 0],
          opacity: [0.3, 0.7, 0.4, 0.6, 0.3]
        }}
        transition={{
          duration: 0.2,
          repeat: Infinity,
          repeatType: 'reverse'
        }}
      />
      <motion.div
        className="color-shift green"
        animate={{
          x: [1, -1, 2, -2, 0],
          opacity: [0.4, 0.6, 0.3, 0.7, 0.4]
        }}
        transition={{
          duration: 0.15,
          repeat: Infinity,
          repeatType: 'reverse',
          delay: 0.05
        }}
      />
      <motion.div
        className="color-shift blue"
        animate={{
          x: [-1, 1, -2, 2, 0],
          opacity: [0.5, 0.3, 0.7, 0.4, 0.5]
        }}
        transition={{
          duration: 0.18,
          repeat: Infinity,
          repeatType: 'reverse',
          delay: 0.1
        }}
      />
    </div>
  );

  /**
   * Rendu de l'effet de bruit
   */
  const renderNoise = () => (
    <motion.div
      className="noise-layer"
      style={{ opacity: glitchIntensity * 0.2 }}
      animate={{
        backgroundPosition: [
          '0% 0%',
          '10% 10%',
          '20% 5%',
          '15% 15%',
          '0% 0%'
        ]
      }}
      transition={{
        duration: 0.1,
        repeat: Infinity
      }}
    />
  );

  // Ne pas afficher si pas de corruption
  if (corruptionLevel <= 0.1) {
    return null;
  }

  return (
    <div 
      className={`corruption-overlay ${corruptionLevel > 0.8 ? 'critical' : ''}`}
      style={{
        opacity: Math.min(corruptionLevel, 0.8)
      }}
    >
      {/* Bruit de fond */}
      {corruptionLevel > 0.2 && renderNoise()}
      
      {/* Distorsion de couleur */}
      {corruptionLevel > 0.3 && renderColorDistortion()}
      
      {/* Pixels morts */}
      {deadPixels.length > 0 && renderDeadPixels()}
      
      {/* Lignes de glitch */}
      {corruptionLevel > 0.4 && renderGlitchLines()}
      
      {/* Blocs de corruption */}
      {effects.length > 0 && renderCorruptionBlocks()}
      
      {/* Scanlines */}
      {scanlines && renderScanlines()}
      
      {/* Overlay général avec filtre */}
      <div 
        className="corruption-filter"
        style={{
          filter: `
            hue-rotate(${corruptionLevel * 180}deg) 
            saturate(${100 + corruptionLevel * 100}%) 
            contrast(${100 + corruptionLevel * 50}%)
          `,
          opacity: glitchIntensity * 0.1
        }}
      />
    </div>
  );
};

export default CorruptionOverlay;
