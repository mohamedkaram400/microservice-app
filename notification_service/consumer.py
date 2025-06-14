import pika, sys, os
from send import email

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq')
    )
    channel1 = connection.channel()

    def callback(ch, method, props, body):
        err = email.notification(body)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel1.basic_consume(
        queue=os.environ.get('MP3_QUEUE'), on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")

    channel1.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)