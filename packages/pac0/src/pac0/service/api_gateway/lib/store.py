# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
pac0.service.api_gateway.lib.store handles all s3 storage interaction.


"""

import hashlib
import aiobotocore
from fastapi import UploadFile
import httpx
import s3fs
from botocore.config import Config


# TODO: move to conf
# ENDPOINT_URL = "http://localhost:8333"
ENDPOINT_URL = "https://store.document.legal"
REGION_NAME = "fr-par"
AWS_ACCESS_KEY_ID = "pdplibrekey"
AWS_SECRET_ACCESS_KEY = "Sup3rCl3"


async def put(
    url: str,
    file: UploadFile,
):
    """
    Upload un fichier via un url s3 pre-signé
    """
    async with httpx.AsyncClient() as client:
        filename = (file.filename or "document").split("/")[-1]
        files = {"file": (filename, file.file, "application/octet-stream")}
        response = await client.put(url, files=files)
        response.raise_for_status()


def get_srv_bucket_key_from_file_ctx(
    hash: str,
    jwt: str | None,
    user_id: str | None,
    supplier_id: str | None,
    customer_id: str | None,
) -> tuple[str, str, str]:
    """
    Renvoie le serveur s3, le bucket la clé du fichier
    Utilise les arguments fournis pour choisir le bonserver/bucket/key
    """
    #
    server = s3fs.S3FileSystem(
        key=AWS_ACCESS_KEY_ID,
        secret=AWS_SECRET_ACCESS_KEY,
        endpoint_url=ENDPOINT_URL,
        # endpoint_url="http://192.168.12.50:8333",
        # endpoint_url="https://store.document.legal/",
        client_kwargs={"region_name": REGION_NAME},
        asynchronous=True,
    )

    bucket = "my-bucket"
    file_key = "xxxxxx.pdf"
    return (server, bucket, file_key)


async def get_presigned_url(
    s3: s3fs.S3FileSystem,
    bucket: str,
    key: str,
    method: str,
) -> str:
    """
    Generate a pre-signed URL for uploading a file to S3

    Utile uniquement pour le service 01-api
    les autres services recevront les URL pré-signés

    action = "put_object", "get_object"

    Returns:
        str: The pre-signed URL.
    """
    expiration = 3600  # 1 h

    # 1. Get the aiobotocore session from s3fs
    if s3.session is None:
        await s3.set_session()

    session = s3.session
    # session = aiobotocore.session
    session = aiobotocore.session.get_session()

    # 2. Create a client using the same session
    # For 'put_object', explicitly set signature_version to avoid issues
    async with session.create_client(
        "s3",
        # config=config
        # endpoint_url="https://store.document.legal/",
        endpoint_url=ENDPOINT_URL,
        config=Config(signature_version="s3v4"),
        region_name=REGION_NAME,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    ) as client:
        # 3. Generate the pre-signed URL
        url = await client.generate_presigned_url(
            ClientMethod=method,
            Params={
                "Bucket": bucket,
                "Key": key,
                # "ContentType": "application/pdf",
                # application/xml
                # application/json
                # application/pdf
                # application/yaml
            },
            ExpiresIn=expiration,
        )
        return url


async def compute_h256(file: UploadFile, buffer_size: int = 65536) -> str:
    """
    Calcule le hash SHA256 d'un fichier UploadFile de manière asynchrone.
    Replace le pointeur du fichier au début après le calcul.

    Args:
        file: Le fichier UploadFile de FastAPI
        buffer_size: Taille du buffer pour la lecture (64KB par défaut)

    Returns:
        Le hash SHA256 en hexadécimal
    """
    # Initialiser le hash
    sha256_hash = hashlib.sha256()

    # Placer le pointeur au début du fichier
    await file.seek(0)

    # Lire le fichier par blocs pour éviter de charger tout en mémoire
    while chunk := await file.read(buffer_size):
        sha256_hash.update(chunk)

    # Récupérer le hash en hexadécimal
    file_hash = sha256_hash.hexdigest()

    # Replacer le pointeur au début du fichier
    await file.seek(0)

    return file_hash


"""
IGNORE: ce qui suit:

- we use s3fs python package to access s3 buckets
- all s3 operations must be async
- offer a generic write()
- offer a generic read()
- offer a generic glob()
- offer a generic remove()
- all file argument must accept bytes, fastapi.UploadFile or pathlib.Path
- all functions accept an optional StoreCtx argument
- StoreCtx contains
    - company_id
    - invoice_id
    - s3fs.S3FileSystem
    - pre-signed URL 
    - 
       to get server/bucket/path

-
is a

"""
