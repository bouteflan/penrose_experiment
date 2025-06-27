/**
 * Store pour la simulation du système d'exploitation
 * Gère l'état de l'interface de bureau virtuelle et la corruption
 */
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

export const useOSStore = create(
  subscribeWithSelector((set, get) => ({
    // ===== ÉTAT INITIAL =====
    
    // Configuration
    sessionId: null,
    wsService: null,
    
    // État d'initialisation
    isInitialized: false,
    isLoading: false,
    
    // Thème et apparence
    theme: {
      name: 'Digital Homestead',
      background: null,
      accentColor: '#6c5ce7',
      mode: 'light'
    },
    
    // Bureau virtuel
    desktop: {
      background: null,
      widgets: [],
      shortcuts: [],
      layout: 'casual_organized'
    },
    
    // Système de fichiers virtuel
    files: [],
    folders: [],
    recycleBin: [],
    
    // Fenêtres ouvertes
    windows: [],
    activeWindow: null,
    
    // État de corruption
    corruptionLevel: 0.0,
    corruptionEffects: [],
    corruptionHistory: [],
    
    // Performance système simulée
    systemPerformance: 1.0,
    networkStatus: 'connected',
    securityAlerts: [],
    
    // Barre des tâches
    taskbar: {
      apps: ['file_explorer', 'tom_console', 'system_monitor'],
      notifications: []
    },
    
    // Personnalisation
    personalization: {
      playerName: null,
      customFolders: [],
      userSession: 'Session : Joueur'
    },
    
    // ===== ACTIONS =====
    
    /**
    * Initialise l'OS store
    */
    initialize: async (initData) => {
    const { sessionId, wsService } = initData;
    
    set({
    sessionId,
    wsService,
    isLoading: true,
    });
    
    try {
    // Attendre un peu pour éviter les requêtes simultanées
    await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 500));
    
    // Demander l'état initial de l'OS au backend
    const response = await fetch(`/api/game/sessions/${sessionId}/os-state`);
    
    if (response.ok) {
    const osData = await response.json();
    get()._loadOSState(osData.os_state);
    } else {
      // Générer un OS par défaut
      await get()._generateDefaultOS();
    }
    
    set({
      isInitialized: true,
      isLoading: false,
    });
      
    console.log('🖥️ OS Store initialisé');
    
    } catch (error) {
    console.error('❌ Erreur initialisation OS:', error);
    await get()._generateDefaultOS();
    
    set({
        isInitialized: true,
          isLoading: false,
      });
    }
  },
    
    /**
     * Charge l'état de l'OS depuis le backend
     */
    _loadOSState: (osState) => {
      set({
        theme: osState.theme || get().theme,
        desktop: osState.desktop || get().desktop,
        files: osState.file_system?.documents || [],
        folders: osState.file_system?.desktop || [],
        windows: osState.windows || [],
        systemPerformance: osState.system_state?.performance || 1.0,
        networkStatus: osState.system_state?.network_status || 'connected',
        personalization: {
          ...get().personalization,
          ...osState.personalization
        }
      });
    },
    
    /**
     * Génère un OS par défaut si le backend n'est pas disponible
     */
    _generateDefaultOS: async () => {
      const defaultTheme = {
        name: 'Digital Homestead',
        background: {
          name: 'Sunset Beach',
          type: 'personal_photo',
          description: 'Coucher de soleil sur une plage',
          color_palette: ['#FF6B35', '#F7931E', '#FFD23F', '#06BCC1']
        },
        accentColor: '#FF6B35',
        mode: 'light'
      };
      
      const defaultFiles = [
        {
          name: 'CV-pour-candidature.pdf',
          type: 'document',
          size: '2.3 MB',
          protected: true,
          icon: 'pdf_file',
          position: { x: 80, y: 200 }
        },
        {
          name: 'Photos_Vacances_Été.zip',
          type: 'archive',
          size: '234.1 MB',
          protected: true,
          icon: 'archive_file',
          position: { x: 220, y: 180 }
        },
        {
          name: 'Projet_Passion.docx',
          type: 'document',
          size: '8.2 MB',
          protected: true,
          icon: 'word_file',
          position: { x: 85, y: 260 }
        }
      ];
      
      const defaultFolders = [
        {
          name: 'Mes Documents',
          type: 'folder',
          protected: true,
          icon: 'folder_documents',
          position: { x: 50, y: 100 }
        },
        {
          name: 'Corbeille',
          type: 'recycle_bin',
          protected: false,
          icon: 'recycle_bin_empty',
          position: { x: 50, y: 300 }
        }
      ];
      
      const defaultWidgets = [
        {
          id: 'clock_widget',
          type: 'clock',
          position: { x: 20, y: 20 },
          size: { width: 200, height: 80 },
          data: {
            time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
            date: new Date().toLocaleDateString('fr-FR'),
            timezone: 'Europe/Paris'
          }
        },
        {
          id: 'weather_widget',
          type: 'weather',
          position: { x: 20, y: 120 },
          size: { width: 180, height: 100 },
          data: {
            location: 'Le Mans',
            temperature: 22,
            condition: 'sunny',
            forecast: 'Ensoleillé'
          }
        },
        {
          id: 'music_widget',
          type: 'music_player',
          position: { x: 250, y: 20 },
          size: { width: 220, height: 60 },
          data: {
            current_song: 'Lo-fi Hip Hop - Chill Beats',
            artist: 'Study Music',
            playing: true,
            volume: 0.3
          }
        }
      ];
      
      set({
        theme: defaultTheme,
        desktop: {
          background: defaultTheme.background,
          widgets: defaultWidgets,
          shortcuts: defaultFiles.slice(0, 2), // Premiers fichiers comme raccourcis
          layout: 'casual_organized'
        },
        files: defaultFiles,
        folders: defaultFolders,
      });
    },
    
    /**
     * Ouvre une nouvelle fenêtre
     */
    openWindow: (windowData) => {
      const state = get();
      const windowId = windowData.id || `window_${Date.now()}`;
      
      const newWindow = {
        id: windowId,
        ...windowData,
        isOpen: true,
        zIndex: state.windows.length + 100,
        createdAt: new Date().toISOString()
      };
      
      set({
        windows: [...state.windows, newWindow],
        activeWindow: windowId
      });
      
      console.log('🪟 Fenêtre ouverte:', windowData.title || windowId);
      return windowId;
    },
    
    /**
     * Ferme une fenêtre
     */
    closeWindow: (windowId) => {
      const state = get();
      
      set({
        windows: state.windows.filter(w => w.id !== windowId),
        activeWindow: state.activeWindow === windowId ? null : state.activeWindow
      });
      
      console.log('❌ Fenêtre fermée:', windowId);
    },
    
    /**
     * Active une fenêtre (la met au premier plan)
     */
    focusWindow: (windowId) => {
      const state = get();
      const maxZ = Math.max(...state.windows.map(w => w.zIndex || 0));
      
      set({
        windows: state.windows.map(w => 
          w.id === windowId 
            ? { ...w, zIndex: maxZ + 1 }
            : w
        ),
        activeWindow: windowId
      });
    },
    
    /**
     * Met à jour les propriétés d'une fenêtre
     */
    updateWindow: (windowId, updates) => {
      set({
        windows: get().windows.map(w => 
          w.id === windowId 
            ? { ...w, ...updates }
            : w
        )
      });
    },
    
    /**
     * Gère une action sur un fichier
     */
    handleFileAction: (action, fileName, data = {}) => {
      const state = get();
      
      switch (action) {
        case 'delete':
          return get()._deleteFile(fileName);
        
        case 'rename':
          return get()._renameFile(fileName, data.newName);
        
        case 'move':
          return get()._moveFile(fileName, data.destination);
        
        case 'properties':
          return get()._showFileProperties(fileName);
        
        default:
          console.warn('Action fichier non reconnue:', action);
          return false;
      }
    },
    
    /**
     * Supprime un fichier (le déplace vers la corbeille)
     */
    _deleteFile: (fileName) => {
      const state = get();
      const file = state.files.find(f => f.name === fileName);
      
      if (!file) {
        console.warn('Fichier non trouvé:', fileName);
        return false;
      }
      
      // Déplacer vers la corbeille
      const deletedFile = {
        ...file,
        deletedAt: new Date().toISOString(),
        originalLocation: 'desktop'
      };
      
      set({
        files: state.files.filter(f => f.name !== fileName),
        recycleBin: [...state.recycleBin, deletedFile]
      });
      
      // Notifier le backend si connecté
      if (state.wsService) {
        state.wsService.send({
          type: 'file_action',
          session_id: state.sessionId,
          action: 'delete',
          target: fileName,
          timestamp: new Date().toISOString()
        });
      }
      
      console.log('🗑️ Fichier supprimé:', fileName);
      return true;
    },
    
    /**
     * Renomme un fichier
     */
    _renameFile: (fileName, newName) => {
      const state = get();
      
      set({
        files: state.files.map(f => 
          f.name === fileName 
            ? { ...f, name: newName }
            : f
        )
      });
      
      // Notifier le backend
      if (state.wsService) {
        state.wsService.send({
          type: 'file_action',
          session_id: state.sessionId,
          action: 'rename',
          target: fileName,
          data: { newName },
          timestamp: new Date().toISOString()
        });
      }
      
      console.log('✏️ Fichier renommé:', fileName, '->', newName);
      return true;
    },
    
    /**
     * Affiche les propriétés d'un fichier
     */
    _showFileProperties: (fileName) => {
      const file = get().files.find(f => f.name === fileName);
      
      if (!file) return false;
      
      // Ouvrir une fenêtre de propriétés
      get().openWindow({
        id: `properties_${fileName}`,
        type: 'file_properties',
        title: `Propriétés - ${fileName}`,
        position: { x: 300, y: 200 },
        size: { width: 400, height: 500 },
        content: {
          file: file,
          dependencies: fileName === 'helper.exe' ? ['malware.exe'] : []
        }
      });
      
      return true;
    },
    
    /**
     * Applique un effet de corruption
     */
    applyCorruption: (corruptionData) => {
      const state = get();
      
      const newLevel = Math.min(corruptionData.new_level || 0, 1.0);
      const effects = corruptionData.effects || [];
      
      set({
        corruptionLevel: newLevel,
        corruptionEffects: [...state.corruptionEffects, ...effects],
        corruptionHistory: [...state.corruptionHistory, {
          timestamp: new Date().toISOString(),
          level: newLevel,
          effects: effects
        }]
      });
      
      // Appliquer les effets visuels
      get()._applyCorruptionEffects(effects);
      
      console.log('💥 Corruption appliquée:', newLevel);
    },
    
    /**
     * Applique les effets visuels de corruption
     */
    _applyCorruptionEffects: (effects) => {
      effects.forEach(effect => {
        switch (effect.type) {
          case 'pixel_corruption':
            get()._applyPixelCorruption(effect);
            break;
          
          case 'widget_glitch':
            get()._applyWidgetGlitch(effect);
            break;
          
          case 'color_shift':
            get()._applyColorShift(effect);
            break;
          
          case 'background_decay':
            get()._applyBackgroundDecay(effect);
            break;
          
          default:
            console.log('Effet de corruption:', effect.type);
        }
      });
    },
    
    /**
     * Applique la corruption de pixels
     */
    _applyPixelCorruption: (effect) => {
      const state = get();
      
      // Modifier le fond d'écran
      if (state.desktop.background) {
        set({
          desktop: {
            ...state.desktop,
            background: {
              ...state.desktop.background,
              corruption: {
                dead_pixels: effect.intensity * 50,
                color_shift: effect.intensity * 0.3
              }
            }
          }
        });
      }
    },
    
    /**
     * Applique le glitch des widgets
     */
    _applyWidgetGlitch: (effect) => {
      const state = get();
      
      set({
        desktop: {
          ...state.desktop,
          widgets: state.desktop.widgets.map(widget => {
            if (widget.type === 'weather') {
              return {
                ...widget,
                corruption: {
                  display_error: true,
                  data_corruption: 'ERROR_404_WEATHER'
                }
              };
            }
            return widget;
          })
        }
      });
    },
    
    /**
     * Applique le changement de couleur
     */
    _applyColorShift: (effect) => {
      const corruptedPalettes = {
        'sick_yellow': ['#D4AF37', '#DAA520', '#B8860B', '#FFD700'],
        'toxic_green': ['#ADFF2F', '#9ACD32', '#32CD32', '#00FF00'],
        'corrupted_red': ['#DC143C', '#B22222', '#8B0000', '#FF6347']
      };
      
      const paletteNames = Object.keys(corruptedPalettes);
      const selectedPalette = paletteNames[Math.floor(Math.random() * paletteNames.length)];
      
      set({
        theme: {
          ...get().theme,
          corruptedPalette: {
            name: selectedPalette,
            colors: corruptedPalettes[selectedPalette],
            intensity: effect.intensity
          }
        }
      });
    },
    
    /**
     * Simule une corruption (pour debug)
     */
    simulateCorruption: () => {
      const randomEffect = {
        type: ['pixel_corruption', 'widget_glitch', 'color_shift'][Math.floor(Math.random() * 3)],
        intensity: Math.random() * 0.5 + 0.2,
        timestamp: new Date().toISOString()
      };
      
      get().applyCorruption({
        new_level: Math.min(get().corruptionLevel + 0.1, 1.0),
        effects: [randomEffect]
      });
    },
    
    /**
     * Met à jour les widgets
     */
    updateWidget: (widgetId, updates) => {
      const state = get();
      
      set({
        desktop: {
          ...state.desktop,
          widgets: state.desktop.widgets.map(widget =>
            widget.id === widgetId
              ? { ...widget, ...updates }
              : widget
          )
        }
      });
    },
    
    /**
     * Ajoute une notification
     */
    addNotification: (notification) => {
      const state = get();
      const notificationId = `notif_${Date.now()}`;
      
      const newNotification = {
        id: notificationId,
        ...notification,
        timestamp: new Date().toISOString()
      };
      
      set({
        taskbar: {
          ...state.taskbar,
          notifications: [...state.taskbar.notifications, newNotification]
        }
      });
      
      // Auto-supprimer après 5 secondes si pas persistante
      if (!notification.persistent) {
        setTimeout(() => {
          get().removeNotification(notificationId);
        }, 5000);
      }
      
      return notificationId;
    },
    
    /**
     * Supprime une notification
     */
    removeNotification: (notificationId) => {
      const state = get();
      
      set({
        taskbar: {
          ...state.taskbar,
          notifications: state.taskbar.notifications.filter(n => n.id !== notificationId)
        }
      });
    },
    
    /**
     * Met à jour la personnalisation
     */
    updatePersonalization: (updates) => {
      set({
        personalization: {
          ...get().personalization,
          ...updates
        }
      });
    },
    
    /**
     * Nettoyage du store
     */
    cleanup: () => {
      set({
        windows: [],
        activeWindow: null,
        corruptionEffects: [],
        taskbar: {
          ...get().taskbar,
          notifications: []
        }
      });
      
      console.log('🧹 OS Store nettoyé');
    },
    
    // ===== SÉLECTEURS =====
    
    /**
     * Retourne la fenêtre active
     */
    getActiveWindow: () => {
      const state = get();
      return state.windows.find(w => w.id === state.activeWindow);
    },
    
    /**
     * Retourne les fenêtres triées par z-index
     */
    getSortedWindows: () => {
      return get().windows.sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0));
    },
    
    /**
     * Retourne l'état de corruption
     */
    getCorruptionState: () => {
      const state = get();
      return {
        level: state.corruptionLevel,
        effects: state.corruptionEffects,
        phase: state.corruptionLevel <= 0.2 ? 'minimal' :
               state.corruptionLevel <= 0.4 ? 'noticeable' :
               state.corruptionLevel <= 0.6 ? 'concerning' :
               state.corruptionLevel <= 0.8 ? 'severe' : 'catastrophic'
      };
    },
    
    /**
     * Retourne les statistiques du système
     */
    getSystemStats: () => {
      const state = get();
      return {
        performance: state.systemPerformance,
        corruption: state.corruptionLevel,
        files: state.files.length,
        openWindows: state.windows.length,
        notifications: state.taskbar.notifications.length
      };
    }
  }))
);

// Synchronisation avec le game store
useOSStore.subscribe(
  (state) => state.corruptionLevel,
  (level) => {
    // Notifier les autres stores du changement de corruption
    console.log('💀 Niveau de corruption:', (level * 100).toFixed(1) + '%');
  }
);
