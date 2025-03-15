# Fastliner-Lite

**Fastliner-Lite** is a lightweight, command-based, terminal-style Matrix client built with Python. 
It leverages `matrix-nio` for Matrix API interactions and PySide6 for a minimalistic graphical interface. 
The application is designed to be simple and efficient.

---

## Features

- **Matrix Compatible:** Fully supports standard Matrix features including messaging, room and space management and user invites.
- **Terminal-like Command Interface:** Simplified interaction through intuitive `/commands`.
- **Lightweight UI:** Minimal graphical interface implemented with PySide6.

---

## Installation (Running from source)

Clone the repository and install dependencies:

```bash
git clone <repository_url>
cd Fastliner-Lite
pip install -r requirements.txt
```

*(Ensure you have Python 3.8 or higher installed.)*

---

## Running the Application (Running from source)

Run the application from source:

```bash
python main.py
```

---

## Project Structure

```
Fastliner-Lite/
├── ASSETS/
│    └── #Assets like logos etc go here.
├── CACHE/
│    └── #Cache used by the app for downloads like media.
├── CONFIG/
│    └── env.py #File for holding the homeserver and other adresses.
├── CORE/
│    ├── command_handler.py #All commands get processed and executed here.
│    └── matrix_client.py #Matrix logic group used for communicating with the homeserver(s).
├── LOGS/
│    └── #App logs that store the crash logs, errors and critical health data.
├── STORE/
│    └── config.json #File for reading and writing app settings.
├── UI/
│    ├── bot_game.py #Dormant file for later use.
│    ├── main_window.py #Main GUI window of the application.
│    ├── room_settings_window.py #Interface for displaying and interacting with room/space settings.
│    └── settings_window.py #Interface for displaying and interacting with application settings.
├── UTILS/
│    ├── color_manager.py #File which handles the coloring of different message signals.
│    ├── config_manager.py #The file for handling and managing config.json.
│    ├── jwt.py #Dormant file for later use.
│    ├── open_room_manager.py #File that keeps the track of opened rooms.
│    └── signals.py #General manager for signals, handles cross block communications.
├── .gitignore #gitignore file.
├── main.py #Main entry point of the app.
├── README.md #Readme file.
└── requirements.txt #Python requirements file.
```

---