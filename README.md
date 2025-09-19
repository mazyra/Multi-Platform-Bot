# Multi Platform Bot

SocialVideoBot is a Python-based automated bot for managing social media content.  
It currently supports **Instagram** and **YouTube Shorts**, and is designed to handle multiple types of media efficiently.

## Features

### Instagram
- Downloads **IGTV videos**, **Reels**, **photos**, and **stories** (including multi-slide stories).  
- Extracts and saves **captions** for each post.  
- Separates **audio from videos** and saves it as a separate file.  

### YouTube
- Downloads **short videos** (YouTube Shorts).  
- Extracts **audio from the videos** and saves it separately.  
- Retrieves **video captions**.  
- Future updates will include support for **full-length YouTube videos**.

## Technology
- Written in **Python**.  
- Uses **async PostgreSQL (asyncpg)** for database operations.  
- Fully modular design to easily add support for **more platforms** in the future.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/mazyra/Multi-Platform-Bot.git
cd Multi-Platform-Bot
