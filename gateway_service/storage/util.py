import pika, json

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except Exception as err:
        print("GridFS Upload Error:", err)
        return 'internal server error', 500

    message = {
        'video_fid': str(fid),
        'mp3': None,
        "email": access["email"],
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        print("RabbitMQ Publish Error:", err)
        fs.delete(fid)
        return 'internal server error', 500

     