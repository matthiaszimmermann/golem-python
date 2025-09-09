# RabbitMQ Integration

## Install Pika (Python Lib)

```bash
uv add pika
```

## Starting Local Rabbit MQ

Open a new terminal and start Rabbit MQ
```bash
cd src/mq
docker compose up -d
```


## Run Scripts

Open a new terminal and start the Rabbit MQ Consumer
```bash
uv run src/mq/consumer.py
```

Open a new terminal and start the Rabbit MQ Producer (Golem DB Event Listener)
```bash
uv run src/mq/producer.py
```

Open a new terminal and start the Golem DB entity creator)
```bash
uv run src/mq/create_entities.py
```

Check the terminal output for the producer and the consumer.
In addition, check the Rabbit MQ Statistics in the [Rabbit MQ webapp](http://localhost:15672/).
The webapp was already started as part of the docker compose command.

Running the create_entities script with 1500 entities per batch leads to approx 170 created entities per second.
Below a sample output of the script is shown.

```bash
root@a0e5c3584e31:/workspaces/golem-python# uv run src/mq/create_entities.py
2025-09-09T11:05:05 Connected to Golem DB
2025-09-09T11:05:14 Batch no 0: Created 1500 entities
2025-09-09T11:05:24 Batch no 1: Created 1500 entities
2025-09-09T11:05:32 Batch no 2: Created 1500 entities
2025-09-09T11:05:45 Batch no 3: Created 1500 entities
2025-09-09T11:05:55 Batch no 4: Created 1500 entities
2025-09-09T11:06:05 Batch no 5: Created 1500 entities
2025-09-09T11:06:14 Batch no 6: Created 1500 entities
2025-09-09T11:06:23 Batch no 7: Created 1500 entities
2025-09-09T11:06:33 Batch no 8: Created 1500 entities
2025-09-09T11:06:43 Batch no 9: Created 1500 entities
```
