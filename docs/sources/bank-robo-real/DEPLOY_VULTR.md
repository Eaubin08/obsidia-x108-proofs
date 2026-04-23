# Guide de Déploiement Vultr - Bank Safety Lab

## Étape 1: Se connecter au serveur Vultr

Ouvrez un terminal (PowerShell, CMD, ou Terminal) et connectez-vous :

```bash
ssh root@45.32.151.185
```

Entrez votre mot de passe quand demandé.

## Étape 2: Mettre à jour le code depuis GitHub

Une fois connecté au serveur, exécutez ces commandes **une par une** :

```bash
# Aller dans le dossier du projet
cd /root/bank-robo

# Récupérer les dernières modifications depuis GitHub
git pull origin main

# Redémarrer l'application
pm2 restart bank-safety-lab
```

## Étape 3: Vérifier que ça fonctionne

Ouvrez votre navigateur et allez sur : http://45.32.151.185/

Vous devriez voir :
- ✅ Les boutons Batch (10/50/100/500) ont **disparu**
- ✅ Seulement 3 boutons de contrôle : Démarrer, Pause, Arrêter
- ✅ Les boutons de vitesse : Lent, Normal, Rapide, Ultra
- ✅ Le bouton Export CSV

## Problèmes courants

### Si `git pull` dit "Already up to date"

Cela signifie que le serveur pense qu'il a déjà la dernière version. Forcez la mise à jour :

```bash
cd /root/bank-robo
git fetch origin
git reset --hard origin/main
pm2 restart bank-safety-lab
```

### Si les boutons Batch sont toujours là après le redémarrage

Le cache du navigateur peut afficher l'ancienne version. Faites **Ctrl+Shift+R** (ou Cmd+Shift+R sur Mac) pour forcer le rechargement.

### Si PM2 ne redémarre pas

```bash
pm2 stop bank-safety-lab
pm2 start ecosystem.config.cjs
pm2 save
```

## Vérifier les logs en cas d'erreur

```bash
pm2 logs bank-safety-lab
```

Appuyez sur **Ctrl+C** pour quitter les logs.
