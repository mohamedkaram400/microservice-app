import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId

server = Flask(__name__)

# mongo_video = PyMongo(server, uri="mongodb://host.minikube.internal:27017/videos")
# mongo_mp3 = PyMongo(server, uri="mongodb://host.minikube.internal:27017/mp3s")
mongo_video = PyMongo(server, uri="mongodb://mongodb:27017/videos")
mongo_mp3 = PyMongo(server, uri="mongodb://mongodb:27017/mp3s")

videos_fs = gridfs.GridFS(mongo_video.db)
mp3s_fs = gridfs.GridFS(mongo_mp3.db)

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
server.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 

@server.route('/login', methods=['POST'])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err
    
@server.route('/upload', methods=['POST'])
def upload():
    print("Receiving file...")
    access, err = validate.token(request)

    if err:
        print("Access token error:", err)
        return err

    try:
        access = json.loads(access)
    except Exception as e:
        print("Error decoding access token:", e)
        return "Bad token format", 400

    if not access.get("admin", False):
        print("Not admin!")
        return "Not authorized", 401

    if "file" not in request.files:
        print("No file found in request!")
        return "File required", 400

    try:
        f = request.files["file"]
        f.seek(0)
        print("Uploading file:", f.filename)

        # ممكن تضيف طباعة عن حجم الملف
        file_size = len(f.read())
        print("File size:", file_size)
        f.seek(0)

        err = util.upload(f, videos_fs, channel, access)
        if err:
            print("Upload utility returned error:", err)
            return "Upload error", 500

        return "success", 200

    except Exception as e:
        print("Unhandled exception during upload:", e)
        import traceback
        traceback.print_exc()
        return "internal server error", 500

    

@server.route('/download', methods=['GET'])
def download():
    access, err = validate.token(request)

    if err:
        return err
    
    access = json.loads(access)

    if access['admin']:
        fid_string = request.args.get('fid')
        if not fid_string:
            return 'fid is required', 400
        
        try:
            out = mp3s_fs.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err)
            return "internal server error", 500
    
    return 'not authorized', 401

@server.route('/check-mongo')
def check_mongo():
    try:
        collections = mongo_video.db.list_collection_names()
        return {'status': 'connected', 'collections': collections}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500
    
if __name__ == "__main__":
    server.run(debug=True, host="0.0.0.0", port=8080)
