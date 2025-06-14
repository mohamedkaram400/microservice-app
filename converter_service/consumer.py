from convert import to_mp3
import gridfs
from pymongo import MongoClient
import pika, sys, os, time

def main():
    client = MongoClient("mongodb://mongodb:27017")

    db_videos = client.videos
    db_mp3s = client.mp3

    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq')
    )
    channel1 = connection.channel()

    def callback(ch, method, props, body):
        err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    channel1.basic_consume(
        queue=os.environ.get('VIDEO_QUEUE'), on_message_callback=callback
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