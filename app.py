import streamlit as st
from groq import Groq
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

st.set_page_config(page_title="HR Mail Assistant", page_icon="📧", layout="wide")
st.title("📧 HR Mail Assistant")
st.markdown("AI-powered email reader and auto-reply generator for HR teams")

client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_emails(service, max_results=10):
    results = service.users().messages().list(
        userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
    messages = results.get('messages', [])
    emails = []
    for msg in messages:
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = txt['payload']
        headers = payload['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
        elif 'body' in payload:
            data = payload['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        emails.append({
            'id': msg['id'],
            'subject': subject,
            'sender': sender,
            'body': body[:500]
        })
    return emails

def generate_reply(subject, sender, body):
    prompt = f"""You are a professional HR assistant. Generate a polite, professional email reply.

Original Email:
From: {sender}
Subject: {subject}
Body: {body}

Write a professional HR reply that:
- Acknowledges the email
- Provides a helpful response
- Is concise and professional
- Ends with a professional sign-off

Reply:"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_email(service, to, subject, body):
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = f"Re: {subject}"
    message.attach(MIMEText(body, 'plain'))
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()

if 'service' not in st.session_state:
    st.session_state.service = None
if 'emails' not in st.session_state:
    st.session_state.emails = []

col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("⚙️ Controls")
    if st.button("🔐 Connect Gmail", use_container_width=True):
        with st.spinner("Authenticating..."):
            st.session_state.service = authenticate_gmail()
            st.success("Connected!")

    if st.session_state.service:
        if st.button("📬 Fetch Emails", use_container_width=True):
            with st.spinner("Fetching emails..."):
                st.session_state.emails = get_emails(st.session_state.service)
                st.success(f"Fetched {len(st.session_state.emails)} emails!")

with col2:
    st.subheader("📨 Inbox")
    if not st.session_state.emails:
        st.info("Connect Gmail and fetch emails to get started.")
    else:
        for i, email in enumerate(st.session_state.emails):
            with st.expander(f"📩 {email['subject']} — From: {email['sender']}"):
                st.markdown(f"**From:** {email['sender']}")
                st.markdown(f"**Subject:** {email['subject']}")
                st.markdown(f"**Preview:** {email['body'][:200]}...")

                if st.button(f"🤖 Generate AI Reply", key=f"gen_{i}"):
                    with st.spinner("Generating reply..."):
                        reply = generate_reply(
                            email['subject'],
                            email['sender'],
                            email['body']
                        )
                        st.session_state[f"reply_{i}"] = reply

                if f"reply_{i}" in st.session_state:
                    st.markdown("**AI Generated Reply:**")
                    edited_reply = st.text_area(
                        "Edit before sending:",
                        value=st.session_state[f"reply_{i}"],
                        key=f"edit_{i}",
                        height=200
                    )
                    if st.button(f"📤 Send Reply", key=f"send_{i}"):
                        sender_email = email['sender'].split('<')[-1].replace('>', '').strip()
                        send_email(
                            st.session_state.service,
                            sender_email,
                            email['subject'],
                            edited_reply
                        )
                        st.success("Reply sent!")