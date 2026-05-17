Voice Messaging System Project Documentation
Abstract
This project is a cloud-based voice messaging system that allows users to record audio through a
browser, upload it to a backend server, store it in cloud storage, and send real-time SMS
notifications with access links. The system removes dependency on traditional phone call voicemail
systems and provides a fully web-based solution.
Tech Stack
Frontend HTML, JavaScript, MediaRecorder API
Backend Python, Flask
Database & Storage Supabase (PostgreSQL + Storage)
Messaging Twilio SMS
Tunneling ngrok
Features Included
- Browser-based voice recording - Cloud storage of audio files - Database storage of metadata -
SMS notification with voice link - Real-time backend processing
Workflow
User opens web app ® Records voice ® Audio sent to Flask backend ® Stored in Supabase ®
SMS sent via Twilio ® User receives link ® Plays voice message.
System Architecture
Frontend (Browser UI) ¯ Flask Backend API ¯ Supabase Storage + Database ¯ Twilio SMS
Notification ¯ User Access via Link
