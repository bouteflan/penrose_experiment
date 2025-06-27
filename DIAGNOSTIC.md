# 🔍 DIAGNOSTIC REMOTE - Résolution des problèmes

## Problème identifié
Vous obtenez une page vide après l'écran de chargement "REMOTE".

## Solutions étape par étape

### 1. Démarrage rapide avec le diagnostic automatique

```bash
# Dans le répertoire remote-game
python diagnostic.py
```

### 2. Diagnostic manuel

#### Étape 1: Vérifier Node.js et npm
```bash
node --version    # Doit être >= 18.0.0
npm --version     # Doit être >= 9.0.0
```

Si pas installé : https://nodejs.org/

#### Étape 2: Installer les dépendances
```bash
cd frontend
npm install
```

#### Étape 3: Démarrer le mode diagnostic
```bash
npm run dev
```

#### Étape 4: Ouvrir dans le navigateur
- Aller sur http://localhost:5173
- Ouvrir la console du navigateur (F12)
- Vérifier les messages de diagnostic

### 3. Problèmes courants et solutions

#### ❌ "Module not found" ou erreurs d'import
**Solution :**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### ❌ Page blanche sans erreurs
**Solution :**
1. Ouvrir F12 dans le navigateur
2. Regarder l'onglet Console pour les erreurs JavaScript
3. Regarder l'onglet Network pour les erreurs de chargement

#### ❌ WebSocket connection failed
**Solution :**
1. Démarrer le backend :
```bash
cd backend
python run.py
```
2. Vérifier que le backend est accessible sur http://localhost:8000

#### ❌ Erreurs de compilation Vite
**Solution :**
```bash
cd frontend
npm run build  # Tester la compilation
```

### 4. Mode diagnostic avancé

Le projet a été configuré avec un mode diagnostic spécial :

1. **Fichiers de diagnostic créés :**
   - `frontend/src/App-debug.jsx` - Version simplifiée de l'app
   - `frontend/src/index-debug.jsx` - Point d'entrée de diagnostic
   - `frontend/index.html` - Version diagnostic

2. **Tests à effectuer :**
   - Ouvrir http://localhost:5173
   - Vérifier les messages dans la console
   - Tester chaque étape du diagnostic

### 5. Retour à la version normale

Une fois le problème identifié :

```bash
# Restaurer l'index.html original
cd frontend
mv index.html.backup index.html

# Modifier index.html pour utiliser index.jsx au lieu de index-debug.jsx
# Ligne 213: <script type="module" src="/src/index.jsx"></script>
```

### 6. Structure des logs attendus

**Dans la console du navigateur, vous devriez voir :**
```
🚀 index-debug.jsx : Démarrage du diagnostic REMOTE
📋 Configuration de diagnostic: {...}
🔍 Vérifications préliminaires:
⚛️ Création de la racine React...
📦 Rendu de l'application de diagnostic...
✅ Application de diagnostic démarrée avec succès
```

**Si vous voyez des erreurs :**
- Noter le message d'erreur exact
- Vérifier le stack trace
- Suivre les solutions correspondantes

### 7. Vérifications systématiques

#### Backend (optionnel mais recommandé)
```bash
curl http://localhost:8000/health
# Ou ouvrir dans le navigateur
```

#### Frontend
```bash
cd frontend
npm run build  # Test de compilation
npm run preview  # Test de la version build
```

### 8. Aide supplémentaire

Si le problème persiste :

1. **Copier les logs d'erreur** de la console du navigateur
2. **Vérifier les versions :**
   ```bash
   node --version
   npm --version
   python --version
   ```
3. **État des services :**
   - Backend : http://localhost:8000/health
   - Frontend : http://localhost:5173

### 9. Debug avancé avec les stores Zustand

Si l'application se charge mais reste vide, le problème vient probablement des stores :

1. **Dans la console du navigateur :**
```javascript
// Tester les stores
import('./src/stores/gameStore.js').then(console.log)
import('./src/stores/osStore.js').then(console.log)
import('./src/stores/tomStore.js').then(console.log)
```

2. **Ajouter des logs dans les stores :**
Modifier `gameStore.js`, `osStore.js`, `tomStore.js` pour ajouter :
```javascript
console.log('Store initialisé:', storeName);
```

### 10. Configuration WebSocket

Le problème peut venir de la connexion WebSocket :

**Test manuel :**
```javascript
// Dans la console du navigateur
const ws = new WebSocket('ws://localhost:8000/ws/test');
ws.onopen = () => console.log('WebSocket OK');
ws.onerror = (e) => console.log('WebSocket erreur:', e);
```

---

## Résumé rapide

1. `python diagnostic.py` (dans remote-game/)
2. Ouvrir http://localhost:5173 
3. Ouvrir F12 → Console
4. Suivre les messages de diagnostic
5. Appliquer les corrections suggérées

Le mode diagnostic vous guidera étape par étape pour identifier le problème exact.
