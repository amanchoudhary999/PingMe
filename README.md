# PingMe – Real-Time Chat Application (Django + WebSockets)

PingMe is a lightweight real-time group chat application built using **Django**, **Channels**, and **WebSockets**.  
This project was developed as an **internship learning project**, focusing on authentication, live messaging, invite links, and basic room management with admin controls.

---

## 🚀 Features

### 🔐 Authentication
- Login system using Django sessions  
- Secure CSRF-protected forms  
- Support for redirect using `?next=` (especially for invite links)  
- Access restricted to authenticated users  

### 💬 Real-Time Chat
- WebSocket-based messaging using **Django Channels**
- Instant broadcast of messages to room members  
- Loads recent chat history through REST API  

### 🏠 Chat Rooms
- Create chat rooms  
- Enter existing rooms  
- Invite users via unique URLs (`?invite=1`)  
- Automatic member registration on first join  

### 👥 Room Member Management (Inside Chat)
- View all room members  
- **Admin-only actions:**  
  - Kick a user  
  - Transfer admin  
  - Delete room  
- **Available to all users:**  
  - Leave room  

### 📜 Logging System
- Logs major room events:  
  - invite  
  - join  
  - leave  
  - admin transfer  
- Useful for future auditing or UI enhancements  

---

## 🛠️ Technologies Used

- **Python**  
- **Django Framework**  
- **Django Channels** (WebSockets)  
- **Daphne** (ASGI server)  
- **SQLite** (simple DB for intern project)  
- **HTML, CSS, JavaScript**

---

## 🌐 Deployment (Render.com – No Redis Version)

This project uses the **InMemoryChannelLayer**, suitable for demos and internship projects.

### Build Commands


## 🗂️ Project Structure

