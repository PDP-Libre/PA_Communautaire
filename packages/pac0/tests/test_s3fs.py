# see https://s3fs.readthedocs.io/en/latest/
# see https://github.com/fsspec/s3fs

import s3fs


s3 = s3fs.S3FileSystem(
    key="scaleway-api-key...",
    secret="scaleway-secretkey...",
    endpoint_url="https://s3.fr-par.scw.cloud",
    client_kwargs={"region_name": "fr-par"},
)


def test_10():
    s3 = s3fs.S3FileSystem(anon=True)
    s3.ls("my-bucket")
    with s3.open("my-bucket/my-file.txt", "rb") as f:
        print(f.read())
        