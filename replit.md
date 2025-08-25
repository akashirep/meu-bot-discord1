# FenixBot - Discord Ticket System

## Overview

FenixBot is a Discord bot designed to provide ticket management functionality for Discord servers. The bot allows users to create tickets for product requests and partnerships through interactive modals and buttons. It features a web dashboard for monitoring bot status, automated restart capabilities, and comprehensive logging. The system is designed to run on Replit with a keep-alive service to maintain continuous operation.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Architecture
The application follows a modular architecture with clear separation of concerns:

- **Main Application (`main.py`)**: Contains the BotManager class that handles bot lifecycle, auto-restart functionality, and error recovery
- **Bot Core (`bot.py`)**: Implements the FenixBot class extending discord.py's commands.Bot with ticket-specific functionality
- **Keep-Alive Service (`keep_alive.py`)**: Flask web server providing health monitoring and preventing Replit from sleeping

### Configuration Management
- JSON-based configuration system (`config.json`) for persistent storage of:
  - Category IDs for products and partnerships
  - Log channel configuration
  - Staff role assignments
  - Ticket counter tracking
- Environment variable support for sensitive data like bot tokens and prefixes

### User Interface Components
- Discord UI components using discord.py's View, Button, and Modal classes
- Interactive ticket creation forms with text inputs for product details
- Button-based navigation for different ticket types (products vs partnerships)

### Error Handling and Monitoring
- Comprehensive logging system with file and console output
- Automatic restart mechanism for bot failures
- Health check endpoints for external monitoring
- Status tracking including uptime, restart count, and guild statistics

### Web Dashboard
- Bootstrap-based responsive web interface
- Real-time status monitoring via REST API endpoints
- Visual status indicators and bot metrics display
- Auto-refreshing dashboard for continuous monitoring

## External Dependencies

### Core Framework
- **Discord.py**: Primary library for Discord bot functionality and API interaction
- **Flask**: Lightweight web framework for the keep-alive service and dashboard

### Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework for responsive web design
- **Font Awesome 6.4.0**: Icon library for visual elements

### Infrastructure
- **Replit Platform**: Cloud hosting environment with specific keep-alive requirements
- **File System Storage**: Local JSON files for configuration persistence and logging

### Python Standard Libraries
- **asyncio**: Asynchronous programming support for Discord bot operations
- **threading**: Multi-threading for concurrent web server and bot execution
- **logging**: Comprehensive logging and error tracking
- **json**: Configuration file parsing and data serialization
- **datetime**: Timestamp management and uptime calculations