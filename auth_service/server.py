import datetime, os, jwt
from flask import Flask, request
from flask_mysqldb import MySQL


server = Flask(__name__)
server.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
server.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
server.config['MYSQL_PORT'] = os.environ.get('MYSQL_PORT')
server.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
server.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
mysql = MySQL(server)

@server.route('/login', methods=['POST'])
def login():
    print("Headers:", request.headers)
    print("Content-Type:", request.content_type)
    print("Raw data:", request.data)

    data = request.get_json()
    print("Parsed JSON:", data)

    print(data)
    if not data or 'email' not in data or 'password' not in data:
        return data, 'Missing credentials', 401

    email = data['email']
    password = data['password']

    print(email, password)
    # check db for email and password  
    cur = mysql.connection.cursor()
    cur.execute("SELECT email, password FROM user WHERE email=%s", (email,))
    user_row = cur.fetchone()

    if user_row and user_row[1] == password:
        return createJWT(email, os.environ.get('JWT_SECRET'), True)
    else:
        return 'Invalid credentials', 401

def createJWT(email, secret, auth):
    return jwt.encode(
        {
            'email': email,
            'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'admin': auth
        },
        secret= secret,
        algorithm= 'HS256'
    )

@server.route('/validate', methods=['POST'])
def validate():
    encoded_jwt = request.headers['Authorization']
    
    if not encoded_jwt:
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
    except:
        return "not authorized", 403

    return decoded, 200
 
    

if __name__ == '__main__':
    server.run(host="0.0.0.0", port=5000)