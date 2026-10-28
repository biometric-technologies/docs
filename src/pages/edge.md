---
title: Edge service
nav: Edge service
desc: Local capture and matching service for Iritech iris scanners and webcams.
---
# Edge service

<p class="lead">A small service that runs next to the capture device. It talks to the scanner, gives your web application a simple local REST API for capture and live preview, keeps an encrypted local person database and synchronises it with the Cloud Iris API. Enrolment and matching keep working when the network is down.</p>

Supported devices:

- Iritech IriShield and other scanners on the Iritech IDDK 2000 SDK;
- generic USB webcams (for development and demos, not for production iris capture).

Runs on Windows and Linux with Java 11 or newer.

## Installation

1. Install JDK 11 or newer and make sure `java -version` reports 11+.
2. Install the device driver from the scanner vendor.
3. Unpack the service build into a folder, for example `C:\iriscan` or `/opt/iriscan`.
4. Start it with `start.bat` (Windows) or `./start` (Linux). To run it as a system service use `install-service.bat` or `install-service.sh`; on Linux this installs a systemd unit named `iriscan`.

The service listens on `http://localhost:8080`. Builds are provided to customers on request.

The local database is an embedded H2 file encrypted with AES and unlocked with the device ID and key issued with your tenant.

## Capture API

All responses carry `"status": "success"` or `"status": "error"`.

| Method | Path | What it does |
|---|---|---|
| `POST` | `/1.0/initialize` | Opens the scanner and starts the preview stream |
| `GET` | `/1.0/stream` | Live preview as MJPEG (`multipart/x-mixed-replace`) |
| `POST` | `/1.0/capture` | Captures a sample, returns `captureIds` |
| `GET` | `/1.0/samplequality` | Quality of the last capture |
| `POST` | `/1.0/download/image` | Last captured image as base64 JPEG in `sensorData` |
| `GET` | `/1.0/deviceinfo` | Device properties as key/value pairs |

```json
POST /1.0/initialize
{ "status": "success", "cameraModality": "monocular", "streamUrls": ["stream"] }

GET /1.0/samplequality
{ "status": "success", "quality": { "submodality": "iris", "totalScore": 87, "usableAreaScore": 92 } }
```

A typical page puts `<img src="http://localhost:8080/1.0/stream">` in front of the user, polls `samplequality` while the subject positions the eye, calls `capture` when the score is good enough and then `download/image`.

## Local person API

The same person operations as the [Cloud Iris API](cloud-api.html) are served locally under `/tenant-api/persons`: create, update, delete, query, 1:N `find` and 1:1 `verify`.

Every new person is encrypted with the device key and pushed to the cloud tenant over a persistent RSocket connection. Records enrolled while the site was offline are sent when the connection comes back, so enrolment and verification never wait for the network.
