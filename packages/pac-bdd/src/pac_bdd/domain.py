import pytest
from pytest_bdd import given, parsers, scenario, then, when


@pytest.fixture
def auth():
    return {}

@pytest.fixture
def author():
    return "bob"


@given("un utilisateur")
def author_user(auth, author):
    auth["user"] = author


@given(
    parsers.parse("la PA #{pa}"),
)
def pa_given(pa):
    ...


@given(
    parsers.parse("l'entreprise #{company} enregistrée sur la PA #{pa}"),
)
def company_given(company, pa): ...


@given(
    parsers.parse(
        "la facture #{invoice} de #{company1} à #{company2}"
    ),
)
def invoice_given(invoice, company1, company2): ...


@when("je dépose une facture")
@when(
    parsers.parse(
        "je dépose la facture #{invoice} sur #{pa}"
    ),
)
@when(
    parsers.parse("je dépose la facture {invoice}"),
)
def submit_invoice():
    ...


@when(
    parsers.parse("je dépose pour contrôle la facture @{invoice}"),
)
def control_invoice(): ...


@then("j'obtiens un numéro de tâche")
def job_id():
    ...


@when("j'interroge la tâche")
def task_status(): ...


@when("je définis un contrôle de conformité métier fournisseur")
def compliance_rule_set(): ...


@when(
    parsers.parse('''l'adresse de contrôle "{url}"'''),
)
def compliance_rule_set_url(): ...


@then(
    parsers.parse("j'obtiens le statut #{status}"),
)
def job_status(status):
    assert False, f"statut {status} expected but not implemented !"
