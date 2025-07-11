# MikroTechAcademy Telegram Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![python-telegram-bot](https://img.shields.io/badge/Library-python--telegram--bot-blue)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

A Telegram bot for **MikroTechAcademy** designed to connect students with tutors. The bot handles service requests, gathers user information, provides pricing details, and notifies administrators of new requests in real-time.

## Features

- **🌍 Region Selection**: Users select their country of study to get tailored information.
- **🛠️ Service Menu**: A clear menu allows users to choose the help they need:
  - **Assignment/Project Help**: Users can upload files, photos, or text descriptions of their assignments.
  - **Private Lessons**: A guided process collects the user's name, phone number, and subject.
  - **Direct Tutor Connection**: Offers users the choice to either fill out a detailed form or request an immediate connection via Telegram.
- **💰 Dynamic Pricing**: Displays tutoring prices in the user's local currency based on pre-defined rates.
- **🔔 Admin Notifications**: Instantly notifies an administrator of all user requests. For direct connection requests, it provides a special "click-to-chat" link for the admin to immediately contact the user.
- **🤖 Conversation-Based Flow**: Uses a robust `ConversationHandler` to guide users through each step seamlessly.
- **🔒 Secure Configuration**: Bot tokens and admin IDs are loaded securely from environment variables, not hardcoded.

## Technology Stack

- **Language**: Python 3.10+
- **Main Library**: `python-telegram-bot`
- **Standard Libraries**: `os`, `logging`, `math`

## Setup and Installation

Follow these steps to get the bot running on your own machine or server.

### 1. Prerequisites

- Python 3.10 or newer.
- `pip` (Python package installer).
- A Telegram Bot Token from **@BotFather**.
- Your personal Telegram User ID from **@userinfobot**.

### 2. Clone the Repository

```bash
git clone [https://github.com/your-username/mikrotech-bot.git](https://github.com/your-username/mikrotech-bot.git)
cd mikrotech-bot
```

### 3. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

- **On macOS/Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- **On Windows:**
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

### 4. Install Dependencies

First, create a `requirements.txt` file in your project directory with the following content:

**`requirements.txt`**
```
python-telegram-bot
```

Now, run the installation command:

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

This project uses environment variables to keep your secret keys safe. You must set the following variables in your system:

- `TELEGRAM_BOT_TOKEN`: Your bot's API token from @BotFather.
- `ADMIN_CLIENT_ID`: Your personal Telegram User ID where notifications will be sent.

- **On macOS/Linux:**
  ```bash
  export TELEGRAM_BOT_TOKEN="7213024729:xxxxxxxxxxxxxxxxxxxxxxxx"
  export ADMIN_CLIENT_ID="123456789"
  ```
  *(Note: You may want to add these lines to your `.bashrc` or `.zshrc` file for them to persist)*

- **On Windows (Command Prompt):**
  ```bash
  set TELEGRAM_BOT_TOKEN="7213024729:xxxxxxxxxxxxxxxxxxxxxxxx"
  set ADMIN_CLIENT_ID="123456789"
  ```

### 6. Running the Bot

Once the dependencies are installed and the environment variables are set, you can run the bot with:

```bash
python bot.py
```

You should see the message `Bot is running...` in your console. You can now interact with your bot on Telegram!

## Project Structure

```
mikrotech-bot/
├── .gitignore
├── bot.py           # Main application logic
├── requirements.txt # Project dependencies
└── README.md        # This file
```

## How It Works

The bot is built around the `ConversationHandler` from the `python-telegram-bot` library. This allows for a state-based conversation, guiding the user from one step to the next based on their input (button clicks or messages). Each function corresponds to a specific state in the conversation, making the logic easy to follow and extend.
