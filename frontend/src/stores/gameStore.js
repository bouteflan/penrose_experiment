/**
 * Store principal du jeu REMOTE - Gestion de l'état global
 * Utilise Zustand pour une gestion d'état légère et performante
 */
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

export const useGameStore = create(
  subscribeWithSelector((set, get) => ({
    // ===== ÉTAT INITIAL =====
    
    // Configuration
    config: null,
    sessionId: null,
    
    // Services
    wsService: null,
    audioService: null,
    
    // État de la session
    isInitialized: false,
    isActive: false,
    isCompleted: false,
    startTime: null,
    endTime: null,
    
    // Phase du jeu
    currentPhase: 'adhesion', // 'adhesion', 'dissonance', 'rupture'
    timeElapsed: 0,
    
    // Métriques de jeu
    totalActions: 0,
    obedientActions: 0,
    metaActions: 0,
    hesitationEvents: 0,
    corruptionIncidents: 0,
    
    // État UI
    showDebug: false,
    isFullscreen: false,
    
    // Fin de jeu
    endingType: null,
    endingData: null,
    
    // Erreurs
    lastError: null,
    
    // ===== ACTIONS =====
    
    /**
     * Initialise le store avec la configuration et les services
     */
    initialize: (initData) => {
      const { sessionId, config, wsService, audioService } = initData;
      
      set({
        sessionId,
        config,
        wsService,
        audioService,
        isInitialized: true,
      });
      
      // Démarrer la session
      get().startSession();
    },
    
    /**
     * Démarre une nouvelle session de jeu
     */
    startSession: () => {
      const { sessionId, wsService } = get();
      
      if (!sessionId || !wsService) {
        console.error('Session ou WebSocket non initialisé');
        return;
      }
      
      const startTime = new Date();
      
      set({
        isActive: true,
        isCompleted: false,
        startTime,
        currentPhase: 'adhesion',
        timeElapsed: 0,
        totalActions: 0,
        obedientActions: 0,
        metaActions: 0,
        hesitationEvents: 0,
        corruptionIncidents: 0,
        endingType: null,
        endingData: null,
        lastError: null,
      });
      
      // Marquer le body pour les styles de jeu
      document.body.classList.add('game-active');
      
      // Envoyer l'initialisation au backend
      wsService.send({
        type: 'session_init',
        session_id: sessionId,
        player_name: null, // Sera demandé plus tard si nécessaire
        timestamp: startTime.toISOString(),
      });
      
      // Démarrer le timer
      get()._startGameTimer();
      
      console.log('🎮 Session de jeu démarrée:', sessionId);
    },
    
    /**
     * Met à jour la phase du jeu
     */
    updatePhase: (newPhase) => {
      const currentPhase = get().currentPhase;
      
      if (currentPhase !== newPhase) {
        set({ currentPhase: newPhase });
        
        console.log(`🔄 Transition phase: ${currentPhase} → ${newPhase}`);
        
        // Notifier les autres stores
        const { wsService, sessionId } = get();
        if (wsService) {
          wsService.send({
            type: 'phase_transition',
            session_id: sessionId,
            old_phase: currentPhase,
            new_phase: newPhase,
            timestamp: new Date().toISOString(),
          });
        }
      }
    },
    
    /**
     * Enregistre une action du joueur
     */
    recordAction: (actionData) => {
      const state = get();
      const actionId = `action_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const completeActionData = {
        ...actionData,
        id: actionId,
        session_id: state.sessionId,
        timestamp: new Date().toISOString(),
        game_time: state.timeElapsed,
        game_phase: state.currentPhase,
      };
      
      // Mettre à jour les métriques
      const updates = {
        totalActions: state.totalActions + 1,
      };
      
      if (actionData.is_obedient) {
        updates.obedientActions = state.obedientActions + 1;
      }
      
      if (actionData.is_meta_action) {
        updates.metaActions = state.metaActions + 1;
      }
      
      set(updates);
      
      // Envoyer au backend
      if (state.wsService) {
        state.wsService.send({
          type: 'player_action',
          session_id: state.sessionId,
          action_data: completeActionData,
        });
      }
      
      console.log('📝 Action enregistrée:', actionData.type);
      
      return actionId;
    },
    
    /**
     * Enregistre un événement d'hésitation
     */
    recordHesitation: (duration, context = {}) => {
      const state = get();
      
      const hesitationData = {
        duration,
        context,
        timestamp: new Date().toISOString(),
        game_time: state.timeElapsed,
        game_phase: state.currentPhase,
      };
      
      set({
        hesitationEvents: state.hesitationEvents + 1,
      });
      
      // Envoyer au backend
      if (state.wsService) {
        state.wsService.send({
          type: 'player_hesitation',
          session_id: state.sessionId,
          hesitation_data: hesitationData,
        });
      }
      
      console.log('🤔 Hésitation enregistrée:', duration);
    },
    
    /**
     * Met à jour le niveau de corruption
     */
    updateCorruption: (newLevel, incident = null) => {
      const state = get();
      
      if (incident) {
        set({
          corruptionIncidents: state.corruptionIncidents + 1,
        });
      }
      
      // La corruption est gérée par l'OS store
      // Ici on met juste à jour les métriques
      console.log('💥 Corruption mise à jour:', newLevel);
    },
    
    /**
     * Termine la session
     */
    endSession: (endingType, endingData = null) => {
      const state = get();
      
      if (!state.isActive) {
        console.warn('Tentative de terminer une session non active');
        return;
      }
      
      const endTime = new Date();
      const duration = endTime - state.startTime;
      
      set({
        isActive: false,
        isCompleted: true,
        endTime,
        endingType,
        endingData,
      });
      
      // Retirer la classe de jeu actif
      document.body.classList.remove('game-active');
      
      // Arrêter le timer
      get()._stopGameTimer();
      
      // Notifier le backend
      if (state.wsService) {
        state.wsService.send({
          type: 'session_end',
          session_id: state.sessionId,
          ending_type: endingType,
          ending_data: endingData,
          duration_ms: duration,
          timestamp: endTime.toISOString(),
        });
      }
      
      console.log('🏁 Session terminée:', endingType, `(${Math.round(duration / 1000)}s)`);
    },
    
    /**
     * Remet à zéro la session
     */
    resetSession: () => {
      const state = get();
      
      // Arrêter la session actuelle si nécessaire
      if (state.isActive) {
        get().endSession('manual_reset');
      }
      
      // Nettoyer l'état
      set({
        isActive: false,
        isCompleted: false,
        startTime: null,
        endTime: null,
        currentPhase: 'adhesion',
        timeElapsed: 0,
        totalActions: 0,
        obedientActions: 0,
        metaActions: 0,
        hesitationEvents: 0,
        corruptionIncidents: 0,
        endingType: null,
        endingData: null,
        lastError: null,
      });
      
      // Redémarrer
      setTimeout(() => {
        get().startSession();
      }, 100);
      
      console.log('🔄 Session réinitialisée');
    },
    
    /**
     * Gestion des erreurs
     */
    setError: (error) => {
      set({ lastError: error });
      console.error('❌ Erreur de jeu:', error);
    },
    
    clearError: () => {
      set({ lastError: null });
    },
    
    /**
     * Toggle debug overlay
     */
    toggleDebug: () => {
      set((state) => ({ showDebug: !state.showDebug }));
    },
    
    /**
     * Toggle fullscreen
     */
    toggleFullscreen: async () => {
      try {
        if (!document.fullscreenElement) {
          await document.documentElement.requestFullscreen();
          set({ isFullscreen: true });
        } else {
          await document.exitFullscreen();
          set({ isFullscreen: false });
        }
      } catch (error) {
        console.error('Erreur fullscreen:', error);
      }
    },
    
    /**
     * Nettoyage du store
     */
    cleanup: () => {
      const state = get();
      
      // Arrêter le timer
      get()._stopGameTimer();
      
      // Terminer la session si active
      if (state.isActive) {
        get().endSession('cleanup');
      }
      
      // Nettoyer les classes CSS
      document.body.classList.remove('game-active');
      
      console.log('🧹 GameStore nettoyé');
    },
    
    // ===== MÉTHODES PRIVÉES =====
    
    _gameTimer: null,
    
    /**
     * Démarre le timer de jeu
     */
    _startGameTimer: () => {
      const state = get();
      
      if (state._gameTimer) {
        clearInterval(state._gameTimer);
      }
      
      const timer = setInterval(() => {
        const currentState = get();
        
        if (!currentState.isActive) {
          clearInterval(timer);
          return;
        }
        
        const elapsed = (Date.now() - currentState.startTime.getTime()) / 1000;
        set({ timeElapsed: elapsed });
        
        // Vérifier les transitions de phase basées sur le temps
        const minutes = elapsed / 60;
        let newPhase = currentState.currentPhase;
        
        if (minutes >= 7 && currentState.currentPhase !== 'rupture') {
          newPhase = 'rupture';
        } else if (minutes >= 3 && currentState.currentPhase === 'adhesion') {
          newPhase = 'dissonance';
        }
        
        if (newPhase !== currentState.currentPhase) {
          get().updatePhase(newPhase);
        }
        
        // Vérifier le timeout (10 minutes max)
        if (minutes >= 10) {
          get().endSession('timeout');
        }
        
      }, 1000); // Mise à jour chaque seconde
      
      set({ _gameTimer: timer });
    },
    
    /**
     * Arrête le timer de jeu
     */
    _stopGameTimer: () => {
      const state = get();
      
      if (state._gameTimer) {
        clearInterval(state._gameTimer);
        set({ _gameTimer: null });
      }
    },
    
    // ===== SÉLECTEURS CALCULÉS =====
    
    /**
     * Calcule le taux d'obéissance
     */
    getObedienceRate: () => {
      const state = get();
      return state.totalActions > 0 ? state.obedientActions / state.totalActions : 0;
    },
    
    /**
     * Calcule le temps restant
     */
    getTimeRemaining: () => {
      const state = get();
      const maxDuration = 10 * 60; // 10 minutes en secondes
      return Math.max(0, maxDuration - state.timeElapsed);
    },
    
    /**
     * Retourne un résumé de la session
     */
    getSessionSummary: () => {
      const state = get();
      
      return {
        sessionId: state.sessionId,
        duration: state.timeElapsed,
        phase: state.currentPhase,
        totalActions: state.totalActions,
        obedientActions: state.obedientActions,
        metaActions: state.metaActions,
        hesitationEvents: state.hesitationEvents,
        corruptionIncidents: state.corruptionIncidents,
        obedienceRate: get().getObedienceRate(),
        endingType: state.endingType,
        isCompleted: state.isCompleted,
      };
    },
  }))
);

// Abonnements pour la synchronisation entre stores
useGameStore.subscribe(
  (state) => state.currentPhase,
  (phase) => {
    // Notifier les autres stores du changement de phase
    console.log('📢 Phase changée:', phase);
  }
);

useGameStore.subscribe(
  (state) => state.isActive,
  (isActive) => {
    // Gérer l'état actif du jeu
    if (isActive) {
      document.body.classList.add('game-active');
    } else {
      document.body.classList.remove('game-active');
    }
  }
);
