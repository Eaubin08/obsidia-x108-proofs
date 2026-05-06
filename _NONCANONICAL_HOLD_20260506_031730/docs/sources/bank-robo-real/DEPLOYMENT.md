# Déploiement sur Manus

## 🌐 URL de Production

**Application en direct** : [https://3000-ip5ied8cvspm6oruxykv7-bff6e46a.us2.manus.computer](https://3000-ip5ied8cvspm6oruxykv7-bff6e46a.us2.manus.computer)

---

## 🏗️ Architecture

- **Frontend** : React 19 + Vite + Tailwind CSS 4
- **Backend** : Express 4 + tRPC 11
- **Database** : MySQL/TiDB (géré par Manus)
- **IA** : Gemini AI (intégration via Manus LLM helpers)
- **Plateforme** : Manus Space (hébergement complet)

---

## 📦 Stack Technique

### Frontend
- **React 19** : Framework UI moderne avec hooks
- **Tailwind CSS 4** : Styling utility-first
- **Chart.js** : Visualisations interactives
- **tRPC Client** : Type-safe API calls

### Backend
- **Express 4** : Serveur Node.js
- **tRPC 11** : API type-safe end-to-end
- **Drizzle ORM** : Gestion de base de données
- **Gemini AI** : Analyse intelligente des transactions

### Base de Données
- **MySQL/TiDB** : Base relationnelle gérée
- **Tables** :
  - `users` : Utilisateurs et authentification
  - `transactions` : Historique des transactions
  - `sessions` : Sessions de simulation

---

## 🚀 Instructions de Déploiement

### 1. Push sur GitHub
```bash
git add .
git commit -m "Update: Description des changements"
git push origin main
```

### 2. Déploiement Automatique
- Manus détecte automatiquement les changements sur la branche `main`
- Le build et le déploiement se font automatiquement
- Temps de déploiement : ~2-3 minutes

### 3. Vérification
- Accéder à l'URL de production
- Tester les fonctionnalités principales
- Vérifier les logs dans le dashboard Manus

---

## 🔧 Configuration

### Variables d'Environnement (Auto-injectées par Manus)
- `DATABASE_URL` : Connexion MySQL/TiDB
- `JWT_SECRET` : Secret pour sessions
- `BUILT_IN_FORGE_API_KEY` : Clé API Gemini (backend)
- `VITE_FRONTEND_FORGE_API_KEY` : Clé API Gemini (frontend)
- `VITE_APP_TITLE` : Titre de l'application
- `VITE_APP_LOGO` : Logo de l'application

### Ports
- **Dev** : 3000 (local)
- **Prod** : Géré automatiquement par Manus

---

## 📊 Monitoring

### Dashboard Manus
- **Status** : État du serveur (running/stopped)
- **Logs** : Logs en temps réel
- **Analytics** : UV/PV pour les sites publiés
- **Database** : Interface CRUD pour la base de données

### Logs Disponibles
- `.manus-logs/devserver.log` : Logs du serveur
- `.manus-logs/browserConsole.log` : Logs du navigateur
- `.manus-logs/networkRequests.log` : Requêtes HTTP
- `.manus-logs/sessionReplay.log` : Interactions utilisateur

---

## 🔄 Workflow de Mise à Jour

1. **Développement Local**
   ```bash
   pnpm dev  # Lance le serveur de développement
   ```

2. **Tests**
   ```bash
   pnpm test  # Exécute les tests unitaires
   pnpm check  # Vérifie les types TypeScript
   ```

3. **Build**
   ```bash
   pnpm build  # Build pour production
   ```

4. **Déploiement**
   ```bash
   git push origin main  # Push sur GitHub
   # Manus déploie automatiquement
   ```

---

## 🎯 Checkpoints

Manus utilise un système de checkpoints pour sauvegarder l'état du projet :

- **Créer un checkpoint** : Via l'interface Manus ou `webdev_save_checkpoint`
- **Rollback** : Restaurer un checkpoint précédent si nécessaire
- **Publish** : Publier un checkpoint pour le rendre accessible publiquement

---

## 🔐 Sécurité

- **HTTPS** : Activé automatiquement
- **Authentification** : Manus OAuth intégré
- **Secrets** : Gérés via l'interface Manus (jamais commités)
- **CORS** : Configuré automatiquement

---

## 📈 Performance

- **CDN** : Assets statiques servis via CDN
- **Compression** : Gzip/Brotli activé
- **Cache** : Headers de cache optimisés
- **SSR** : Non utilisé (SPA React)

---

## 🐛 Dépannage

### Le serveur ne démarre pas
- Vérifier les logs dans `.manus-logs/devserver.log`
- Vérifier que les dépendances sont installées (`pnpm install`)
- Redémarrer le serveur via l'interface Manus

### Erreurs de base de données
- Vérifier la connexion dans le dashboard Manus
- Exécuter les migrations : `pnpm db:push`
- Vérifier les logs SQL

### Erreurs TypeScript
- Exécuter `pnpm check` pour voir les erreurs
- Vérifier que les types sont à jour
- Redémarrer le serveur

---

## 📞 Support

- **Documentation Manus** : [https://help.manus.im](https://help.manus.im)
- **Repository GitHub** : [https://github.com/Eaubin08/bank-robo](https://github.com/Eaubin08/bank-robo)
- **Hackathon** : Launch Fund AI × Robotics (lablab.ai)

---

## 🎉 Prochaines Étapes

1. ✅ Application déployée sur Manus
2. ⏳ Créer vidéo de démo (2-3 minutes)
3. ⏳ Poster sur X/Twitter avec tags @lablabai @Surgexyz_
4. ⏳ Soumettre sur lablab.ai
5. ⏳ Présenter au jury

---

**Dernière mise à jour** : 11 février 2026  
**Version** : 1.0.0  
**Statut** : ✅ Production Ready
