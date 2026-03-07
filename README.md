# 🎵 Discord Music Bot

A high-performance Discord music bot developed in Python, supporting music playback via Lavalink. It features a "Music Box" system (a dedicated control channel) that makes operating the bot effortless and visually appealing.

## ✨ Features
* **Music Box UI:** Control music playback via interactive buttons (Play, Pause, Skip, Loop) without needing to type any commands.
* **Self-Deafen:** The bot automatically deafens itself when joining a voice channel to ensure user privacy and save bandwidth.
* **Global Support:** Fully supports multiple servers simultaneously using Global Commands.
* **High Performance:** Powered by a custom fork of Wavelink and Lavalink (supporting the latest versions).

## 🛠️ Tech Stack
* Python 3.10+
* [discord.py](https://github.com/Rapptz/discord.py)
* [Wavelink (Custom Fork)](https://github.com/ken-tulakorn/Wavelink) (For advanced audio handling and Discord DAVE support)
* SQLite3 (For managing the Music Box database)

## 🚀 How to Run
1. Install Python and the required libraries:
   ```bash
   pip install git+https://github.com/ken-tulakorn/Wavelink.git
