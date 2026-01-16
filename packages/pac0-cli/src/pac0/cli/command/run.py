import typer
import subprocess
import subprocess
from . import setup
from .. import utils


app = typer.Typer()


services = [
    "01-api-gateway",
    "02-esb-central",
    "03-controle-formats",
    "04-validation-metier",
    "05-conversion-formats",
    "06-annuaire-local",
    "07-routage",
    "08-transmission-fiscale",
    "09-gestion-cycle-vie",
]


def _run_service(
    service: str,
):
    # TODO: check/install tools
    setup.tool(install=True)
    # TODO: get app folder
    setup.source()
    # TODO: clone if necessary
    _call(service)


def _call(
    service: str,
    run: bool = True,
    check: bool = False,
):
    # service folder: "05-conversion-formats" -> "conversion_formats"
    service_folder = "_".join(service.split("-")[1:])
    base_folder = utils.get_app_base_folder()
    print(f"{base_folder=}")
    if service == "01-api-gateway":
        full_path = f"src/pac0/service/{service_folder}/main.py"
        cmd = ["uv", "run", "fastapi", "dev", str(full_path)]
    elif service == "02-esb-central":
        cmd = ["nats-server", "-V", "-js"]
    else:
        full_path = f"src/pac0/service/{service_folder}/main:app"
        cmd = ["uv", "run", "faststream", "run", str(full_path)]

    if service != "02-esb-central":
        if check and not full_path.exists():
            typer.echo(f"Erreur: Le service {service} n'existe pas ({full_path})")
            raise typer.Exit(code=1)

    pac0_package_base_folder = base_folder / "packages" / "pac0"
    typer.echo(f"Lancement du service {service}...")
    typer.echo(f"Commande: {' '.join(cmd)}")
    typer.echo(f"pac0_package_base_folder: {pac0_package_base_folder}")

    if run:
        subprocess.call(cmd, cwd=pac0_package_base_folder)


@app.command(name="1", help="lance le service 01-api-gateway ...")
def _(): _run_service("01-api-gateway")

@app.command(name='2', help='lance le service 02-esb-central ...')
def _(): _run_service("02-esb-central")

@app.command(name='3', help='lance le service 03-controle-formats ...')
def _(): _run_service("03-controle-formats")

@app.command(name='4', help='lance le service 04-validation-metier ...')
def _(): _run_service("04-validation-metier")

@app.command(name='5', help='lance le service 05-conversion-formats ...')
def _(): _run_service("05-conversion-formats")

@app.command(name='6', help='lance le service 06-annuaire-local ...')
def _(): _run_service("06-annuaire-local")

@app.command(name='7', help='lance le service 07-routage") ...')
def _(): _run_service("07-routage")

@app.command(name='8', help='lance le service 08-transmission-fiscale ...')
def _(): _run_service("08-transmission-fiscale")

@app.command(name='9', help='lance le service 09-gestion-cycle ...')
def _(): _run_service("09-gestion-cycle-vie")


