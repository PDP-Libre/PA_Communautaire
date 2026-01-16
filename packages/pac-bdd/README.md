# pac-bdd

Ce projet `pac-bdd` permets la documentation et le dévéloppement selon l'approche BDD.
Une partie des fonctionnalités sont décrites sous forme de scenario BDD avec [Cucumber/Gherkin](https://cucumber.io/docs/).

Nous utilisons la syntaxe [gherkin en Français](https://cucumber.io/docs/gherkin/languages).

Les tests BDD sont des fichiers avec l'extension `.feature` et peuvent être placé n'importe où dans la doc.

Pour exécuter tous les tests BDD:

```shell
uv run pytest
```

```
❯ uv run pytest -v
============================================== test session starts ===============================================
platform linux -- Python 3.13.2, pytest-9.0.2, pluggy-1.6.0 -- /home/philippe/src/PA_Communautaire/packages/pac-bdd/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/philippe/src/PA_Communautaire/packages/pac-bdd
configfile: pyproject.toml
plugins: bdd-8.1.0
collected 2 items                                                                                                

test_scenario.py::test_pa PASSED                                                                           [ 50%]
test_scenario.py::test_invoice PASSED                                                                      [100%]

=============================================== 2 passed in 0.02s ================================================
```
