# ThermalGuard HAT

ThermalGuard HAT is a Raspberry Pi HAT for monitoring and controlling airflow in a server rack or enclosed equipment bay.

This repository contains both the hardware design and the software stack:

- a custom KiCad HAT
- a Python hardware service running on the Raspberry Pi
- a .NET 8 API
- an Angular web dashboard

## Demo

https://github.com/user-attachments/assets/5256e6de-0484-4bef-b895-a79b62438027

## Board Renders And Wiring

### KiCad 3D render - front

![ThermalGuard HAT front render](docs/images/thermalguard-front.png)

### KiCad 3D render - back

![ThermalGuard HAT back render](docs/images/thermalguard-back.png)

### Wiring overview

![ThermalGuard HAT wiring schematic](docs/images/thermalguard-scheme.png)

## What The Project Does

ThermalGuard HAT is designed to:

- read two DS18B20 temperature probes
- read ambient humidity and temperature from an SHT31D sensor
- drive two PWM fans
- monitor fan RPM and system current
- expose live telemetry through MQTT
- store history in SQLite
- provide a web UI for monitoring, setup and control

The current reference platform for this project is a Raspberry Pi 2B.

## Repository Structure

```text
thermalguard-hat/
|-- back/         .NET 8 API, persistence, workers, static frontend hosting
|-- front/        Angular frontend
|-- python/       Raspberry Pi hardware service
|-- kicad/        KiCad project for the HAT PCB
|-- config/       Shared example configuration
|-- docs/         README media assets
`-- install.sh    Raspberry Pi installation script
```

## Hardware

Main hardware blocks currently present in the project:

- Raspberry Pi 2B host
- custom HAT PCB designed in KiCad
- 2 x DS18B20 probes
- 1 x SHT31D temperature and humidity sensor
- 2 x PWM-controlled fans
- fan tachometer and current measurement circuitry
- OLED display and onboard controls

The repository is not only a software project. It also includes the PCB design files required to fabricate the HAT.

## Software Architecture

### Python service

The Python service is the hardware-facing part of the system. It:

- initializes GPIO and sensors
- controls the fans
- reads live measurements
- publishes telemetry on MQTT
- persists data into SQLite

Main entry points:

- [python/main.py](python/main.py)
- [python/service.py](python/service.py)

### Backend API

The backend is a .NET 8 application that:

- serves the web application
- exposes authenticated API endpoints
- stores and queries historical data
- exposes configuration for the frontend
- manages service status operations

Main entry points:

- [back/Program.cs](back/Program.cs)
- [back/Api/Controllers](back/Api/Controllers)

### Frontend

The frontend is an Angular application providing:

- dashboard views
- setup and login screens
- kiosk mode
- live MQTT-backed monitoring cards and graphs

Main entry points:

- [front/src/app/pages/dashboard.component.ts](front/src/app/pages/dashboard.component.ts)
- [front/src/app/app.routes.ts](front/src/app/app.routes.ts)

## Installation

Run the installation script on the Raspberry Pi as root:

```bash
sudo bash -c "$(curl -sSL https://raw.githubusercontent.com/olivierpetitjean/thermalguard-hat/main/install.sh)"
```

The script installs the software stack, prepares the Raspberry Pi environment and deploys the backend, frontend and Python service.

## Storage Recommendation

For a permanent installation, it is strongly recommended to store the SQLite database on an external storage device such as:

- a USB flash drive
- an external SSD
- an external hard drive

Reason:

- the system performs repeated read and write operations
- keeping the database on the Raspberry Pi SD card increases wear
- the SD card also hosts the operating system, so avoiding unnecessary writes improves reliability

The database location is configurable:

- backend connection string in [back/appsettings.json](back/appsettings.json)
- Python database path in [python/settings.example.json](python/settings.example.json)

## Configuration

Useful configuration files:

- [config/settings.example.json](config/settings.example.json)
- [python/settings.example.json](python/settings.example.json)
- [back/appsettings.json](back/appsettings.json)

Configuration covers:

- database path
- MQTT broker settings
- sensor identifiers
- GPIO mapping
- JWT authentication secret
- display labels and UI naming

## Security

- API endpoints are protected with JWT authentication except the authentication bootstrap endpoints
- passwords are hashed with BCrypt
- the JWT secret must be changed before deployment
- CORS origins should be restricted to the actual deployed frontend origin

## License

MIT. See [LICENSE](LICENSE).
