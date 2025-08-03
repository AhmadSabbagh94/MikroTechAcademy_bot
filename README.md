# MikroTechAcademy Telegram Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Framework](https://img.shields.io/badge/Framework-Flask-blue?logo=flask)
![Library](https://img.shields.io/badge/Library-python--telegram--bot-blue)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

A Telegram bot for **MikroTechAcademy** designed to connect students with tutors. This version is a webhook-based Flask application ready for deployment on cloud platforms like Render.

## Features

- **🌍 Region Selection**: Users select their country to get tailored information.
- **🛠️ Service Menu**: A clear menu for assignments, private lessons, and direct tutor connections.
- **💰 Dynamic Pricing**: Displays tutoring prices in the user's local currency.
- **🔔 Admin Notifications**: Instantly notifies an administrator of all user requests with a "click-to-chat" link.
- **🚀 Webhook Ready**: Built with Flask to receive updates via HTTP, making it perfect for serverless deployment.
- **🔒 Secure Configuration**: Bot tokens and other secrets are loaded from environment variables.

## Deployment on Render

Follow these steps to deploy the bot on [Render](https://render.com/).

### 1. Fork the Repository

First, make sure all the files (`bot.py`, `requirements.txt`, `Procfile`, `README.md`) are in your GitHub repository.

### 2. Create a New Web Service on Render

1.  Go to your Render Dashboard and click **New +** > **Web Service**.
2.  Connect your GitHub account and select your bot's repository.
3.  Fill in the initial settings:
    - **Name**: Give your service a name (e.g., `mikrotech-bot`). This will be part of your URL.
    - **Root Directory**: Leave this as is if your files are in the root of the repo.
    - **Environment**: `Python 3`
    - **Region**: Choose a region close to you.
    - **Branch**: `main` (or your default branch).

### 3. Configure the Service

This is the most important part.

1.  **Build Command**: This command installs dependencies and sets up the bot.
    ```bash
    pip install -r requirements.txt && python bot.py setup_webhook
    ```
    *This command does two things: it installs the libraries, and then it runs our `setup_webhook` command from `bot.py` to tell Telegram where to send updates.*

2.  **Start Command**: This command runs the web server.
    ```bash
    gunicorn bot:app
    ```
    *This tells Gunicorn to run the `app` object found inside the `bot.py` file.*

3.  **Instance Type**: The `Free` plan is sufficient to start.

### 4. Add Environment Variables

Go to the **Environment** tab for your new service and add the following secrets:

- **Key**: `TELEGRAM_BOT_TOKEN`
  - **Value**: `7213024729:xxxxxxxxxxxxxxxxxxxxxxxx` (Your bot token)
- **Key**: `ADMIN_CLIENT_ID`
  - **Value**: `123456789` (Your personal Telegram ID)
- **Key**: `WEBHOOK_URL`
  - **Value**: `https://your-service-name.onrender.com` (The URL of your Render service, which you can find on the dashboard. **Do not add a slash at the end.**)
- **Key**: `PYTHON_VERSION`
  - **Value**: `3.11` (or your preferred Python 3 version)

### 5. Deploy

Click **Create Web Service**. Render will now build and deploy your application. You can watch the progress in the **Logs** tab. If everything is configured correctly, the bot will be live and responsive on Telegram!
