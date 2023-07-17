# API

## `Consumer(...)`

Creates a new SQS consumer. Default parameters:

```python
consumer = Consumer(
    queue_url, # REQUIRED
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

### Attributes

| Attribute                                                                                                                     | Description                                                                                                                                                                                                                                                                                                                         | Default       | Example(s)                                                                                                                            |
|-------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `queue_url` (`str`)                                                                                                           | SQS Queue URL                                                                                                                                                                                                                                                                                                                       | **REQUIRED**  | `"https://sqs.eu-west-1.amazonaws.com/12345678901/test_queue"`                                                                        |
| `region` (`str`)                                                                                                              | AWS region for internally creating an SQS client using `boto3`                                                                                                                                                                                                                                                                      | `None` | `"us-east-1"`, `"ap-south-1"`; if not specified, will try to use boto3's environment variable `AWS_DEFAULT_REGION`                                                                                                         |
| `sqs_client` ([`boto3.SQS.Client`](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#id57)) | Override this to pass your own SQS client. This takes precedence over `region`                                                                                                                                                                                                                                                      | `None`        | `sqs_client = boto3.client("sqs", region_name="ap-south-1")`                                                                          |
| `attribute_names` (`list`)                                                                                                    | List of attributes that need to be returned along with each message.                                                                                                                                                                                                                                                                | `[]`          | - `["All"]` - Returns all values.<br>- `["ApproximateFirstReceiveTimestamp", "ApproximateReceiveCount", "SenderId", "SentTimestamp"]` |
| `message_attribute_names` (`list`)                                                                                            | List of names of message attributes, i.e. metadata you have passed to each message while sending to the queue.                                                                                                                                                                                                                      | `[]`          | `["CustomAttr1", "CustomAttr2"]`                                                                                                      |
| `batch_size` (`int`)                                                                                                          | Number of messages to return at once. (Maximum `10`)<br><br>- If `batch_size = 1`, override `handle_message(message)` and `handle_processing_exception(message, exception)` methods.<br>- If `batch_size > 1`, override `handle_message_batch(messages)` and `handle_batch_processing_exception(messages, exception)` methods.<br>  | `1`           |                                                                                                                                       |
| `wait_time_seconds` (`int`)                                                                                                   | The duration (in seconds) for which the call waits for a message to arrive in the queue before returning. If a message is available, the call returns sooner than `wait_time_seconds`.                                                                                                                                              | `1`           |                                                                                                                                       |
| `visibility_timeout_seconds` (`int`)                                                                                          | The duration (in seconds) that the received messages are hidden from subsequent retrieve requests after being retrieved. <br><br>If this is `None`, visibility timeout of the queue is used.                                                                                                                                        | `None`        | `30`                                                                                                                                  |
| `polling_wait_time_ms` (`int`)                                                                                                | The duration (in ms) between two subsequent polls.                                                                                                                                                                                                                                                                                  | `0`           | `2000` (2 seconds)                                                                                                                    |

### `consumer.start()`

Starts polling the queue. This blocks the main thread.

### `consumer.stop()`

Stops polling the queue. You can use this method only if you run the `consumer` in a separate thread.

### `handle_message(message)`

Override this method to define logic for handling a single message. By default, this does nothing (i.e. `pass`). This is called only if `batch_size=1`.

```python
from aws_sqs_consumer import Consumer, Message

class SimpleConsumer(Consumer):
    def handle_message(self, message: Message):
        print(f"Processing message: {message.Body}")
```

### `handle_processing_exception(message, exception)`

Override this method to handle any exception processing the message, including message deletion. By default, stack trace is printed to the console. This is called only if `batch_size=1`.

See [Handling exceptions](#handling-exceptions).

### `handle_message_batch(messages)`

Override this method to define logic for handling a message batch. By default, this does nothing (i.e. `pass`). This is called only if `batch_size > 1`.

See [Receiving messages in batches](#receiving-messages-in-batches).

### `handle_batch_processing_exception(messages, exception)`

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

## `Message`

`Message` represents a single SQS message. It is defined as a Python `dataclass` with the following attributes:

* `MessageId` (`str`) - A unique identifier for the message.
* `ReceiptHandle` (`str`) - An identifier associated with the act of receiving the message.
* `MD5OfBody` (`str`) - An MD5 digest of the non-URL-encoded message body string.
* `Body` (`str`) - The message's contents.
* `Attributes` (`Dict[str, str]`) - A map of the attributes requested in `attribute_names` parameter in `Consumer`.
* `MD5OfMessageAttributes` (`str`) - An MD5 digest of the non-URL-encoded message attribute string.
* `MessageAttributes` (`Dict[str, MessageAttributeValue]`) - Dictionary of user defined message attributes.

**Example:**

```python
def handle_message(self, message: Message):
    print("MessageID: ", message.MessageId)
    print("ReceiptHandle: ", message.ReceiptHandle)
    print("MD5OfBody: ", message.MD5OfBody)
    print("Body: ", message.Body)
    print("Attributes: ", message.Attributes)
```

```
MessageID:  29bab209-989d-41f3-85b4-c0e9f8d8b7a9
ReceiptHandle:  AQEBU2VaFVLF6eXzFVLwPIFCqrZC0twP+qzfy2mi...==
MD5OfBody:  c72b9698fa1927e1dd12d3cf26ed84b3
Body:  test message
Attributes:  {'ApproximateFirstReceiveTimestamp': '1640985674001'}
```

### `MessageAttributeValue`

`MessageAttributeValue` represents a user-defined SQS message attribute value. It is defined as a Python `dataclass` with the following attributes:

* `StringValue` (`str`) - attribute value, if it is a `str`.
* `BinaryValue` (`bytes`) - Binary type attributes can store any binary data, such as compressed data, encrypted data, or images.
* `DataType` (`str`) - SQS supports `String`, `Number`, and `Binary`. For the Number data type, you must use `StringValue`.

**Example:**

```python
def handle_message(self, message: Message):
    msg_attributes = message.MessageAttributes
    host = msg_attributes["host"].StringValue
    age  = msg_attributes["age"].StringValue

    print("Message body=", message.Body)
    print("Message attribute host=", host)
    print("Message attribute age=", age)
```

```
Message body=test message
Message attribute host=host001.example.com
Message attribute age=20
```