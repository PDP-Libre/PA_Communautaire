# Tests

## fichier feature

Voir le fichier [demo_test.feature](demo_test.feature) pour un test minimaliste.

Voir le fichier [demo_test_comment.feature](demo_test_comment.feature) pour le même test minimaliste
avec des explications.

## définition des étapes BDD

Le [scenario ci-dessus](demo_test.feature) a besoin de 3 types d'étapes BDD:
- @when("je fais quelque chose")
- @when("je fais autre chose")
- @then(parsers.parse("""j'ai fait {nb} choses"""))

Voici comment elles sont définies dans le fichier `packages/pac-bdd/src/pac_bdd/demo.py`:

```python
from pytest_bdd import then, when, parsers

# le contexte où conserver les états/valeurs à vérifier
ctx = {'nb': 0}

# on décore la fonction pour lui dire qu'elle doit être appelée
# pour l'étape "Quand je fais quelque chose"
@when("je fais quelque chose")
# peu import le nom de la fonction (il doit être unique)
def _():
    # on place dans le contexte la valeur modifiée
    ctx["nb"] += 1

# même chose pour l'étape "Quand je fais autre chose"
# valable aussi pour "Et je fais autre chose"
@when("je fais autre chose")
def _():
    ctx["nb"] += 1


# même chose pour l'étape "Alors j'ai fait 4 choses"
# notez le paramêtre `nb`
# notez l'utilisation pratique des triple quotes (''')
@then(parsers.parse("""j'ai fait {nb} choses"""))
def _(nb):
    # si le nombre donnée `nb` ne corresponds pas au contexte, on échoue
    assert ctx['nb'] == int(nb)
```

## rapports

En exécutant `./script/test` vous obtiendrez:


```
============================================================
Test Summary
============================================================
  pac0: PASSED (OK: 30, KO: 0)
  pac-bdd: FAILED (exit code: 1) (OK: 11, KO: 55)

Total: OK: 41/96, KO: 55/96

Reports generated in: /home/philippe/src/PA_Communautaire/report
  - pac0/report.html
  - pac0/report.xml
  - pac0/report.md
  - pac-bdd/report.html
  - pac-bdd/report.xml
  - pac-bdd/report.md
```