# HR Mail Assistant

An AI-powered email automation tool that reads Gmail inbox, understands email content, and generates professional HR replies using LLM — all from a clean web interface.

## Demo
Run locally (see instructions below) — Gmail OAuth required

## Features
- Secure Gmail authentication via OAuth 2.0
- Fetch and display inbox emails in real-time
- AI-generated professional replies using Groq LLM (LLaMA 3.3)
- Edit AI reply before sending
- Send reply directly from Gmail via API
- Clean Streamlit web interface

## Tech Stack
- Python
- Streamlit
- Gmail API (Google OAuth 2.0)
- Groq API (LLaMA 3.3-70b)
- Google API Python Client

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/Pranavvvv-21/HR-Mail-Assistant.git
cd HR-Mail-Assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your credentials
- Download credentials.json from Google Cloud Console with Gmail API enabled
- Get your Groq API key from console.groq.com
- Replace YOUR_GROQ_API_KEY_HERE in app.py with your actual key

### 4. Run the app
```bash
streamlit run app.py
```

## Project Structure
```
hr-mail-assistant/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── credentials.json    # Gmail OAuth credentials (not committed)
└── token.json          # Auto-generated after first login (not committed)
```

## Security Note
Never commit your credentials.json or token.json to GitHub.
Always use environment variables or placeholders for API keys.

## Author
Pranav M
