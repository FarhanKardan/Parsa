# Parsa Employee/Bot Management System

A Telegram bot project for managing employee leave requests, payment plans, and inventory boxes targeting Persian-speaking teams. The bot streamlines HR, payment, and inventory processes using a conversational interface and connects to a MongoDB backend.

## Features

- **Employee Leave Management:**
  - Request/Approve/Reject leaves with date and reason capture.
  - Managers notified & employees updated on request status.
  - Validations for permissions and duplicate requests.
- **Payment Calculator:**
  - Mobile phone plans with dynamic interest calculation based on payment %, guarantee type, term length.
  - Interactive, step-by-step plan selection in Telegram chat.
- **Inventory/Box Management:**
  - Add, update, lookup, and remove inventory boxes.
  - Box categories and full details stored in MongoDB.
- **Admin Tools:**
  - Add, edit, and remove supported mobile models and prices.

## Project Structure

```
Parsa/
├── bot.py                     # Main bot entry point
├── config.py                  # Environment, tokens, and employee configuration
├── requirements.txt           # Python dependencies
├── db_operations 2.py         # MongoDB persistence for leave and box modules
├── modules/
│   ├── admin.py               # Mobile model management handlers
│   ├── box.py                 # Inventory (box) conversation and DB logic
│   ├── leave_request.py       # Leave request conversation, manager UX
│   ├── payment_calculator.py  # Installment/payment calculation logic
│   └── payment.py             # Payment plan handler
├── utils.py                   # Shared utility logic
```

## Getting Started

### Prerequisites
- Python 3.10+
- [MongoDB](https://www.mongodb.com/) running (default: `localhost:27017`)
- A valid Telegram Bot Token ([see instructions](https://core.telegram.org/bots#6-botfather))

### Installation
1. Clone the repo:
    ```bash
    git clone <yourrepo-url>
    cd Parsa
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Configure your environment:
    - Edit `config.py` with your actual Telegram bot token and employees info as appropriate.
4. Start MongoDB if not already running.
5. Run the bot:
    ```bash
    python bot.py
    ```

## Docker Usage

### Build the image
```bash
docker build -t parsa-bot .
```

### Run the container
```bash
docker run --env BOT_TOKEN=your_actual_token_here -p 8443:8443 parsa-bot
```

- By default MongoDB is assumed to be available on the host network at `localhost:27017`, or you can connect your container to an external Mongo instance.
- For production, use proper Secrets management for the bot token.

## Environment Variables
- `BOT_TOKEN`: Your Telegram bot token. (Set in `config.py` or via env var for Docker)

## License
MIT License
