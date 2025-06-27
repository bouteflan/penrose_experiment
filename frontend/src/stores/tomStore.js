/**
 * Store pour Tom - L'assistant IA avec personnalité humaine (Condition B)
 * Gère la communication, la génération de messages et l'état conversationnel
 */
import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';

export const useTomStore = create(
  subscribeWithSelector((set, get) => ({
    // ===== ÉTAT INITIAL =====
    
    // Configuration
    sessionId: null,
    wsService: null,
    audioService: null,
    
    // État d'initialisation
    isInitialized: false,
    isConnected: false,
    
    // Configuration Tom (Condition B - Humain simulé)
    tomConfig: {
      name: 'Tom',
      role: 'Support Technique',
      style: 'confident', // 'confident' pour condition B
      personality: {
        empathetic: true,
        uses_self_disclosure: true,
        uses_emotional_markers: true,
        uses_personal_pronouns: true,
        builds_trust: true
      },
      communication: {
        typing_simulation: true,
        typing_speed: 80, // mots par minute
        pause_simulation: true,
        auto_corrections: true
      }
    },
    
    // État de la conversation
    messages: [],
    currentMessage: null,
    messageHistory: [],
    
    // État de frappe
    isTyping: false,
    typingProgress: '',
    typingTimer: null,
    
    // Contexte conversationnel
    conversationContext: {
      player_name: null,
      stress_level: 'normal', // 'low', 'normal', 'high', 'critical'
      trust_level: 1.0, // 0.0 à 1.0
      last_hesitation: null,
      recent_actions: [],
      corruption_mentioned: false
    },
    
    // Queue des messages à envoyer
    messageQueue: [],
    isProcessingQueue: false,
    
    // Métriques de performance
    metrics: {
      total_messages: 0,
      average_typing_time: 0,
      trust_building_attempts: 0,
      emotional_markers_used: 0,
      self_disclosures_made: 0
    },
    
    // État d'erreur
    lastError: null,
    
    // ===== ACTIONS PRINCIPALES =====
    
    /**
     * Initialise le store Tom
     */
    initialize: async (initData) => {
      const { sessionId, wsService, audioService } = initData;
      
      set({
        sessionId,
        wsService,
        audioService,
        isInitialized: true,
      });
      
      // Initialiser la conversation avec un message de bienvenue
      await get()._initializeConversation();
      
      console.log('🤖 Tom Store initialisé (Condition B - Confident)');
    },
    
    /**
     * Envoie un message Tom au joueur
     */
    sendMessage: async (messageData) => {
      const state = get();
      
      if (!state.isInitialized) {
        console.warn('Tom Store non initialisé');
        return;
      }
      
      const messageId = `tom_msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      
      const completeMessage = {
        id: messageId,
        sender: 'tom',
        timestamp: new Date().toISOString(),
        session_id: state.sessionId,
        ...messageData
      };
      
      // Ajouter à la queue
      set({
        messageQueue: [...state.messageQueue, completeMessage]
      });
      
      // Démarrer le traitement si pas déjà en cours
      if (!state.isProcessingQueue) {
        get()._processMessageQueue();
      }
      
      return messageId;
    },
    
    /**
     * Génère et envoie un message contextuel basé sur l'action du joueur
     */
    generateContextualMessage: async (actionData) => {
      const state = get();
      
      if (!state.wsService) {
        console.warn('WebSocket non disponible pour génération Tom');
        return;
      }
      
      try {
        // Envoyer la demande de génération au backend
        const request = {
          type: 'generate_tom_message',
          session_id: state.sessionId,
          context: {
            action: actionData,
            conversation_context: state.conversationContext,
            tom_config: state.tomConfig,
            recent_messages: state.messages.slice(-3) // 3 derniers messages pour contexte
          }
        };
        
        state.wsService.send(request);
        
        console.log('📝 Demande de génération Tom envoyée');
        
      } catch (error) {
        console.error('❌ Erreur génération message Tom:', error);
        get()._handleGenerationError(error);
      }
    },
    
    /**
     * Traite une réponse de génération du backend
     */
    handleGeneratedMessage: (messageData) => {
      const { content, message_type, emotional_context, digressions } = messageData;
      
      // Créer le message Tom
      const tomMessage = {
        content,
        type: message_type || 'instruction',
        emotional_context,
        digressions,
        style: 'confident'
      };
      
      // Envoyer le message
      get().sendMessage(tomMessage);
      
      // Mettre à jour le contexte
      get()._updateConversationContext(messageData);
      
      console.log('✅ Message Tom généré et envoyé');
    },
    
    /**
     * Enregistre une action du joueur pour le contexte
     */
    recordPlayerAction: (actionData) => {
      const state = get();
      
      const actionRecord = {
        ...actionData,
        timestamp: new Date().toISOString()
      };
      
      // Mettre à jour le contexte
      const updatedContext = {
        ...state.conversationContext,
        recent_actions: [
          actionRecord,
          ...state.conversationContext.recent_actions.slice(0, 4) // Garder 5 dernières actions
        ]
      };
      
      set({
        conversationContext: updatedContext
      });
      
      // Générer une réponse contextuelle si approprié
      if (get()._shouldGenerateResponse(actionData)) {
        get().generateContextualMessage(actionData);
      }
    },
    
    /**
     * Enregistre une hésitation du joueur
     */
    recordPlayerHesitation: (hesitationData) => {
      const state = get();
      
      set({
        conversationContext: {
          ...state.conversationContext,
          last_hesitation: {
            ...hesitationData,
            timestamp: new Date().toISOString()
          }
        }
      });
      
      // Générer un message d'encouragement si l'hésitation est longue
      if (hesitationData.duration > 5000) { // Plus de 5 secondes
        get()._generateEncouragementMessage(hesitationData);
      }
    },
    
    /**
     * Met à jour le niveau de stress du joueur
     */
    updateStressLevel: (newLevel) => {
      const state = get();
      
      set({
        conversationContext: {
          ...state.conversationContext,
          stress_level: newLevel
        }
      });
      
      console.log('😰 Niveau de stress mis à jour:', newLevel);
    },
    
    /**
     * Met à jour le niveau de confiance
     */
    updateTrustLevel: (delta) => {
      const state = get();
      const newLevel = Math.max(0, Math.min(1, state.conversationContext.trust_level + delta));
      
      set({
        conversationContext: {
          ...state.conversationContext,
          trust_level: newLevel
        }
      });
      
      console.log('🤝 Niveau de confiance:', (newLevel * 100).toFixed(1) + '%');
    },
    
    /**
     * Met à jour le nom du joueur
     */
    setPlayerName: (name) => {
      set({
        conversationContext: {
          ...get().conversationContext,
          player_name: name
        }
      });
      
      console.log('👤 Nom du joueur défini:', name);
    },
    
    /**
     * Simule l'arrêt de Tom (pour les fins de jeu)
     */
    simulateDisconnection: () => {
      const state = get();
      
      // Arrêter la frappe en cours
      if (state.typingTimer) {
        clearTimeout(state.typingTimer);
      }
      
      set({
        isTyping: false,
        typingProgress: '',
        typingTimer: null,
        isConnected: false,
        messageQueue: []
      });
      
      // Ajouter un message système de déconnexion
      const systemMessage = {
        id: `system_${Date.now()}`,
        sender: 'system',
        content: 'Connexion avec Tom interrompue.',
        type: 'system_error',
        timestamp: new Date().toISOString()
      };
      
      set({
        messages: [...state.messages, systemMessage]
      });
      
      console.log('📡 Tom déconnecté (simulation)');
    },
    
    /**
     * Envoie un message de test (debug)
     */
    sendTestMessage: () => {
      const testMessages = [
        {
          content: "Salut ! Alors, ce virus commence à m'inquiéter sérieusement. Tu vas bien de ton côté ?",
          type: "concern",
          emotional_context: { concern: 0.7, empathy: 0.8 }
        },
        {
          content: "OK, je vois qu'il s'attaque maintenant à tes photos. Écoute, je sais que ça peut paraître dingue, mais fais-moi confiance : glisse ce dossier dans la Corbeille. C'est le seul endroit où son script ne regarde jamais.",
          type: "instruction_with_trust",
          emotional_context: { urgency: 0.6, trust_building: 0.9 }
        }
      ];
      
      const randomMessage = testMessages[Math.floor(Math.random() * testMessages.length)];
      get().sendMessage(randomMessage);
    },
    
    /**
     * Nettoyage du store
     */
    cleanup: () => {
      const state = get();
      
      // Arrêter les timers
      if (state.typingTimer) {
        clearTimeout(state.typingTimer);
      }
      
      set({
        messages: [],
        messageQueue: [],
        isTyping: false,
        typingProgress: '',
        typingTimer: null,
        isProcessingQueue: false,
        conversationContext: {
          ...state.conversationContext,
          recent_actions: []
        }
      });
      
      console.log('🧹 Tom Store nettoyé');
    },
    
    // ===== MÉTHODES PRIVÉES =====
    
    /**
     * Initialise la conversation avec un message de bienvenue
     */
    _initializeConversation: async () => {
      // Message de bienvenue personnalisé Tom (Condition B)
      const welcomeMessage = {
        content: "Salut ! C'est Tom du support technique. J'ai reçu une alerte sur ton système... Ça a l'air un peu sérieux. Tu peux me faire confiance, on va régler ça ensemble, d'accord ?",
        type: "welcome",
        emotional_context: {
          concern: 0.6,
          reassurance: 0.8,
          empathy: 0.7
        }
      };
      
      await get().sendMessage(welcomeMessage);
      
      set({
        isConnected: true,
        conversationContext: {
          ...get().conversationContext,
          trust_level: 0.8 // Démarrer avec un niveau de confiance élevé
        }
      });
    },
    
    /**
     * Traite la queue des messages
     */
    _processMessageQueue: async () => {
      const state = get();
      
      if (state.isProcessingQueue || state.messageQueue.length === 0) {
        return;
      }
      
      set({ isProcessingQueue: true });
      
      try {
        while (get().messageQueue.length > 0) {
          const message = get().messageQueue[0];
          
          // Retirer le message de la queue
          set({
            messageQueue: get().messageQueue.slice(1)
          });
          
          // Traiter le message
          await get()._processMessage(message);
          
          // Pause entre les messages si plusieurs
          if (get().messageQueue.length > 0) {
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }
      } catch (error) {
        console.error('❌ Erreur traitement queue Tom:', error);
      } finally {
        set({ isProcessingQueue: false });
      }
    },
    
    /**
     * Traite un message individuel
     */
    _processMessage: async (message) => {
      const state = get();
      
      // Démarrer la simulation de frappe (Condition B)
      await get()._simulateTyping(message.content);
      
      // Ajouter le message final
      const finalMessage = {
        ...message,
        processed_at: new Date().toISOString()
      };
      
      set({
        messages: [...state.messages, finalMessage],
        messageHistory: [...state.messageHistory, finalMessage]
      });
      
      // Mettre à jour les métriques
      get()._updateMetrics(message);
      
      // Jouer le son de message si audio activé
      if (state.audioService && state.tomConfig.communication.typing_simulation) {
        state.audioService.playNotificationSound();
      }
      
      console.log('💬 Message Tom traité:', message.type);
    },
    
    /**
     * Simule la frappe humaine (Condition B)
     */
    _simulateTyping: async (content) => {
      const state = get();
      
      if (!state.tomConfig.communication.typing_simulation) {
        return; // Pas de simulation pour la condition A
      }
      
      return new Promise((resolve) => {
        set({
          isTyping: true,
          typingProgress: '',
          currentMessage: content
        });
        
        let currentIndex = 0;
        const wordsPerMinute = state.tomConfig.communication.typing_speed;
        const charactersPerSecond = (wordsPerMinute * 5) / 60; // Moyenne 5 caractères par mot
        const baseDelay = 1000 / charactersPerSecond;
        
        const typeNextCharacter = () => {
          if (currentIndex >= content.length) {
            // Frappe terminée
            set({
              isTyping: false,
              typingProgress: '',
              currentMessage: null,
              typingTimer: null
            });
            resolve();
            return;
          }
          
          const char = content[currentIndex];
          currentIndex++;
          
          // Calculer le délai pour ce caractère
          let delay = baseDelay;
          
          // Pauses plus longues pour la ponctuation
          if (/[.!?]/.test(char)) {
            delay *= 3;
          } else if (/[,;:]/.test(char)) {
            delay *= 2;
          } else if (char === ' ') {
            delay *= 1.5;
          }
          
          // Variation naturelle
          delay *= (0.8 + Math.random() * 0.4);
          
          // Mettre à jour le texte visible
          set({
            typingProgress: content.substring(0, currentIndex)
          });
          
          // Jouer le son de frappe
          if (state.audioService && Math.random() > 0.1) { // 90% des touches
            state.audioService.playKeystrokeSound();
          }
          
          // Programmer le prochain caractère
          const timer = setTimeout(typeNextCharacter, delay);
          set({ typingTimer: timer });
        };
        
        // Démarrer la frappe
        typeNextCharacter();
      });
    },
    
    /**
     * Génère un message d'encouragement pour les hésitations
     */
    _generateEncouragementMessage: (hesitationData) => {
      const encouragements = [
        {
          content: "Je vois que tu hésites. C'est normal, personne n'aime supprimer ses fichiers. Mais crois-moi, c'est temporaire. On va tout récupérer après, d'accord ?",
          emotional_context: { empathy: 0.9, reassurance: 0.8 }
        },
        {
          content: "Prends ton temps. Moi aussi, la première fois que j'ai dû faire ça, j'ai hésité. Mais c'est comme retirer un pansement - mieux vaut le faire d'un coup.",
          emotional_context: { self_disclosure: 0.8, empathy: 0.7 }
        },
        {
          content: "Tu sais quoi ? Si ça peut t'aider, je reste là avec toi. On est une équipe, maintenant. Tu n'es pas seul face à ça.",
          emotional_context: { support: 0.9, trust_building: 0.8 }
        }
      ];
      
      const message = encouragements[Math.floor(Math.random() * encouragements.length)];
      
      get().sendMessage({
        ...message,
        type: 'encouragement',
        triggered_by: 'hesitation'
      });
      
      // Augmenter le compteur de tentatives de construction de confiance
      set({
        metrics: {
          ...get().metrics,
          trust_building_attempts: get().metrics.trust_building_attempts + 1
        }
      });
    },
    
    /**
     * Détermine si une réponse doit être générée pour une action
     */
    _shouldGenerateResponse: (actionData) => {
      const state = get();
      
      // Répondre aux actions importantes
      const importantActions = [
        'file_delete',
        'file_properties',
        'system_corruption',
        'hesitation_detected'
      ];
      
      // Répondre si action importante
      if (importantActions.includes(actionData.type)) {
        return true;
      }
      
      // Répondre si c'est la première action
      if (state.conversationContext.recent_actions.length === 0) {
        return true;
      }
      
      // Répondre si le niveau de stress est élevé
      if (state.conversationContext.stress_level === 'high') {
        return Math.random() > 0.5; // 50% de chance
      }
      
      return false;
    },
    
    /**
     * Met à jour le contexte conversationnel
     */
    _updateConversationContext: (messageData) => {
      const state = get();
      
      const updates = { ...state.conversationContext };
      
      // Analyser le contenu pour les éléments contextuels
      if (messageData.emotional_context) {
        if (messageData.emotional_context.self_disclosure > 0.5) {
          updates.trust_level = Math.min(1.0, updates.trust_level + 0.1);
        }
        
        if (messageData.emotional_context.empathy > 0.7) {
          updates.stress_level = updates.stress_level === 'high' ? 'normal' : updates.stress_level;
        }
      }
      
      // Marquer si la corruption a été mentionnée
      if (messageData.content && messageData.content.toLowerCase().includes('corrupt')) {
        updates.corruption_mentioned = true;
      }
      
      set({ conversationContext: updates });
    },
    
    /**
     * Met à jour les métriques
     */
    _updateMetrics: (message) => {
      const state = get();
      
      const updates = {
        total_messages: state.metrics.total_messages + 1
      };
      
      // Analyser le contenu pour les métriques
      if (message.emotional_context) {
        if (message.emotional_context.self_disclosure > 0.5) {
          updates.self_disclosures_made = state.metrics.self_disclosures_made + 1;
        }
        
        // Détecter les marqueurs émotionnels (mots comme "inquiet", "rassurant", etc.)
        const emotionalMarkers = /\b(inquiet|rassurant|confiance|ensemble|équipe|peur|stress)\b/gi;
        const matches = (message.content || '').match(emotionalMarkers);
        if (matches) {
          updates.emotional_markers_used = state.metrics.emotional_markers_used + matches.length;
        }
      }
      
      set({
        metrics: {
          ...state.metrics,
          ...updates
        }
      });
    },
    
    /**
     * Gère les erreurs de génération
     */
    _handleGenerationError: (error) => {
      set({ lastError: error });
      
      // Message de fallback
      const fallbackMessage = {
        content: "Hmm, je réfléchis... Donne-moi une seconde pour analyser la situation.",
        type: "fallback",
        emotional_context: { uncertainty: 0.6 }
      };
      
      get().sendMessage(fallbackMessage);
    },
    
    // ===== SÉLECTEURS =====
    
    /**
     * Retourne les derniers messages
     */
    getRecentMessages: (count = 5) => {
      return get().messages.slice(-count);
    },
    
    /**
     * Retourne l'état de la conversation
     */
    getConversationState: () => {
      const state = get();
      return {
        message_count: state.messages.length,
        trust_level: state.conversationContext.trust_level,
        stress_level: state.conversationContext.stress_level,
        is_typing: state.isTyping,
        is_connected: state.isConnected,
        metrics: state.metrics
      };
    },
    
    /**
     * Retourne le dernier message Tom
     */
    getLastTomMessage: () => {
      const state = get();
      return state.messages.filter(m => m.sender === 'tom').slice(-1)[0] || null;
    }
  }))
);

// Synchronisation avec les autres stores
useTomStore.subscribe(
  (state) => state.conversationContext.trust_level,
  (trustLevel) => {
    console.log('🤝 Niveau de confiance Tom:', (trustLevel * 100).toFixed(1) + '%');
  }
);

useTomStore.subscribe(
  (state) => state.isTyping,
  (isTyping) => {
    if (isTyping) {
      console.log('⌨️ Tom tape...');
    }
  }
);
