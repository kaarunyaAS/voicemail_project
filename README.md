# 🎙️ Voice Messaging System

A cloud-based voice messaging web application that allows users to record audio directly from the browser, upload it to cloud storage, and send SMS notifications with a playable voice message link.

---

## 🚀 Features

- 🎤 Browser-based voice recording
- ☁️ Cloud storage for audio files
- 🗄️ Metadata storage using Supabase
- 📩 SMS notifications using Twilio
- ⚡ Real-time backend processing
- 🔗 Shareable voice message links

---

## 🛠️ Tech Stack

### Frontend
- HTML
- JavaScript
- MediaRecorder API

### Backend
- Python
- Flask

### Database & Storage
- Supabase (PostgreSQL + Storage)

### Messaging
- Twilio SMS API

### Development Tool
- ngrok

---

## ⚙️ Workflow

1. User opens the web application  
2. Records a voice message  
3. Audio is sent to the Flask backend  
4. Audio file is uploaded to Supabase storage  
5. Metadata is stored in the database  
6. Twilio sends an SMS with the voice message link  
7. Recipient opens the link and listens to the message  

---

## 🏗️ System Architecture

```text
Browser UI
    ↓
Flask Backend API
    ↓
Supabase Storage + Database
    ↓
Twilio SMS Notification
    ↓
User Access via Link
