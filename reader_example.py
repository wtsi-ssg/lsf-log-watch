#!/usr/bin/env python
import pika
import json

'''
an example AMQP reader to collect successful
job data from a Rabbit AMQP LSF job queue
'''

COUNT = 0 

credentials=pika.credentials.PlainCredentials("userid", "password")
parameters = pika.ConnectionParameters('rabbitmq-server',
                                        5672,
                                        '/',
                                        credentials)

connection = pika.adapters.blocking_connection.BlockingConnection(parameters=parameters)
channel = connection.channel()
channel.queue_declare(queue = 'Finish')

def callback(ch, method, properties, body):
    if "job" in body:
    #if "Success" in body:
        global COUNT
        COUNT += 1
        print " [x] Received %r %d" % (body, COUNT)
channel.basic_consume(callback,
                      queue = 'Finish',
                      no_ack = True)
channel.start_consuming()
