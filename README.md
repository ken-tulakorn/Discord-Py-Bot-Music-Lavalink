# 🎵 Discord Music Bot

A high-performance Discord music bot developed in Python, supporting music playback via Lavalink. It features a "Music Box" system (a dedicated control channel) that makes operating the bot effortless and visually appealing.

## ✨ Features
* **Music Box UI:** Control music playback via interactive buttons (Play, Pause, Skip, Loop) without needing to type any commands.
* **Self-Deafen:** The bot automatically deafens itself when joining a voice channel to ensure user privacy and save bandwidth.
* **Global Support:** Fully supports multiple servers simultaneously using Global Commands.
* **High Performance:** Powered by a custom fork of Wavelink and Lavalink (supporting the latest versions).

## 🛠️ Tech Stack
* Python 3.10+
* Java 17+ (Required for Lavalink)
* [discord.py](https://github.com/Rapptz/discord.py)
* [Wavelink (Custom Fork)](https://github.com/ken-tulakorn/Wavelink) (For advanced audio handling and Discord DAVE support)
* SQLite3 (For managing the Music Box database)

## 🚀 How to Run
### 1. Prerequisites
The bot is built using Python and requires both standard and external libraries:
* Java: You must have Java 17 or higher installed to run the [Lavalink](https://lavalink.dev/getting-started/index.html) server.
* Standard Libraries: `os`, `io`, `asyncio`, `logging`, `sqlite3`, `datetime`, `typing`.
* External Libraries: `discord.py`, `pytz`, `python-dotenv`.

### 2. Installation
You need to install the core Discord library and my specific Wavelink fork to ensure all features work correctly:
   ```bash
   pip install git+https://github.com/ken-tulakorn/Wavelink.git
   ```

### 3. Download Database
Because the bot uses SQLite to store data, you need to download the SQLite program:
   * Tool: Download and install [DB Browser for SQLite.](https://sqlitebrowser.org/dl/)

### 4. Configuration and Start
1. Token: Open the .env file and insert your bot token:
   ``
   DISCORD_API_TOKEN=YOUR_BOT_TOKEN_HERE
   ``

2. Lavalink Server Setup (Required)
   * The bot needs a Lavalink server to process audio.
     
3. Launch:
   * Windows: Double-click run.bat.
   * Other Platforms: Run python index.py in your terminal.
