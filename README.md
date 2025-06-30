# 🎵 Video to MP3 Microservices System

This is a containerized microservices-based system built with **Python**, **Flask**, **RabbitMQ**, **MongoDB**, **MySQL**, and deployed using **Kubernetes** and **Docker**. It allows authenticated users to upload videos, convert them to MP3 format, and download the results, with optional email notifications upon conversion completion.

---

## 🧰 Technologies

- **Python (Flask)** – for building RESTful APIs
- **RabbitMQ** – message broker for async communication
- **MongoDB + GridFS** – for video and MP3 file storage
- **MySQL** – for storing user credentials
- **JWT** – for secure token-based authentication
- **Kubernetes** – for service orchestration and deployment
- **Docker** – for containerization of services

---

## 🧱 Architecture Overview

The system is composed of several microservices:

### 1. 🔐 Auth Service
- Validates user credentials against a MySQL database.
- Issues JWT tokens on successful login.
- Provides a `/validate` endpoint to decode and verify tokens.

### 2. 📤 Upload Service
- Accepts video uploads from authenticated admin users.
- Stores video files in MongoDB using GridFS.
- Publishes a message to RabbitMQ (`video` queue) for conversion.

### 3. 🔁 Converter Service
- Listens on the `video` queue.
- Retrieves the video from MongoDB.
- Converts the video to MP3 using `moviepy`.
- Stores the converted MP3 in a separate MongoDB collection.
- Publishes a message to the `mp3` queue upon success.

### 4. 📬 Notification Service
- Listens on the `mp3` queue.
- Sends an email notification when conversion is complete.

---

## 🚀 Features

- ✅ Upload video files via REST API
- 🔒 JWT-based authentication
- 🐇 Asynchronous processing with RabbitMQ
- 🎞️ Video-to-MP3 conversion using `moviepy`
- 📨 Email notification after successful conversion
- 📁 File storage with MongoDB GridFS
- ☸️ Full deployment via Kubernetes

---

## 📦 API Endpoints

### 🔐 Auth Service (`localhost:5000`)

| Method | Endpoint      | Description                     |
|--------|---------------|---------------------------------|
| POST   | `/login`      | Authenticate user and return JWT |
| POST   | `/validate`   | Validate and decode a JWT token  |

### 📤 Upload Service (`localhost:8080`)

| Method | Endpoint        | Description                       |
|--------|------------------|-----------------------------------|
| POST   | `/login`         | Same as Auth Service login        |
| POST   | `/upload`        | Upload a video file (admin only)  |
| GET    | `/download`      | Download converted MP3 by `fid`   |
| GET    | `/check-mongo`   | Check MongoDB connection status   |

---

## ⚙️ Environment Variables

| Variable         | Description                                   |
|------------------|-----------------------------------------------|
| `MYSQL_HOST`     | MySQL hostname                                |
| `MYSQL_USER`     | MySQL username                                |
| `MYSQL_PASSWORD` | MySQL password                                |
| `MYSQL_DB`       | MySQL database name                           |
| `MYSQL_PORT`     | (Optional) Defaults to `3306`                 |
| `JWT_SECRET`     | Secret used for signing JWT tokens            |
| `VIDEO_QUEUE`    | Name of the RabbitMQ queue for video uploads  |
| `MP3_QUEUE`      | Name of the RabbitMQ queue for MP3 files      |
| `GMAIL_ADDRESS`  | Sender Gmail address for notifications        |
| `GMAIL_PASSWORD` | Gmail App Password or regular password        |

---

## 🐳 Docker & Kubernetes

Each service is containerized and communicates via internal networking:

- MongoDB stores raw video files and MP3s using GridFS.
- RabbitMQ is used as the messaging system between services.
- Services use logical DNS names (like `mongodb`, `rabbitmq`) for communication.
- Kubernetes handles service orchestration, scaling, and network configuration.

> It's recommended to expose only necessary ports (5000 for auth, 8080 for gateway).

---

## 🧪 Example Usage

### 🔑 1. Login and Get JWT

```bash
curl -X POST http://localhost:5000/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@example.com", "password": "yourpassword"}'

---

## 📤 Example Usage

### 1. Login and get JWT:
```bash
curl -X POST http://localhost:5000/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@example.com", "password": "yourpassword"}'
```

## Gateway Service
```bash
POST /upload
Headers: Authorization: Bearer <JWT>
Form: file=<video file>

GET /download?fid=<id>
Headers: Authorization: Bearer <JWT>
```

## Upload video
```bash
curl -X POST http://localhost:8080/upload \
     -H "Authorization: Bearer <JWT>" \
     -F "file=@video.mp4"
```

## Download MP3
```bash
curl -X GET "http://localhost:8080/download?fid=<file_id>" \
     -H "Authorization: Bearer <JWT>" --output output.mp3
```

## Check MongoDB

```bash
curl -X GET http://localhost:8080/check-mongo
