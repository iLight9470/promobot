# Telegram Bot Controller

## Overview

This is a Flask-based web application that provides a dashboard interface for controlling a Telegram bot. The bot automatically sends promotional messages to multiple Telegram groups at scheduled intervals. The application features a web-based control panel for starting/stopping the bot, monitoring its status, viewing logs, and configuring settings.

The system is designed to automate social media promotion across Telegram groups while providing comprehensive monitoring and control capabilities through a user-friendly web interface.

## User Preferences

Preferred communication style: Simple, everyday language.
Real-time logging preference: User wants logs to update automatically without manual refresh.
Preferred operation duration: 24-hour continuous operation for promotional campaigns.

## System Architecture

### Frontend Architecture
- **Framework**: HTML templates with Bootstrap 5 dark theme for responsive UI
- **JavaScript**: Vanilla JavaScript with class-based architecture for bot control
- **Styling**: Custom CSS with Bootstrap overrides, featuring dark theme and modern card-based layout
- **Real-time Updates**: JavaScript intervals for status polling and log refreshing

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite with configurable database URL support
- **Models**: Three main entities - BotLog (logging), BotConfig (configuration), BotStatus (runtime status)
- **Service Layer**: Dedicated TelegramBotService class for bot operations using async/await pattern
- **Threading**: Background threading for bot operations to prevent blocking the web interface

### Bot Service Architecture
- **Client**: Telethon library for Telegram API integration
- **Async Operations**: Asyncio event loop for handling Telegram operations
- **State Management**: Thread-safe bot status tracking with database persistence
- **Error Handling**: Comprehensive error handling for Telegram API limitations (flood wait, admin requirements)

### Data Storage
- **Primary Database**: SQLite with connection pooling and ping checks
- **Models**:
  - BotLog: Timestamped logging with severity levels
  - BotConfig: Key-value configuration storage
  - BotStatus: Runtime status tracking with metrics
- **Session Management**: Flask sessions with configurable secret key

### API Design
- **RESTful Endpoints**: JSON API for bot control operations
- **Status Endpoint**: Real-time bot status and metrics
- **Logs Endpoint**: Paginated log retrieval with filtering
- **Control Endpoints**: Start/stop bot operations with response feedback

## External Dependencies

### Telegram Integration
- **Telethon**: Python Telegram client library for API interactions
- **API Credentials**: Requires TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_PHONE environment variables
- **Group Targeting**: Hardcoded list of target Telegram group usernames

### Web Framework Dependencies
- **Flask**: Core web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Bootstrap 5**: Frontend CSS framework with dark theme
- **Font Awesome**: Icon library for UI elements

### Infrastructure
- **ProxyFix**: Werkzeug middleware for proxy header handling
- **Environment Variables**: Configuration through environment variables for credentials and database URL
- **Logging**: Python's built-in logging system for application monitoring

### Runtime Dependencies
- **Threading**: Python threading for concurrent bot operations
- **Asyncio**: Asynchronous programming for Telegram API calls
- **Queue**: Thread-safe communication between web interface and bot service