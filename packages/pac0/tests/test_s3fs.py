# see https://s3fs.readthedocs.io/en/latest/
# see https://github.com/fsspec/s3fs


# secret dans projet forgejo CI
# credentials bucket par Camille
# test s3fs


import s3fs
import os

s3 = s3fs.S3FileSystem(
    key=os.environ.get("STOCKAGE_KEY", "pdplibrekey"),
    secret=os.environ.get("STOCKAGE_SECRET", "Sup3rCl3"),
    endpoint_url=os.environ.get("STOCKAGE_URL", "http://localhost:8333/"),
    client_kwargs={"region_name": "fr-par"},
)

def test_upload_file():
    s3.put_file('my-file.txt', 'my-bucket/my-file.txt')
    print("✅ Upload réussi")

def test_10():
    s3.ls("my-bucket")
    with s3.open("my-bucket/my-file.txt", "rb") as f:
        print(f.read())