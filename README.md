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

## Features

- System monitoring for onboard temperature, power consumption and relative humidity
- Two configurable temperature probes for rack, ambient or custom placement
- Dual fan control with RPM tracking and airflow estimation
- Automatic fan curves with linked or independent behavior
- Temporary boost mode to force maximum cooling for a defined duration
- Web dashboard with live status cards and historical charts
- History browsing by custom period, day or hour
- Local or remote access with authentication
- Kiosk mode for dedicated wall display or rack display usage
- End-to-end installation assistant, including kiosk setup
- Configurable SQLite storage location, including external USB or disk-based storage

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

## Dashboard

The web interface provides both live monitoring cards and historical charts.

### Live overview

![ThermalGuard HAT dashboard cards](docs/images/thermalguard-dashboard-cards.png)

### History view

![ThermalGuard HAT dashboard history](docs/images/thermalguard-dashboard-history.png)

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

The main configuration reference is [config/settings.example.json](config/settings.example.json).

### Core settings

| Key | Purpose | Example |
|---|---|---|
| `ConnectionStrings.WebApiDatabase` | SQLite database path used by the API | `Data Source=/opt/thermalguard-hat/api/db/LocalDatabase.db` |
| `Python.DbPath` | SQLite database path used by the Python service | `/opt/thermalguard-hat/api/db/LocalDatabase.db` |
| `RetentionDays` | Number of days of historical data to keep | `30` |
| `Auth.JwtSecret` | Secret used to sign JWT tokens | `change-me-in-production-at-least-32-chars!!` |
| `Auth.TokenExpiryHours` | JWT validity duration in hours | `12` |
| `AllowedOrigins` | Allowed frontend origin for CORS | `http://raspberrypi.local` |

### MQTT and broker settings

| Key | Purpose | Example |
|---|---|---|
| `BrokerHostSettings.Host` | MQTT broker hostname or IP | `127.0.0.1` |
| `BrokerHostSettings.Port` | MQTT TCP port | `1883` |
| `BrokerHostSettings.WsPort` | MQTT over WebSocket port | `1884` |
| `BrokerHostSettings.User` | MQTT username | `your-user` |
| `BrokerHostSettings.Password` | MQTT password | `your-password` |
| `BrokerHostSettings.UseTls` | Enable TLS for broker communication | `false` |
| `Mosquitto.Local.Authentication.Enabled` | Enable authentication on local Mosquitto | `false` |
| `Mosquitto.Bridge.Enabled` | Enable broker bridge mode | `false` |
| `Mosquitto.Bridge.Host` | Upstream broker hostname | `mqtt.example.com` |
| `Mosquitto.Bridge.Port` | Upstream broker port | `1883` |

### Sensors, cooling and hardware pins

| Key | Purpose | Example |
|---|---|---|
| `Python.Sensor1Uid` | 1-Wire identifier for probe 1 | `xxxxxxxxxxxx` |
| `Python.Sensor2Uid` | 1-Wire identifier for probe 2 | `xxxxxxxxxxxx` |
| `Python.SysFanThreshold` | Temperature threshold for the system fan | `38` |
| `Python.Fan1Pin` | PWM pin for fan 1 | `12` |
| `Python.Fan2Pin` | PWM pin for fan 2 | `13` |
| `Python.Fan1Sensor` | Tachometer input for fan 1 | `25` |
| `Python.Fan2Sensor` | Tachometer input for fan 2 | `24` |
| `Python.SystemFan` | GPIO pin for the auxiliary system fan | `23` |
| `Python.SysBuzzer` | GPIO pin for the buzzer | `22` |
| `Python.Button1Pin` | GPIO pin for button 1 | `17` |
| `Python.Button2Pin` | GPIO pin for button 2 | `0` |

### Display and UI labels

| Key | Purpose | Example |
|---|---|---|
| `Display.DashboardTitle` | Dashboard title shown in the UI | `Dashboard` |
| `Display.Sensor1Name` | Label for probe 1 | `Rack` |
| `Display.Sensor2Name` | Label for probe 2 | `Ambient` |
| `Display.Fan1Name` | Label for fan 1 | `Intake Fan` |
| `Display.Fan2Name` | Label for fan 2 | `Exhaust Fan` |
| `Display.Locale` | UI locale | `en-US` |
| `Display.TemperatureUnit` | Temperature unit | `C` |
| `Display.AirflowUnit` | Airflow unit displayed in the UI | `m3h` |
| `Display.Fan1MaxAirflow` | Reference airflow value for fan 1 | `95` |
| `Display.Fan2MaxAirflow` | Reference airflow value for fan 2 | `95` |

### Kiosk settings

| Key | Purpose | Example |
|---|---|---|
| `Kiosk.BypassIPs` | IP addresses allowed to access kiosk mode without standard login | `[]` |
| `KioskSetup.Enabled` | Enable kiosk setup during installation | `false` |
| `KioskSetup.User` | Desktop user used for kiosk autologin | `pi` |
| `KioskSetup.HideCursor` | Hide mouse cursor in kiosk mode | `true` |
| `KioskSetup.DesktopAutologin` | Enable desktop autologin | `true` |
| `KioskSetup.DisableScreenBlanking` | Disable screen blanking and sleep | `true` |
| `KioskSetup.Autostart` | Launch kiosk automatically on boot | `true` |

## Security

- API endpoints are protected with JWT authentication except the authentication bootstrap endpoints
- passwords are hashed with BCrypt
- the JWT secret must be changed before deployment
- CORS origins should be restricted to the actual deployed frontend origin

## License

MIT. See [LICENSE](LICENSE).
