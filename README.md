# 🤖 X - Agent

An AI-powered Twitter (X) agent built using **Python**, **Tweepy**, and **Google Gemini AI**. This bot is optimized for the X API Free Tier, featuring smart rate-limit tracking and a "Copilot" mode for human-in-the-loop content creation.

---

## ✨ Key Features

- **🚀 Copilot Mode**: Generate high-quality AI tweets based on a topic and approve/edit them before they go live.
- **⚡ Auto-Post**: Quickly post AI-generated content to a specific topic with a single command.
- **📊 Stats Dashboard**: Real-time tracking of monthly posts to stay within X API Free Tier limits (500 posts/month).
- **🧠 Gemini Powered**: Uses `gemini-1.5-flash` for fast, creative, and context-aware tweet generation.
- **🛡️ Rate Limit Protection**: Built-in safeguards to prevent API overages.
- **📂 State Persistence**: Uses SQLite to keep track of posted tweets and monthly statistics.

---

## 🛠️ Tech Stack

- **Language**: Python 3.8+
- **Twitter API**: [Tweepy](https://www.tweepy.org/)
- **AI Model**: [Google Gemini AI](https://aistudio.google.com/)
- **Database**: SQLite3
- **Env Management**: python-dotenv

---

## 🚀 Getting Started

### Prerequisites

1.  **Python 3.8+** installed on your system.
2.  **X Developer Account**: Create an app on the [X Developer Portal](https://developer.x.com/) to get your API keys.
3.  **Google AI Studio Key**: Get a free API key for Gemini from [Google AI Studio](https://aistudio.google.com/).

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/x-bot-agent.git
    cd x-bot-agent
    ```

2.  **Set up a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r x_bot_agent/requirements.txt
    ```

---

## ⚙️ Configuration

Copy the `.env.example` file to `.env` inside the `x_bot_agent` directory and fill in your credentials:

```bash
cp x_bot_agent/.env.example x_bot_agent/.env
```

**Required Variables:**
- `X_API_KEY`: Your X Consumer Key.
- `X_API_SECRET_KEY`: Your X Consumer Secret.
- `X_ACCESS_TOKEN`: Your X Access Token.
- `X_ACCESS_TOKEN_SECRET`: Your X Access Token Secret.
- `GEMINI_API_KEY`: Your Google AI Studio API key.

---

## 📖 Usage

Navigate to the `x_bot_agent` directory:
```bash
cd x_bot_agent
```

### 1. Copilot Mode (Recommended)
Generate a tweet and approve it before posting:
```bash
python main.py copilot "the future of agentic AI"
```

### 2. Auto-Post
Post a tweet directly without approval:
```bash
python main.py post "python coding tips" --auto
```

### 3. Check Statistics
View your monthly usage and remaining post limit:
```bash
python main.py stats
```

---

## 📁 Project Structure

```text
x-bot-agent/
├── x_bot_agent/
│   ├── main.py          # CLI Entry point
│   ├── config.py        # Configuration & API clients
│   ├── post_tweet.py    # Posting logic & AI generation
│   ├── database.py      # SQLite operations
│   └── .env             # Your secrets (not tracked)
├── .venv/               # Virtual environment
└── requirements.txt     # Python dependencies
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
