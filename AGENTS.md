# AGENTS.md

Guidelines for AI coding agents working in this repository.

## Project Overview

PA Communautaire (Plateforme Agréée Communautaire) is a French electronic invoicing
platform (PDP) built to comply with France's 2026-2027 mandatory e-invoicing reform.
It's an open-source, community-driven alternative supporting UBL, CII, and Factur-X
invoice formats per AFNOR standards (XP_Z12-012, XP_Z12-013, XP_Z12-014).

## Technology Stack

- **Language:** Python 3.13+
- **Package Manager:** uv (Rust-based, fast)
- **REST API:** FastAPI
- **Messaging:** NATS with JetStream, FastStream
- **Data Validation:** Pydantic
- **Testing:** pytest, pytest-asyncio, pytest-bdd

## Project Structure

```
/
├── packages/
│   ├── pac0/                 # Reference implementation
│   │   ├── src/pac0/
│   │   │   ├── service/      # Individual services
│   │   │   │   ├── api_gateway/
│   │   │   │   ├── validation_metier/
│   │   │   │   ├── gestion_cycle_vie/
│   │   │   │   └── routage/
│   │   │   └── shared/       # Shared utilities
│   │   └── tests/
│   └── pac-bdd/              # BDD testing package
│       ├── src/pac_bdd/      # Step definitions
│       └── test_*.py         # Test runners
├── docs/
│   ├── briques/              # Component docs + .feature files
│   │   ├── 01-api-gateway/
│   │   ├── 02-esb-central/
│   │   ├── 03-controle-formats/
│   │   ├── 04-validation-metier/
│   │   ├── 05-conversion-formats/
│   │   ├── 06-annuaire-local/
│   │   ├── 07-routage/
│   │   ├── 08-transmission-fiscale/
│   │   └── 09-gestion-cycle-vie/
│   └── norme/                # AFNOR standards, XSD, Swagger specs
└── README.md
```

## Development Commands

### Package Management (uv)

```bash
# Install dependencies
cd packages/pac0 && uv sync
cd packages/pac-bdd && uv sync

# Add a dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>
```

### Running Tests

```bash
# Run all tests in pac0
cd packages/pac0
uv run pytest

# Run a single test file
uv run pytest tests/test_fastapi.py

# Run a single test function
uv run pytest tests/test_fastapi.py::test_api_world_fixture -v

# Run tests with output
uv run pytest -v -s

# Run BDD tests
cd packages/pac-bdd
uv run pytest
```

### Running Services

```bash
cd packages/pac0

# Start NATS server (required first)
nats-server -V -js

# Start API Gateway (FastAPI dev mode)
uv run fastapi dev src/pac0/service/api_gateway/main.py

# Start FastStream services
uv run faststream run src/pac0/service/validation_metier/main:app
uv run faststream run src/pac0/service/gestion_cycle_vie/main:app
```

## Code Style Guidelines

### Imports

Organize imports in three groups, separated by blank lines:
1. Standard library
2. Third-party packages
3. Local imports

```python
import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI
from faststream.nats import NatsBroker, NatsRouter
from pydantic import BaseModel

from pac0.shared.esb import QUEUE
from pac0.service.api_gateway.lib import router
```

### Formatting

- **Indentation:** 4 spaces
- **Quotes:** Double quotes for strings
- **Line length:** ~88-100 characters
- **Trailing commas:** Use in multi-line structures

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Functions/variables | snake_case | `find_available_port` |
| Classes | PascalCase | `WorldContext`, `PaContext` |
| Constants | UPPER_SNAKE_CASE | `QUEUE`, `SUBJECT_IN` |
| NATS subjects | `{service}-IN/OUT/ERR` | `validation-metier-IN` |

### Type Hints

- Always use type hints on function signatures
- Use Pydantic `BaseModel` for data structures
- Use `Annotated` for complex types with metadata

```python
from pydantic import BaseModel

class Incoming(BaseModel):
    m: dict

async def process(message: str) -> dict:
    return {"status": "ok"}
```

### Async Patterns

- Use `async/await` throughout
- Implement async context managers (`__aenter__`/`__aexit__`) for resources
- Use `asyncio.create_task()` for background tasks

```python
async def __aenter__(self):
    self.broker = await self._broker.__aenter__()
    return self

async def __aexit__(self, exc_type, exc_val, exc_tb):
    await self.broker.__aexit__(exc_type, exc_val, exc_tb)
```

### Error Handling

- Use try/except with specific exceptions
- Silently handle `asyncio.CancelledError` during shutdown
- Use `pass` or `...` for intentionally empty handlers

```python
try:
    task.cancel()
except asyncio.CancelledError:
    pass
```

## Testing Guidelines

### Unit Tests (pytest-asyncio)

- Use `@pytest.mark.asyncio` for async tests
- Create fixtures with `@pytest.fixture` or `@pytest_asyncio.fixture`
- Use `WorldContext` and `PaContext` for integration tests

```python
@pytest.fixture
async def my_world():
    async with WorldContext(pac_pool=1) as world:
        yield world

@pytest.mark.asyncio
async def test_api_call(my_world):
    async with my_world.pac1.HttpxAsyncClient() as client:
        response = await client.get("/healthcheck")
        assert response.status_code == 200
```

### BDD Tests (pytest-bdd)

- Feature files use **French Gherkin** (`# language: fr`)
- Feature files are in `docs/briques/*/` directories
- Step definitions are in `packages/pac-bdd/src/pac_bdd/`

```gherkin
# language: fr
Fonctionnalité: healthcheck

    Scénario: healthcheck api ok
        Etant un utilisateur
        Quand j'appele l'API GET /healthcheck
        Alors j'obtiens le code de retour 200
```

## Architecture Notes

### Component Communication

All 9 components communicate via NATS ESB using a consistent channel pattern:

- `{service}-IN`: Input channel (receives messages)
- `{service}-OUT`: Output channel (sends results)
- `{service}-ERR`: Error channel (sends failures)

Example flow: `api-gateway-OUT` -> `controle-formats-IN` -> `controle-formats-OUT` -> `validation-metier-IN`

### Service Pattern

```python
from pac0.shared.esb import QUEUE
from faststream.nats import NatsRouter

SUBJECT_IN = "my-service-IN"
SUBJECT_OUT = "my-service-OUT"
SUBJECT_ERR = "my-service-ERR"

router = NatsRouter()
publisher_out = router.publisher(SUBJECT_OUT)

@router.subscriber(SUBJECT_IN, QUEUE)
async def process(message):
    await publisher_out.publish(message, correlation_id=message.correlation_id)
```

### Key Fixtures for Testing

- `WorldContext(pac_pool=N)`: Creates N isolated PA instances
- `PaContext`: Single PA with NATS, API, and services
- `world1pac`, `world2pac`, etc.: Pre-configured fixtures
