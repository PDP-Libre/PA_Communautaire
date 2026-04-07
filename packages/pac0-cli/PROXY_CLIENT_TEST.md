# Proxy Client Test Command

La commande `pac0 test proxy-client` génère des requêtes API aléatoires pour tester un endpoint proxy ou serveur.

## Utilisation

```bash
# Commande de base
pac0 test proxy-client [ENDPOINT]

# Avec options CLI
pac0 test proxy-client https://api.example.com/endpoint \
  --num-requests 100 \
  --num-parallel 10 \
  --avg-size 2048 \
  --stdev-size 200 \
  --jwt-token "votre-jwt-token"

# Avec fichier de configuration YAML
pac0 test proxy-client -c config.yaml
```

## Arguments

| Argument | Description | Défaut |
|----------|-------------|--------|
| `endpoint` | URL de l'endpoint à tester | `https://httpbin.org/post` |

## Options

| Option | Description | Défaut |
|--------|-------------|--------|
| `--num-requests` | Nombre total de requêtes à envoyer | `10` |
| `--num-parallel` | Nombre de requêtes parallèles | `5` |
| `--avg-size` | Taille moyenne du payload en octets | `1024` |
| `--stdev-size` | Écart-type de la taille du payload | `100` |
| `--jwt-token` | Token JWT pour l'authentification (optionnel) | `""` |
| `--config, -c` | Chemin vers un fichier YAML de configuration | `None` |

## Format du fichier YAML

```yaml
endpoint: https://api.example.com/endpoint
num_requests: 100
num_parallel: 10
avg_payload_size: 2048
stdev_payload_size: 200
jwt_token: "votre-jwt-token"
```

## Sortie

La commande affiche:
1. **Progress en temps réel** avec `tqdm` montrant l'avancement des requêtes
2. **Rapport de statistiques** à la fin comprenant:
   - Nombre total de requêtes, succès/échecs
   - Taille des données envoyées/reçues
   - Durées totales et moyennes
   - Percentiles (P50, P90, P95, P99)
   - Répartition des codes de statut HTTP

## Exemple de sortie

```
======================================================================
TEST PROXY CLIENT
======================================================================

🎯 Endpoint: https://httpbin.org/post
📋 Requêtes: 10
🔀 Parallélisme: 3
📦 Payload: ~1024±100 octets
🔐 JWT: [MASKED]


Requêtes: 100%|██████████| 10/10 [00:03<00:00,  3.12it/s]

======================================================================
RAPPORT DE STATISTIQUES - TEST PROXY CLIENT
======================================================================

📊 Résumé des requêtes:
   Total:        10
   Succès:       10 (100.0%)
   Échecs:       0 (0.0%)

💾 Taille des données:
   Envoyé:       9.77 KB
   Reçu:         24.56 KB

⏱️  Durée:
   Total:        3.21s
   Moyen:        0.321s

📈 Percentiles de durée:
   P50:         0.285s
   P90:         0.412s
   P95:         0.438s
   P99:         0.451s

🔢 Codes de statut:
   200: 10 (100.0%)

======================================================================
```

## Technologies utilisées

- **httpx**: Client HTTP asynchrone
- **tqdm**: Barre de progression
- **typer**: CLI framework
- **PyYAML**: Parsing de fichiers YAML

## Notes

- Les requêtes sont asynchrones et peuvent être exécutées en parallèle
- Le payload est généré aléatoirement avec une taille gaussienne (moyenne ± écart-type)
- Un token JWT optionnel peut être fourni pour l'authentification
- Les codes 2xx et 3xx sont considérés comme des succès
