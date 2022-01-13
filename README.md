# Python AWS SQS Consumer

[![PyPI](https://img.shields.io/pypi/v/aws-sqs-consumer?color=blue)](https://pypi.org/project/aws-sqs-consumer/)
[![Build passing](https://github.com/FlyweightGroup/aws_sqs_consumer_python/actions/workflows/tests.yml/badge.svg?event=push)](https://github.com/FlyweightGroup/aws_sqs_consumer_python/actions/workflows/tests.yml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/aws-sqs-consumer?color=g)

Write Amazon Simple Queue Service (SQS) consumers in Python with simplified interface. Define your logic to process an SQS message. After you're done processing, messages are deleted from the queue.

Checkout the full documentation - [https://aws-sqs-consumer-python.readthedocs.io/en/latest/](https://aws-sqs-consumer-python.readthedocs.io/en/latest/)

## Installation

```
pip install aws-sqs-consumer
```

## Simple Usage

```python
from aws_sqs_consumer import Consumer, Message

class SimpleConsumer(Consumer):
    def handle_message(self, message: Message):
        # Write your logic to handle a single `message`.
        print("Received message: ", message.Body)

consumer = SimpleConsumer(
    queue_url="https://sqs.eu-west-1.amazonaws.com/12345678901/test_queue",
    polling_wait_time_ms=5
)
consumer.start()
```

## Contributing

Checkout the Contribution guidelines - [CONTRIBUTING.md](CONTRIBUTING.md)
