# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Proxy Client Test - Génération de requêtes API aléatoires pour tester un endpoint proxy.

Utilise httpx pour des requêtes asynchrones avec progression et statistiques détaillées.
"""

import asyncio
import json
import random
import string
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import httpx
import typer
import yaml
from tqdm import tqdm

app = typer.Typer()


@dataclass
class TestStats:
    """Statistiques pour les tests de proxy client."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    durations: list[float] = field(default_factory=list)
    status_codes: dict[int, int] = field(default_factory=dict)

    def add_result(
        self,
        success: bool,
        bytes_sent: int,
        bytes_received: int,
        duration: float,
        status_code: Optional[int] = None,
    ):
        """Ajoute un résultat aux statistiques."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
            if status_code:
                self.status_codes[status_code] = (
                    self.status_codes.get(status_code, 0) + 1
                )
        else:
            self.failed_requests += 1
        self.total_bytes_sent += bytes_sent
        self.total_bytes_received += bytes_received
        self.durations.append(duration)

    def percentile(self, data: list[float], p: int) -> float:
        """Calcule le percentile p de la liste de données."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * p / 100
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_data) else f
        return (
            sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])
            if c != f
            else sorted_data[f]
        )

    def report(self):
        """Génère un rapport de statistiques complet."""
        print("\n" + "=" * 70)
        print("RAPPORT DE STATISTIQUES - TEST PROXY CLIENT")
        print("=" * 70)
        print(f"\n📊 Résumé des requêtes:")
        print(f"   Total:        {self.total_requests}")
        print(
            f"   Succès:       {self.successful_requests} ({100 * self.successful_requests / self.total_requests:.1f}%)"
        )
        print(
            f"   Échecs:       {self.failed_requests} ({100 * self.failed_requests / self.total_requests:.1f}%)"
        )

        print(f"\n💾 Taille des données:")
        print(f"   Envoyé:       {self._format_bytes(self.total_bytes_sent)}")
        print(f"   Reçu:         {self._format_bytes(self.total_bytes_received)}")

        print(f"\n⏱️  Durée:")
        total_duration = sum(self.durations)
        print(f"   Total:        {total_duration:.2f}s")
        print(
            f"   Moyen:        {total_duration / len(self.durations):.3f}s (si total_requests > 0)"
        )

        if self.durations:
            print(f"\n📈 Percentiles de durée:")
            for p in [50, 90, 95, 99]:
                print(f"   P{p}:         {self.percentile(self.durations, p):.3f}s")

        if self.status_codes:
            print(f"\n🔢 Codes de statut:")
            for code in sorted(self.status_codes.keys()):
                count = self.status_codes[code]
                pct = 100 * count / self.total_requests
                print(f"   {code}: {count} ({pct:.1f}%)")

        print("\n" + "=" * 70)

    @staticmethod
    def _format_bytes(bytes_count: int) -> str:
        """Formate une taille en bytes en unités lisibles."""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_count < 1024:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024
        return f"{bytes_count:.2f} TB"


def generate_random_payload(avg_size: int, stdev: int) -> str:
    """Génère un payload JSON aléatoire de taille approximative."""
    # Taille cible avec variance
    target_size = max(10, int(random.gauss(avg_size, stdev)))

    # Générer des données aléatoires
    data = {
        "timestamp": time.time(),
        "request_id": "".join(
            random.choices(string.ascii_letters + string.digits, k=16)
        ),
        "payload": "".join(
            random.choices(string.ascii_letters + string.digits, k=target_size - 200)
        ),
        "metadata": {
            "version": "1.0",
            "random": random.random(),
        },
    }

    return json.dumps(data)


def load_config(
    config_path: Optional[str],
    endpoint: str,
    num_requests: int,
    num_parallel: int,
    avg_size: int,
    stdev_size: int,
    jwt_token: str,
) -> dict:
    """Charge la configuration depuis un fichier YAML ou utilise les paramètres CLI."""
    if config_path:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Fichier de configuration non trouvé: {config_path}"
            )

        with open(path, "r") as f:
            config = yaml.safe_load(f) or {}

        # Les paramètres CLI override le fichier YAML
        return {
            "endpoint": config.get("endpoint", endpoint),
            "num_requests": config.get("num_requests", num_requests),
            "num_parallel": config.get("num_parallel", num_parallel),
            "avg_payload_size": config.get("avg_payload_size", avg_size),
            "stdev_payload_size": config.get("stdev_payload_size", stdev_size),
            "jwt_token": config.get("jwt_token", jwt_token),
        }

    return {
        "endpoint": endpoint,
        "num_requests": num_requests,
        "num_parallel": num_parallel,
        "avg_payload_size": avg_size,
        "stdev_payload_size": stdev_size,
        "jwt_token": jwt_token,
    }


async def send_request(
    session: httpx.AsyncClient,
    endpoint: str,
    verb: str,
    path: str,
    payload: str,
    jwt_token: str,
    stats: TestStats,
    pbar,
):
    """Envoie une requête HTTP et met à jour les statistiques."""
    headers = {
        "Content-Type": "application/json",
    }

    # Only add JWT token if provided
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"

    start_time = time.time()
    success = False
    status_code = None
    bytes_sent = len(payload.encode("utf-8"))
    bytes_received = 0

    url = f"{endpoint}{path}"
    print(f"{url=}")
    try:
        response = await session.post(url, data=payload, headers=headers)
        status_code = response.status_code
        bytes_received = len(response.content)
        success = 200 <= status_code < 400  # 2xx and 3xx are considered success
    except Exception as e:
        pass  # L'échec est déjà géré par stats

    duration = time.time() - start_time
    stats.add_result(success, bytes_sent, bytes_received, duration, status_code)
    pbar.update(1)


@app.command()
def proxy_client(
    endpoint: str = typer.Argument(
        default="https://httpbin.org/post", help="URL de l'endpoint à tester"
    ),
    num_requests: int = typer.Option(
        default=10, help="Nombre total de requêtes à envoyer"
    ),
    num_parallel: int = typer.Option(default=5, help="Nombre de requêtes parallèles"),
    avg_size: int = typer.Option(
        default=1024, help="Taille moyenne du payload en octets"
    ),
    stdev_size: int = typer.Option(
        default=100, help="Écart-type de la taille du payload en octets"
    ),
    jwt_token: str = typer.Option(
        default="", help="Token JWT pour l'authentification (optionnel)"
    ),
    config: Optional[str] = typer.Option(
        None, "--config", "-c", help="Chemin vers un fichier YAML de configuration"
    ),
):
    """
    Test de charge pour un endpoint proxy.

    Générate des requêtes API aléatoires asynchrones avec progression visuelle
    et statistiques détaillées (percentiles 50, 90, 95, 99).

    Les paramètres peuvent être donnés en CLI ou dans un fichier YAML.

    \u26a0\ufe0f  Commande: pac0 test proxy-client
    """
    # Charger la configuration
    config_data = load_config(
        config, endpoint, num_requests, num_parallel, avg_size, stdev_size, jwt_token
    )

    endpoint = config_data["endpoint"]
    num_requests = config_data["num_requests"]
    num_parallel = config_data["num_parallel"]
    avg_size = config_data["avg_payload_size"]
    stdev_size = config_data["stdev_payload_size"]
    jwt_token = config_data["jwt_token"]

    print("\n" + "=" * 70)
    print("TEST PROXY CLIENT")
    print("=" * 70)
    print(f"\n🎯 Endpoint: {endpoint}")
    print(f"📋 Requêtes: {num_requests}")
    print(f"🔀 Parallélisme: {num_parallel}")
    print(f"📦 Payload: ~{avg_size}±{stdev_size} octets")
    if jwt_token:
        print(f"🔐 JWT: [MASKED]")
    else:
        print(f"🔐 JWT: non spécifié")
    print()

    stats = TestStats()

    async def run_tests():
        async with httpx.AsyncClient() as session:
            # Créer la file de tâches
            tasks = []  # Liste au lieu de set
            pbar = tqdm(total=num_requests, desc="Requêtes")

            for i in range(num_requests):
                payload = generate_random_payload(avg_size, stdev_size)
                path = "/flow"
                verb = "POST"
                task = asyncio.create_task(
                    send_request(
                        session, endpoint, verb, path, payload, jwt_token, stats, pbar
                    )
                )
                tasks.append(task)

                # Limiter le parallélisme
                if len(tasks) >= num_parallel:
                    done, tasks = await asyncio.wait(
                        tasks, return_when=asyncio.FIRST_COMPLETED
                    )
                    tasks = list(tasks)  # Convertir set en liste

            # Attendre les tâches restantes
            if tasks:
                await asyncio.gather(*tasks)

            pbar.close()

    # Exécuter le test
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrompu par l'utilisateur")

    # Afficher le rapport
    stats.report()


if __name__ == "__main__":
    app()
