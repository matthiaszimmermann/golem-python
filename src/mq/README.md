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
