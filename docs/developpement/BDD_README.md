# Tests pilotés par le comportement

Pour garantir un niveau de qualité élevé du code et s'assurer que le code continue de fonctionner comme prévue, nous avons mis en place des tests BDD - Behavior Driven Development.

Les BDD permettent à des développeurs mais aussi à des experts métiers de comprendre facilement le fonctionnement du projet. 

Vous trouverez 2 guides pour comprendre et construire des jeux de tests : 

* [Guide pour l'expert métier](BDD_Guide_Expert_Metier.md)
* [Guide pour le développeur](BDD_Guide_Developpeur.md)

# Exécution des tests

TODO a relire avec philippe

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
cd packages/pac0 
uv run pytest

# Tests pac-bdd
cd packages/pac-bdd 
uv run pytest
```

On peut utiliser l'option -v pour avoir plus d'information.


Si on veut lancer un test seulement sur une partie du projet : 

```bash
uv run pytest -v test_scenario.py
```
