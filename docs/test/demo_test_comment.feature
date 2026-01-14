# language: fr
#
# Le fichier doit obligatoirement commencer par la ligne `# language: fr`
# pour que la syntaxe gherkin soit en Français
#
# Le fichier doit obligatoirement avoir l'extension `.feature`
# et être placé sous le répertoire `/docs` pour être pris en compte.
#
# Il y a une seule section `Fonctionnalité:` par fichier `.feature`
# 
Fonctionnalité: doc test BDD

    Scénario: simpliste avec commentaire
        Vous pouvez avoir un bloc de commentaire pour chaque scenario.
        Ce bloc doit être *collé* au scenario (pas de ligne vide avant).
        Ce bloc peut s'étendre sur plusieurs lignes.
        Il se *termine* par une ligne vide

        # Les *étapes* BDD suivent avec les mots clés `Quand`, `Alors`, `Et`, ...
        # Attention la majuscule du mot-clé est importante !

        Quand je fais quelque chose
        Et je fais autre chose
        Et je fais autre chose
        Et je fais autre chose
        
        Alors j'ai fait 4 choses

        # pour tester ce scenario uniquement:
        #    cd packages/pac-bdd
        #    uv run pytest -v test_scenario.py::test_simpliste_avec_commentaire
        # ou pour la version non commentée:
        #    uv run pytest -v test_scenario.py::test_simpliste
