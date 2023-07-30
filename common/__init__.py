
from dataclasses import dataclass
from typing import Protocol
import pika
import json


@dataclass
class Event:

    @property
    def name(self):
        return self.__class__.__name__


class EntityID:
    value: int

    @property
    def id(self):
        return self.value

    @id.setter
    def id(self, value: int):
        self.value = value


class AggregateRoot(EntityID):

    domain_events: list[Event]

    def __init__(self):
        self.domain_events = []

    def add_domain_event(self, event: Event):
        self.domain_events.append(event)


class Publisher(Protocol):

    def publish(self, queue: str, event: Event):
        ...


class RabbitMQPublisher(Publisher):

    def __init__(self, connection_string: str = "localhost"):
        self.connection_string = connection_string
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.connection_string))
        self.channel = self.connection.channel()

    def publish(self, queue: str, event: Event):
        self.channel.queue_declare(queue=queue)
        self.channel.basic_publish(
            exchange='', routing_key=queue, body=json.dumps(event.__dict__))

    def close_connection(self):
        self.connection.close()

    def reconnect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.connection_string))
        self.channel = self.connection.channel()
