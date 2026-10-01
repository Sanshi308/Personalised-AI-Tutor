# Personalised AI Tutor for Learning AI — Vector Vision

An adaptive AI learning companion for AI/ML students. It follows the loop:

**Learn → Practice → Diagnose → Adapt → Improve**

## Features
- Level-aware AI Tutor: Beginner / Intermediate / Advanced
- "Explain Simpler", "Give Example", and "Quiz Me" actions
- AI-generated 5-question quizzes
- Instant scoring and explanations
- Weak-topic diagnosis from recent quiz performance
- Personalised next-step recommendations
- Progress dashboard
- Persistent learner history using SQLite
- Gemini API integration through FastAPI
- Clean Next.js interface designed for a hackathon demo

## Architecture

Student → Next.js UI → FastAPI → Gemini AI
                         ↓
                       SQLite
             profile / quiz scores / history

## Requirements
- Node.js 20+
- Python 3.11+
- Gemini API key

## 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Run:

```bash
uvicorn main:app --reload --port 8000
```

## 2. Frontend

Open a second terminal:

```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

Open http://localhost:3000

## Demo flow
1. Open Dashboard.
2. Choose a level and topic.
3. Ask: "Explain gradient descent like I'm a beginner."
4. Click "Explain Simpler" or "Give Example".
5. Click "Quiz Me".
6. Complete 5 questions.
7. Submit the quiz.
8. Show the score, weak topic, and recommendation on the dashboard.

## Important
Never commit `.env` or API keys to GitHub. `.gitignore` already excludes them.

## Hackathon story
A generic chatbot gives an answer. This product closes the learning loop:
**explanation → practice → diagnosis → adaptive recommendation**.

The student's selected level and recent performance influence the tutor's responses and recommendations.
