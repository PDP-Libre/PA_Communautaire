import pytest
from pytest_bdd import given, parsers, scenario, then, when


@given(
    parsers.parse("la PA #{pa}"),
)
def pa_given(pa):
    raise NotImplementedError()


@given(
    parsers.parse("l'entreprise #{company} enregistrée sur la PA #{pa}"),
)
def company_given(company, pa):
    raise NotImplementedError()


@given(
    parsers.parse("la facture #{invoice} de #{company1} à #{company2}"),
)
def invoice_given(invoice, company1, company2):
    raise NotImplementedError()


@when("je dépose une facture")
@when(
    parsers.parse("je dépose la facture #{invoice} sur #{pa}"),
)
@when(
    parsers.parse("je dépose la facture {invoice}"),
)
def submit_invoice():
    raise NotImplementedError()


@when(
    parsers.parse("je dépose pour contrôle la facture @{invoice}"),
)
def control_invoice():
    raise NotImplementedError()


@then("j'obtiens un numéro de tâche")
def job_id():
    raise NotImplementedError()


@when("j'interroge la tâche")
def task_status():
    raise NotImplementedError()


@when("je définis un contrôle de conformité métier fournisseur")
def compliance_rule_set():
    raise NotImplementedError()


@when(
    parsers.parse('''l'adresse de contrôle "{url}"'''),
)
def compliance_rule_set_url():
    raise NotImplementedError()


@then(
    parsers.parse("j'obtiens le statut #{status}"),
)
def job_status(status):
    # assert False, f"statut {status} expected but not implemented !"
    raise NotImplementedError()


@pytest.fixture
async def pac():
    # async with await nats.server.run(port=0) as server:
    #    assert server.is_running is True
    #    assert server.port > 0
    #    yield server
    ...


@pytest.fixture
def auth():
    return {}


@pytest.fixture
def author():
    return "bob"


# Etant un utilisateur
@given("un utilisateur")
def author_user(auth, author, pac):
    auth["user"] = author
    assert pac.is_running is True


# Quand j'appele l'API GET /healthcheck
@when(
    parsers.parse("j'appele l'API {verb} {path}"),
)
def api_call(verb, path):
    # raise NotImplementedError()
    ...


# Alors j'obtiens le code de retour 200
@then(parsers.parse("j'obtiens le code de retour {code}"))
def api_return_code(code):
    print("xxxxx a")
    # raise NotImplementedError()
    ...
