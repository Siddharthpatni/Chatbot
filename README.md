# Service Chatbot with Trivia Game

## Overview

This project implements a **React-based chatbot interface** backed by a **Python (Flask/FastAPI) API**. It provides:

* General Q\&A for university services.
* An interactive trivia game with scoring and feedback.
* Knowledge base management (add/remove questions, bulk CSV upload).
* Multi-tab interface for Chat, Trivia, Manage, and Help.
* A demo video (`final.mp4`) showcasing the application workflow.

The frontend (`App.js`) handles chat rendering, trivia gameplay, knowledge management, and file uploads. The backend (`app.py`) provides REST APIs for question answering, trivia game logic, and CSV ingestion.

---

## Features

### 1. Chat Interface

* Default chatbot greets the user and responds via `/api/ask`.
* Timestamped messages with sender differentiation (user vs. bot).
* Clear chat option.

### 2. Trivia Game

* Start trivia with selectable lengths (5, 10, 15 questions).
* Multiple-choice format (A/B/C/D).
* Real-time scoring and instant feedback.
* Automatic game-over summary with percentage results.
* End trivia at any time.

### 3. Knowledge Base Management

* Add questions manually (form with Q/A).
* Remove existing questions from dropdown.
* Upload CSV file with bulk questions via `/api/upload`.

**CSV Format:**

```csv
question,answer1,answer2,answer3,answer4
"What is the capital of Germany?",Berlin,Hamburg,Munich,Cologne
```

### 4. Help Tab

* Usage guide for each feature.
* File format specifications.

---

## Tech Stack

* **Frontend:** React (Hooks, state management, tab-based navigation)
* **Backend:** Python (Flask or FastAPI, REST endpoints)
* **Storage:** Questions persisted via backend service
* **File Handling:** CSV upload for bulk question import

---

## Installation

### Backend

1. Navigate to the backend folder.
2. Install dependencies:

   ```bash
   pip install flask fastapi uvicorn pandas
   ```
3. Run the backend server:

   ```bash
   python app.py
   ```

   Default port: `5040`

### Frontend

1. Navigate to the frontend folder.
2. Install dependencies:

   ```bash
   npm install
   ```
3. Run the React app:

   ```bash
   npm start
   ```

   Default port: `3000`

---

## API Endpoints

### Chat

* `POST /api/ask` → `{ question: "..." }` → `{ response: "..." }`

### Trivia

* `POST /api/trivia/start` → Starts a new trivia session.
* `POST /api/trivia/answer` → Submits an answer.
* `POST /api/trivia/end` → Ends trivia and returns final score.

### Knowledge Base

* `GET /api/question/list` → Returns all questions.
* `POST /api/question/add` → Add a question.
* `POST /api/question/remove` → Remove a question.
* `POST /api/upload` → Upload CSV with bulk questions.

---

## Demo

A walkthrough of the chatbot and trivia game is shown in `final.mp4`. The video demonstrates:

* Starting a chat.
* Playing trivia with real-time feedback.
* Managing knowledge base (add, remove, upload).
* Viewing help section.

---

## Project Structure

```
├── app.py        # Backend server (Flask/FastAPI)
├── App.js        # React frontend logic
├── App.css       # Stylesheet
├── final.mp4     # Demo video
```

---

## Future Improvements

* Authentication for admin functions.
* Persistent database (SQLite/Postgres) instead of in-memory.
* Improved error handling and UI notifications.
* Question categories and difficulty levels.

---

## License

MIT License. Free to use and modify.
