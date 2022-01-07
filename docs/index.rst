.. Python AWS SQS Consumer documentation master file, created by
   sphinx-quickstart on Sat Jan  1 14:52:57 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python AWS SQS Consumer documentation
===================================================

.. toctree::
   :maxdepth: 2
   :caption: Overview
   :hidden:

   installation
   usage
   faq

.. toctree::
   :maxdepth: 2
   :caption: Reference
   :hidden:

   api

Write Amazon Simple Queue Service (SQS) consumers in Python with simplified interface. Define your logic to process an SQS message. After you're done processing, messages are deleted from the queue.

Heavily inspired from `https://github.com/bbc/sqs-consumer <https://github.com/bbc/sqs-consumer>`_, a similar JavaScript interface.

Installation
----------------

.. code:: bash

   pip install aws-sqs-consumer

Quick Start
----------------

.. code-block:: python
   
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

Indices and tables
==================

* :ref:`modindex`