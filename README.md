# Python AWS SQS Consumer

Write Amazon Simple Queue Service (SQS) consumers in Python with simplified interface. Works based on long polling and deletes messages after processing.

Heavily inspired from [https://github.com/bbc/sqs-consumer](https://github.com/bbc/sqs-consumer), a similar JavaScript interface.

## Installation

```
pip install aws-sqs-consumer
```

## Usage

### Simple usage

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

* `consumer.start()` will block the main thread.
* Consumer uses [SQS long polling](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-short-and-long-polling.html#sqs-long-polling) with configurable wait time between polls (`polling_wait_time_ms`).
* By default, messages are processed one by one. The `handle_message` method must be finished for processing the next one. For batch processing, use the `batch_size` option. [See all attributes](#attributes).
* Messages are deleted from the queue after `handle_message` is successfully completed. 
* Raising an exception in the handler function will not delete the message from the queue. Define your behavior for handling exceptions by overriding `handle_processing_exception(message, exception)` method.  See [Handling exceptions](#handling-exceptions)

### Batch processing

Switch to batch processing by passing `batch_size` parameter greater than `1`. Maximum supported `batch_size` is `10`.

```python
from typing import List
from aws_sqs_consumer import Consumer, Message

class BatchConsumer(Consumer):
    def handle_message_batch(self, messages: List[Message]):
        print(f"Received {len(messages)} Messages")
        for message in messages:
            print(f"\t{message.Body}")

consumer = BatchConsumer(
    queue_url="https://sqs.eu-west-1.amazonaws.com/12345678901/test_queue",
    batch_size=5,
    polling_wait_time_ms=5,
)
consumer.start()
```

### Handling exceptions

```python
from aws_sqs_consumer import Consumer, Message

class SimpleConsumer(Consumer):
    def handle_message(self, message: Message):
        print(f"Processing message: {message.Body}")
        raise Exception("Something went wrong!")

    def handle_processing_exception(self, message: Message, exception):
        # Define your logic to handle exception
        print(f"Exception occured while processing: {exception}")

consumer = SimpleConsumer(
    queue_url="https://sqs.eu-west-1.amazonaws.com/12345678901/test_queue",
    polling_wait_time_ms=5
)
consumer.start()
```

* Override `handle_batch_processing_exception(messages: List[Message], exception)` in case of `batch_size` > 1.

## API

### `Consumer(...)`

Creates a new SQS consumer. Default parameters:

```python
consumer = Consumer(
    queue_url,                      # REQUIRED
    region="eu-west-1",
    sqs_client=None,
    attribute_names=[],
    message_attribute_names=[],
    batch_size=1,
    wait_time_seconds=1,
    visibility_timeout_seconds=None,
    polling_wait_time_ms=0
)
```

#### Attributes

| Attribute                                                                                                                     | Description                                                                                                                                                                                                                                                                                                                         | Default       | Example(s)                                                                                                                            |
|-------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `queue_url` (`string`)                                                                                                        | SQS Queue URL                                                                                                                                                                                                                                                                                                                       | **REQUIRED**  | `"https://sqs.eu-west-1.amazonaws.com/12345678901/test_queue"`                                                                        |
| `region` (`string`)                                                                                                           | AWS region for internally creating an SQS client using `boto3`                                                                                                                                                                                                                                                                      | `"eu-west-1"` | `"us-east-1"`, `"ap-south-1"`                                                                                                         |
| `sqs_client` ([`boto3.SQS.Client`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#id57)) | Override this to pass your own SQS client. This takes precedence over `region`                                                                                                                                                                                                                                                      | `None`        | `sqs_client = boto3.client("sqs", region_name="ap-south-1")`                                                                          |
| `attribute_names` (`list`)                                                                                                    | List of attributes that need to be returned along with each message.                                                                                                                                                                                                                                                                | `[]`          | - `["All"]` - Returns all values.<br>- `["ApproximateFirstReceiveTimestamp", "ApproximateReceiveCount", "SenderId", "SentTimestamp"]` |
| `message_attribute_names` (`list`)                                                                                            | List of names of message attributes, i.e. metadata you have passed to each message while sending to the queue.                                                                                                                                                                                                                      | `[]`          | `["CustomAttr1", "CustomAttr2"]`                                                                                                      |
| `batch_size` (`int`)                                                                                                          | Number of messages to return at once. (Maximum `10`)<br><br>- If `batch_size = 1`, override `handle_message(message)` and `handle_processing_exception(message, exception)` methods.<br>- If `batch_size > 1`, override `handle_message_batch(messages)` and `handle_batch_processing_exception(messages, exception)` methods.<br>  | `1`           |                                                                                                                                       |
| `wait_time_seconds` (`int`)                                                                                                   | The duration (in seconds) for which the call waits for a message to arrive in the queue before returning. If a message is available, the call returns sooner than `wait_time_seconds`.                                                                                                                                              | `1`           |                                                                                                                                       |
| `visibility_timeout_seconds` (`int`)                                                                                          | The duration (in seconds) that the received messages are hidden from subsequent retrieve requests after being retrieved. <br><br>If this is `None`, visibility timeout of the queue is used.                                                                                                                                        | `None`        | `30`                                                                                                                                  |
| `polling_wait_time_ms` (`int`)                                                                                                | The duration (in ms) between two subsequent polls.                                                                                                                                                                                                                                                                                  | `0`           | `2000` (2 seconds)                                                                                                                    |

#### `consumer.start()`

Starts polling the queue. This blocks the main thread.

#### `consumer.stop()`

Stops polling the queue. You can use this method only if you run the `consumer` in a separate thread.

#### `handle_message(message)`

Override this method to define logic for handling a single message. By default, this does nothing (i.e. `pass`). This is called only if `batch_size=1`.

```python
from aws_sqs_consumer import Consumer, Message

class SimpleConsumer(Consumer):
    def handle_message(self, message: Message):
        print(f"Processing message: {message.Body}")
```

#### `handle_processing_exception(message, exception)`

Override this method to handle any exception processing the message, including message deletion. By default, stack trace is printed to the console. This is called only if `batch_size=1`.

See [Handling exceptions](#handling-exceptions).

#### `handle_message_batch(messages)`

Override this method to define logic for handling a message batch. By default, this does nothing (i.e. `pass`). This is called only if `batch_size > 1`.

See [Batch processing](#batch-processing).

#### `handle_batch_processing_exception(messages, exception)`

Override this method to handle any exception processing a message batch, including message batch deletion. By default, stack trace is printed to the console. This is called only if `batch_size > 1`.

```python
from typing import List
from aws_sqs_consumer import Consumer, Message

class BatchConsumer(Consumer):
    def handle_message_batch(self, messages: List[Message]):
        print(f"Received {len(messages)} Messages")
        raise Exception("Failed to process message batch")

    def handle_batch_processing_exception(messages: List[Message], exception):
        print(f"Exception occurred while processing message batch: {exception}")
```
