# pac0

Une implémentation de référence des specifications de PA Commmunautaire.


## tests

```
uv run pytest
```

## dépendances

* a light ESB: NATS: https://github.com/nats-io/nats-server/releases/download/v2.12.3/nats-server-v2.12.3-linux-amd64.tar.gz
* a light S3 storage: seeweedfs


```shell
# install nats-server
NATS_VERSION=2.12.3
wget https://github.com/nats-io/nats-server/releases/download/v${NATS_VERSION}/nats-server-v${NATS_VERSION}-linux-amd64.tar.gz
tar xvf nats-server-v*-linux-amd64.tar.gz
mv nats-server-v*-linux-amd64/nats-server ~/.local/bin/
rm -Rf nats-server-v*-linux-amd64*
```