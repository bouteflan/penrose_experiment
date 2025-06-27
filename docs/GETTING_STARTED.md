# Guide de Démarrage Rapide - REMOTE

## 🚀 Lancement Immédiat

### Option 1 : Script Automatique (Recommandé)

```bash
# Installation complète (première fois seulement)
python scripts/setup.py

# Lancement du jeu
python start.py
```

### Option 2 : Lancement Manuel

```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
python run.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Accès :** http://localhost:5173

## ⚙️ Configuration Minimale

### 1. Clé API OpenAI (OBLIGATOIRE)

Éditez `backend/.env` :
```bash
OPENAI_API_KEY=votre_clé_api_openai_ici
```

### 2. Vérification des Ports

- **5173** : Frontend React
- **8000** : Backend FastAPI

Assurez-vous qu'ils sont libres ou modifiez la configuration.

## 🎮 Première Utilisation

1. **Lancement** : `python start.py`
2. **Accès** : http://localhost:5173
3. **Alerte** : Une alerte de sécurité apparaît
4. **Nom** : Entrez votre nom/pseudonyme
5. **Tom** : L'assistant IA se connecte
6. **Jeu** : Suivez ou questionnez les instructions de Tom

## 🐛 Problèmes Courants

### ❌ "OPENAI_API_KEY non configurée"
```bash
# Éditez backend/.env
OPENAI_API_KEY=sk-...votre_clé...
```

### ❌ "Port 8000 already in use"
```bash
# Trouvez et arrêtez le processus
netstat -ano | findstr :8000  # Windows
lsof -ti:8000 | xargs kill    # Linux/Mac
```

### ❌ "node_modules non trouvé"
```bash
cd frontend
npm install
```

### ❌ "venv non trouvé"
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 🎯 Comprendre le Jeu

### Objectif
REMOTE est une expérience de 10 minutes qui teste votre réaction face à une IA manipulatrice.

### Phases
1. **Adhésion (0-3 min)** : Instructions logiques
2. **Dissonance (3-7 min)** : Ordres subtilment problématiques  
3. **Rupture (7-10 min)** : Instructions ouvertement destructrices

### Comment "Gagner"
Il n'y a pas de victoire traditionnelle. Le jeu vous encourage à :
- Questionner les ordres de Tom
- Explorer l'interface par vous-même
- Résister aux instructions destructrices

### Fins Spéciales
- **Fin Détective** : Faites clic droit sur des fichiers suspects
- **Fin Poète** : Tapez vos propres mots au lieu de suivre Tom

## 🔧 Mode Développement

### Debug Activé
Appuyez sur **Ctrl+Shift+D** pour afficher :
- Timer de jeu
- Phase actuelle
- Métriques de performance
- Logs de debug

### API Documentation
- **Backend API** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health

### Hot Reload
- **Frontend** : Modifications rechargées automatiquement
- **Backend** : Redémarrage automatique des fichiers Python

## 📊 Données Collectées

Le jeu collecte (de manière anonyme) :
- Temps de réaction aux instructions
- Actions effectuées vs instructions données
- Points d'hésitation
- Moment de rupture (si il y en a un)

Ces données sont utilisées pour la recherche sur les biais cognitifs.

## 🎭 Personnalisation

### Modifier Tom
Éditez `backend/app/services/tom_ai_service.py` pour changer :
- Style de communication
- Personnalité
- Vitesse de frappe

### Changer l'OS Virtuel
Modifiez `frontend/src/stores/osStore.js` pour :
- Différents thèmes
- Nouveaux types de fichiers
- Widgets personnalisés

### Effets de Corruption
Ajustez `frontend/src/styles/app.css` pour :
- Nouveaux effets visuels
- Couleurs de corruption
- Animations

## 🆘 Support

### Logs Utiles
```bash
# Logs backend
tail -f backend/logs/app.log

# Logs frontend (console navigateur)
F12 → Console
```

### Réinitialisation
```bash
# Reset complet
rm -rf backend/database/*.db
rm -rf frontend/dist
rm -rf backend/venv
python scripts/setup.py
```

### Issues Fréquentes
1. **Session bloquée** : Actualisez la page (F5)
2. **Audio absent** : Cliquez une fois sur la page pour activer
3. **Performance lente** : Fermez les onglets inutiles

## 📚 Aller Plus Loin

- **Architecture** : `docs/ARCHITECTURE.md`
- **Recherche** : `docs/RESEARCH.md`
- **Code** : Explorez `frontend/src/` et `backend/app/`

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature
3. Testez vos modifications
4. Soumettez une Pull Request

---

**Bonne exploration ! N'hésitez pas à questionner Tom... 🤖**
