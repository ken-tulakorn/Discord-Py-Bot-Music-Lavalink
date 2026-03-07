import os
import io
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import cast

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Button, View

import wavelink
import pytz
from dotenv import load_dotenv

# โหลด Environment Variables
load_dotenv()