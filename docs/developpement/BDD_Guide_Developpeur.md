# Implémenter un test BDD - Guide pour le développeur

Comment faire pour programmer un test à partir des tests BDD rédigés par un expert métier.

Pré-requis: Avoir lu la doc [BDD_Guide_Expert_Metier.md](BDD_Guide_Expert_Metier)


## Architecture des tests BDD

```
packages/pac-bdd/
├── test_scenario.py          # Point d'entrée - charge tous les .feature
└── src/pac_bdd/
    ├── steps.py              # Import de tous les modules de steps
    ├── api.py                # Steps pour les appels API
    ├── peppol.py             # Steps pour PEPPOL/routage
    ├── service.py            # Steps pour les services
    ├── esb.py                # Steps pour le bus de messages
    └── tobeimplemented.py    # Steps en attente d'implémentation

packages/pac0/src/pac0/shared/test/
├── world.py                  # WorldContext et fixtures pytest
└── service/
    ├── pac.py                # PacServiceContext
    ├── nats.py               # NatsServiceContext
    └── faststream.py         # FastStreamServiceContext
```

### Comment ça fonctionne

```
┌────────────┐                 ┌──────────────┐                 ┌───────────┐
│   Étapes   │                 │   Code des   │                 │           │
│ en Gherkin ├─correspondance─>│    Steps     ├────manipule────>│  Système  │
└────────────┘                 └──────────────┘                 └───────────┘
```

1. Cucumber/pytest-bdd lit une étape Gherkin (ex: `Quand j'appele l'API GET /healthcheck`)
2. Recherche un step definition avec une expression correspondante
3. Extrait les paramètres
4. Exécute la fonction Python associée

## Exécution des tests

```bash
cd packages/pac-bdd

# Tous les tests
uv run pytest

# Un test spécifique
uv run pytest test_scenario.py::test_identification_france -v

# Tests avec un tag
uv run pytest -m "smoke"

# Mode debug avec logs
uv run pytest test_scenario.py::test_healthcheck -v -s --log-cli-level=DEBUG

# Collecter sans exécuter
uv run pytest --collect-only

# Arrêt au premier échec
uv run pytest -x
```

## Implémenter une étape (step)

### 1. Identifier l'étape manquante

Quand un test échoue avec `StepDefNotFound`, le message indique l'étape à implémenter :

```
pytest_bdd.exceptions.StepDefNotFound:
Step definition is not found: "je vérifie le format UBL"
```

### 2. Choisir le bon module

| Domaine | Fichier |
|---------|---------|
| Appels REST API | `api.py` |
| PEPPOL, routage | `peppol.py` |
| Services, lifecycle | `service.py` |
| Bus de messages | `esb.py` |
| Steps non implémentés | `tobeimplemented.py` |

### 3. Écrire le step

#### Step simple

```python
from pytest_bdd import given, when, then

@then("j'obtiens une réponse valide")
def _(ctx):
    assert ctx.result is not None
```

#### Step avec paramètres (parsers.parse)

La méthode `parsers.parse` utilise des **Cucumber Expressions** simplifiées :

```python
from pytest_bdd import when, parsers

@when(parsers.parse('je calcule l\'empreinte md5 de "{msg}"'))
def _(peppol_context, msg: str):
    peppol_context.result = hashlib.md5(msg.encode()).hexdigest()

@when(parsers.parse("j'appele l'API {verb} {path}"))
def _(ctx, world1, verb: str, path: str):
    # verb = "GET", path = "/healthcheck"
    ...
```

#### Step avec regex (plus flexible)

Pour des patterns complexes, utilisez `parsers.re` :

```python
from pytest_bdd import then, parsers

@then(parsers.re(r"j'obtiens (?P<count>\d+) résultats?"))
def _(ctx, count: str):
    assert len(ctx.results) == int(count)

# Texte optionnel avec ()?
@then(parsers.re(r"le fichier( n')?(existe)( pas)?"))
def _(ctx, neg1, verb, neg2):
    exists = neg1 is None and neg2 is None
    ...
```

### 4. Gérer les Data Tables

```python
@given(parsers.parse("les entreprises suivantes:"))
def _(ctx, datatable):
    # datatable est une liste de dictionnaires
    for row in datatable:
        # row = {"siren": "123456789", "nom": "Entreprise A"}
        ctx.entreprises.append(row)
```

### 5. Gérer les Doc Strings

```python
@given(parsers.parse("une facture au format JSON:"))
def _(ctx, docstring):
    # docstring contient le texte brut du bloc """..."""
    ctx.facture = json.loads(docstring)
```

## Fixtures pytest-bdd

### WorldContext - environnement multi-PA

```python
from pac0.shared.test.world import WorldContext, world1

@given("une pa communautaire")
def _(world1: WorldContext):
    # world1 contient déjà une PA initialisée
    pass

@when(parsers.parse("j'appele l'API {verb} {path}"))
def _(world1: WorldContext, verb: str, path: str):
    with world1.pa1.api_gateway.get_client() as client:
        response = client.request(verb, path)
```

### Contexte local - données du scénario

Quand on doit manipuler des données diverses, au lieu de balancer à l'arrache un tableau, on peut structurer les données en utilisant pyDantic. On va regrouper et typer nos données dans une class qui sera plus facile à manipuler. 

Créez un contexte Pydantic pour partager des données entre steps :

```python
from pydantic import BaseModel
from typing import Any
import pytest

class LocalTestCtx(BaseModel):
    result: Any | None = None
    result_status_code: int | None = None
    result_json: dict | None = None

@pytest.fixture
def ctx():
    return LocalTestCtx()

@when(parsers.parse("j'appele l'API {verb} {path}"))
def _(ctx: LocalTestCtx, world1: WorldContext, verb: str, path: str):
    with world1.pa1.api_gateway.get_client() as client:
        response = client.request(verb, path)
        ctx.result_status_code = response.status_code
        ctx.result_json = response.json()

@then(parsers.parse("j'obtiens le code de retour {code}"))
def _(ctx: LocalTestCtx, code: str):
    assert ctx.result_status_code == int(code)
```

### Contexte partagé par domaine

Pour les données persistantes entre steps d'un même domaine :

```python
class PeppolContext(BaseModel):
    sml_zone: str = "acc.edelivery.tech.ec.europa.eu"
    result: Any | None = None

@pytest.fixture
def peppol_context():
    return PeppolContext()

@given(parsers.parse('la racine SML "{zone}"'))
def _(peppol_context: PeppolContext, zone: str):
    peppol_context.sml_zone = zone
```

## Hooks (Before/After)

### Hook par scénario

```python
import pytest

@pytest.fixture(autouse=True)
def before_scenario():
    """Exécuté avant chaque scénario"""
    # Setup
    yield
    # Teardown (après le scénario)

# Avec pytest-bdd
from pytest_bdd import scenario

@pytest.fixture
def setup_database():
    db.setup()
    yield
    db.cleanup()
```

### Hook conditionnel par tag

```python
import pytest

@pytest.fixture
def browser(request):
    """Lancé uniquement pour les tests marqués @browser"""
    if "browser" in [m.name for m in request.node.iter_markers()]:
        browser = launch_browser()
        yield browser
        browser.close()
    else:
        yield None
```

## Patterns courants

### Appel API REST

```python
@when(parsers.parse("j'appele l'API {verb} {path}"))
def _(ctx: LocalTestCtx, world1: WorldContext, verb: str, path: str):
    with world1.pa1.api_gateway.get_client() as client:
        response = client.request(verb, path)
        ctx.result_status_code = response.status_code
        ctx.result_json = response.json()
```

### Vérification de valeur générique

```python
@then(parsers.parse('j\'obtiens "{result}"'))
def _(peppol_context, result: str):
    assert peppol_context.result == result
```

### Vérification de structure JSON

```python
@then(parsers.parse('la réponse a une clé "{key}" avec {nb} éléments'))
def _(ctx: LocalTestCtx, key: str, nb: str):
    assert len(ctx.result_json.get(key)) == int(nb)
```

### Async vers sync

pytest-bdd ne supporte pas nativement async. Utilisez ce wrapper :

```python
import asyncio
import functools

def async_to_sync(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return asyncio.run(fn(*args, **kwargs))
    return wrapper

@when("j'envoie un message async")
@async_to_sync
async def _(world1):
    await world1.pa1.esb.publish("topic", {"data": "test"})
```

### Step en attente d'implémentation

```python
@when(parsers.parse("une fonctionnalité future"))
def _():
    pytest.skip("En attente d'implémentation")
```

## Types de paramètres personnalisés

Pour réutiliser un pattern de parsing :

```python
from pytest_bdd import parsers

# Définir un type personnalisé avec regex
IDENTIFIANT_PATTERN = r"(?P<type>SIREN|SIRET|TVA_FR)"

@when(parsers.re(rf"je calcule l'empreinte {IDENTIFIANT_PATTERN} \"(?P<id>\d+)\""))
def _(peppol_context, type: str, id: str):
    peppol_context.result = compute_participant_hash(type, id)
```

## Organisation des fichiers

```python
# steps.py - Point d'entrée qui importe tous les modules
from .api import *
from .demo import *
from .esb import *
from .peppol import *
from .service import *
from .tobeimplemented import *
from .user import *
```

Chaque nouveau module de steps doit être importé dans `steps.py`.

## Debugging

```bash
# Voir les logs détaillés
uv run pytest test_scenario.py::test_healthcheck -v -s --log-cli-level=DEBUG

# Exécuter avec pdb au premier échec
uv run pytest test_scenario.py --pdb

# Afficher les print() dans les steps
uv run pytest -s
```

## Checklist avant PR

- [ ] Le step est dans le bon module (`api.py`, `peppol.py`, etc.)
- [ ] Le module est importé dans `steps.py`
- [ ] Le test passe localement : `uv run pytest test_scenario.py::test_xxx -v`
- [ ] Le step est réutilisable (paramétré si possible)
- [ ] Les assertions ont des messages clairs en cas d'échec
- [ ] Header SPDX présent dans le fichier
- [ ] Pas de couplage avec l'UI ou l'implémentation technique
