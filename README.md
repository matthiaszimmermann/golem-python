# Golem Base using Python SDK

## Spin up a Local Golem Base Node

1. Install [Git](https://git-scm.com/downloads), [Docker](https://www.docker.com/get-started) and [VS Code](https://code.visualstudio.com/)
2. Open a new terminal on your host machine
3. Clone the Golem Base Github repo.
```bash
git clone https://github.com/Golem-Base/golembase-op-geth
cd golembase-op-geth
```

4. Spin up local services of node
```bash
docker compose up -d
```

5. Verify the services are running
```bash
docker compose ps
```

You should see an output similar to the output below
```bash
NAME                              IMAGE                           COMMAND                  SERVICE       CREATED        STATUS                  PORTS
golembase-op-geth-mongodb-etl-1   golembase-op-geth-mongodb-etl   "/usr/local/bin/mong…"   mongodb-etl   18 hours ago   Up 18 hours             8545-8546/tcp, 30303/tcp, 30303/udp
golembase-op-geth-op-geth-1       golembase-op-geth-op-geth       "geth --dev --http -…"   op-geth       18 hours ago   Up 18 hours (healthy)   0.0.0.0:8545->8545/tcp, [::]:8545->8545/tcp
golembase-op-geth-rpcplorer-1     dmilhdef/rpcplorer:v0.0.1       "/app/service"           rpcplorer     18 hours ago   Up 18 hours             0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp
golembase-op-geth-sqlite-etl-1    golembase-op-geth-sqlite-etl    "/usr/local/bin/sqli…"   sqlite-etl    18 hours ago   Up 18 hours             8545-8546/tcp, 30303/tcp, 30303/udp
mongodb                           mongo:8.0.6                     "docker-entrypoint.s…"   mongodb       18 hours ago   Up 18 hours (healthy)   0.0.0.0:27017->27017/tcp, [::]:27017->27017/tcp
```

## Check your Golem Base Setup

1. Check the Golem Base Explorer

Open the Golem Base Explorer in your browser [http://localhost:8080/](http://localhost:8080/)

2. Check the Golem Base CLI is running

Open a shell in the container which runs the Golem Base CLI
```bash
docker exec -it golembase-op-geth-op-geth-1 sh
```

In the opened shell check `golembase` is available (which should print `/usr/local/bin/golembase`)
then show the help page of `golembase`
```bash
which golembase
golembase help
```

## Create and Fund a New Account

```bash
golembase account create
```

Address and the file holding the private key are logged on the command line as shown below.

```bash
privageKeyPath /root/.config/golembase/private.key
Private key generated and saved to /root/.config/golembase/private.key
Address: 0xDF0fdD46CE72E55E96ab3b3Eb3d63eEE6aFeD749
```

Fund the newly created account and check its balance
```bash
golembase account fund
golembase account balance
```

The account balance should show 100 ETH (the default funding amount)
```bash
Address: 0xDF0fdD46CE72E55E96ab3b3Eb3d63eEE6aFeD749
Balance: 100 ETH
```

The same balance should be shown in the Golem Base Explorer [http://localhost:8080/](http://localhost:8080/)


## Clone this Repository

2. Clone this repository:
```bash
git clone https://github.com/matthiaszimmermann/golem-python.git
```

3. Open the project in VS Code:
```bash
cd golem-python
code .
```
4. When prompted, click "Reopen in Container"


## Copy the Private Key

1. Open a new terminal on your host machine
2. `cd` into the golem-python repository
3. Copy the account private key from the Golem Base container to your host machine
```bash
docker cp golembase-op-geth-op-geth-1:/root/.config/golembase/private.key ./private.key
```

## Install Python SDK and Scripts

1. Open a bash terminal

Your terminal inside the devcontainer setup should display a command prompt similar to the one shown below

```bash
root@e928153b72cc:/workspaces/golem-python#
```

Install the scripts.
```bash
uv pip install -e .
```

## Run the 'main' Script

```bash
uv run -m main --instance local
```

## Run the Chat 'client'

```bash
uv run -m client --help
uv run -m client <wallet-file>
```

## Prepare for Runing Tests

Create two funded test accounts and store the corresponding private keys in the following two files.

- `test1_private.key`
- `test2_private.key`

## Run the Tests

To run tests and only show summaries
```bash
uv run pytest
```

To show result per test
```bash
uv run pytest -v
```

To run a specific test and also show the logs from the test
```bash
uv run pytest tests/test_entity_creation.py --log-cli-level=INFO
```
