import pytest
from pytest_bdd import given, parsers, scenario, then, when


# Note: "l'entreprise #{enterprise_id} enregistrée sur la PA #{pa_id}" is now defined in peppol.py
# Note: "la facture #{invoice_id} de #{sender_id} à #{recipient_id}" is now defined in peppol.py
# Note: "je dépose la facture #{invoice_id}" is now defined in peppol.py


@when("je dépose une facture")
def submit_invoice_simple():
    # POST /
    raise NotImplementedError()


@when(parsers.parse("je dépose la facture #{invoice} sur #{pa}"))
def submit_invoice_on_pa(invoice, pa):
    # POST /
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
