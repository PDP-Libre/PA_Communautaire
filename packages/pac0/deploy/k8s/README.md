# déploiement kubernetes pac0

ATTENTION: Ce déploiement est orienté développement et non pas production !
A chaque lancement d'un pod, **les sources et les dépendances sont téléchargées**.

Pré-requis:
* un cluster k8s fonctionnel
* un client kubectl configuré

A faire une seule fois:
```shell
# Namespace où déployer l'application
export NAMESPACE=pac01
kubectl create namespace $NAMESPACE
```


A faire à chaque déploiement:
```shell
# Namespace où déployer l'application
export NAMESPACE=pac01
cd packages/pac0/deploy/k8s/
# Déploiement d'un seul service (03-controle-formats)
kubectl apply -n $NAMESPACE -f deploy_03-controle-formats.yam
# Déploiement complet 
kubectl apply -n $NAMESPACE -f 
```

Utiliser `k9s` pour pouvoir simplement gérer les services
(redémarrage, accès aux logs, accès à une console).


## Déploiement sur document.legal

**arundo.tech** fourni gracieusement 4 déploiements pac0 sur son cluster de développement.
Les entrées DNS pré-définis avec certificats *let's encrypt* sont:
- `pac01.document.legal` (namespace k8s: `pac01`)
- `pac02.document.legal` (namespace k8s: `pac02`)
- `pac03.document.legal` (namespace k8s: `pac03`)
- `pac04.document.legal` (namespace k8s: `pac04`)
