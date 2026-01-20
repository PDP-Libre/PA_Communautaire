## 🧪 Exécution des tests

Pour garantir un niveau de qualité élevé du code et s'assurer que le code continue de fonctionner comme prévue, nous avons mis en place des tests BDD - Behavior Driven Development.

Les BDD permettent à des développeurs mais aussi à des experts métiers de comprendre facilement le fonctionnement du projet. 

Pour exécuter tous les tests et générer des rapports:

```bash
./script/test
```

Cette commande exécute pytest dans les deux packages (`pac0` et `pac-bdd`) et génère des rapports dans le dossier `/report`:

| Package | Rapport MD |Rapport HTML | Rapport JUnit XML |
|---------|--------------|--------------|-------------------|
| pac0 | [report.md](report/pac0/report.md) | [report.html](report/pac0/report.html) | [report/pac0/report.xml](report/pac0/report.xml) |
| pac-bdd | [report.md](report/pac-bdd/report.md)| [report.html](report/pac-bdd/report.html) | [report/pac-bdd/report.xml](report/pac-bdd/report.xml) |

Pour exécuter les tests d'un seul package:

```bash
# Tests pac0
cd packages/pac0 && uv run pytest

# Tests pac-bdd
cd packages/pac-bdd && uv run pytest
```


Voir cet article : "Comment rédiger un test BDD ?"

Pour lancer les tests et vérifier que tout marche bien : 

```bash
cd PA_Communautaire/packages/pac-bdd
uv run pytest -v
```

Si on veut lancer un test seulement sur une partie du projet : 

```bash
uv run pytest -v test_scenario.py
```
