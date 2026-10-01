import json
import os
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# ENVIRONMENT
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Always load .env from backend folder
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

# ---------------------------------------------------------
# GEMINI
# ---------------------------------------------------------

try:
    from google import genai
except Exception:
    genai = None


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

DB_PATH = BASE_DIR / "tutor.db"


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            level TEXT NOT NULL,
            streak INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            level TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )

    row = conn.execute(
        "SELECT id FROM profile WHERE id=1"
    ).fetchone()

    if not row:
        conn.execute(
            """
            INSERT INTO profile(id, name, level, streak)
            VALUES(1, ?, ?, ?)
            """,
            ("Learner", "Beginner", 0),
        )

    conn.commit()
    conn.close()


init_db()


# ---------------------------------------------------------
# FASTAPI
# ---------------------------------------------------------

app = FastAPI(
    title="Personalised AI Tutor API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# MODELS
# ---------------------------------------------------------

class ProfileUpdate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=50
    )

    level: str = Field(
        pattern="^(Beginner|Intermediate|Advanced)$"
    )


class TutorRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=3000
    )

    topic: str = "Machine Learning"

    level: str = Field(
        default="Beginner",
        pattern="^(Beginner|Intermediate|Advanced)$"
    )

    action: str = "explain"

    recent_performance: Optional[List[dict]] = None


class QuizRequest(BaseModel):
    topic: str = "Machine Learning"

    level: str = Field(
        default="Beginner",
        pattern="^(Beginner|Intermediate|Advanced)$"
    )


class QuizSubmit(BaseModel):
    topic: str
    level: str
    score: int
    total: int


# ---------------------------------------------------------
# GEMINI HELPER
# ---------------------------------------------------------

def gemini_text(prompt: str) -> str:

    # If package/API key is missing
    if not API_KEY or genai is None:
        return ""

    try:
        client = genai.Client(
            api_key=API_KEY
        )

        # Retry temporary Gemini failures
        last_error = None

        for attempt in range(3):

            try:
                response = client.models.generate_content(
                    model=MODEL,
                    contents=prompt
                )

                text = getattr(
                    response,
                    "text",
                    None
                )

                if text:
                    return text.strip()

                return ""

            except Exception as exc:
                last_error = exc

                error_text = str(exc)

                # Retry only temporary service errors
                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                ):
                    if attempt < 2:
                        time.sleep(2)
                        continue

                break

        print(
            f"Gemini error: {last_error}"
        )

        return ""

    except Exception as exc:
        print(
            f"Gemini client error: {exc}"
        )
        return ""


# ---------------------------------------------------------
# FALLBACK TUTOR
# ---------------------------------------------------------

def fallback_tutor(
    message: str,
    topic: str,
    level: str,
    action: str
) -> str:

    msg = message.lower().strip()
    topic_lower = topic.lower()

    # -----------------------------------------------------
    # QUIZ REQUEST
    # -----------------------------------------------------

    if (
        "quiz" in msg
        or "test me" in msg
        or "questions" in msg
    ):
        return f"""
# {topic}

## Quick Quiz

Since you are learning at the **{level}** level, try these questions.

### Question 1
What is the main purpose of {topic}?

A. Learning patterns from data  
B. Deleting files  
C. Replacing the CPU  
D. Formatting a disk

**Answer:** A

### Question 2
Why is {topic} useful in Machine Learning?

A. It helps a model learn or make predictions  
B. It only stores files  
C. It controls the keyboard  
D. It replaces RAM

**Answer:** A

### Question 3
What should a learner do after attempting a question?

A. Check the reasoning behind the answer  
B. Ignore the answer  
C. Restart the computer  
D. Delete the dataset

**Answer:** A

### Quick Check

Can you explain **{topic}** in one sentence using your own words?
"""

    # -----------------------------------------------------
    # PRACTICAL EXAMPLE
    # -----------------------------------------------------

    if (
        "practical" in msg
        or "real world" in msg
        or "real-world" in msg
        or "example" in msg
    ):
        return f"""
# Practical Example: {topic}

Imagine you are building a system that predicts whether a student will pass an exam.

The system receives information such as:

- Hours studied
- Attendance
- Previous marks
- Assignment scores

The Machine Learning model uses these inputs to find patterns.

For example:

**More study + good attendance → higher probability of passing**

This is how {topic} can be connected to a real-world Machine Learning problem.

### Simple idea

**Input → Model → Prediction**

### Quick Check

Can you think of one real-world application of **{topic}**?
"""

    # -----------------------------------------------------
    # SIMPLER EXPLANATION
    # -----------------------------------------------------

    if (
        "simple" in msg
        or "simpler" in msg
        or action == "simpler"
    ):
        return f"""
# {topic} — Super Simple Explanation

Think of **{topic}** as a tool that helps a computer learn something from data.

### Easy idea

**Data → Learning → Prediction**

The computer looks at examples, finds patterns, and then uses those patterns to make a prediction or decision.

### Everyday analogy

Imagine teaching a child to recognize apples.

You show the child many examples:

🍎 red apple  
🍏 green apple  
🍎 small apple

After seeing enough examples, the child learns the pattern.

Machine Learning works in a similar way.

### Quick Check

Explain **{topic}** in your own words in one sentence.
"""

    # -----------------------------------------------------
    # GRADIENT DESCENT
    # -----------------------------------------------------

    if "gradient descent" in topic_lower:

        return """
# Gradient Descent

Gradient Descent is an optimization algorithm used to reduce the error of a Machine Learning model.

## Simple analogy

Imagine standing on a foggy hill.

You cannot see the bottom.

You check which direction goes downhill and take a small step.

Then you check again and take another step.

You repeat this until you reach a low point.

That is basically Gradient Descent.

### In Machine Learning

- **Hill:** Error/Loss function
- **Slope:** Gradient
- **Step size:** Learning rate
- **Bottom:** Minimum error

### Formula

new value = old value - learning rate × gradient

### Quick Check

What happens if the learning rate is too large?
"""

    # -----------------------------------------------------
    # LINEAR REGRESSION
    # -----------------------------------------------------

    if "linear regression" in topic_lower:

        return """
# Linear Regression

Linear Regression is used to predict a numerical value.

For example:

**House size → House price**

The model tries to find the best-fitting straight line through the data.

The basic equation is:

y = mx + c

Where:

- y = predicted value
- x = input
- m = slope
- c = intercept

### Example

If house size increases, the predicted house price may also increase.

### Quick Check

Is Linear Regression normally used to predict a number or a category?
"""

    # -----------------------------------------------------
    # CLASSIFICATION
    # -----------------------------------------------------

    if "classification" in topic_lower:

        return """
# Classification

Classification is a Machine Learning task where the output belongs to a category.

### Example

Email → Spam or Not Spam

The model learns from previous examples and predicts which category a new example belongs to.

### Other examples

- Disease → Positive / Negative
- Student → Pass / Fail
- Image → Cat / Dog

### Simple idea

**Input → Classifier → Category**

### Quick Check

Is predicting "Spam" or "Not Spam" a classification problem?
"""

    # -----------------------------------------------------
    # NEURAL NETWORKS
    # -----------------------------------------------------

    if "neural network" in topic_lower:

        return """
# Neural Networks

A Neural Network is a Machine Learning model inspired by the way connected neurons process information.

It contains layers:

**Input Layer → Hidden Layers → Output Layer**

For example, for image recognition:

Image pixels → Neural Network → Predicted class

Each connection has a weight.

During training, the network changes these weights to reduce its error.

### Simple analogy

Imagine many students working together.

Each student processes some information and passes the result to the next student.

Together they solve the problem.

### Quick Check

What are the three basic types of layers in a neural network?
"""

    # -----------------------------------------------------
    # OVERFITTING
    # -----------------------------------------------------

    if "overfitting" in topic_lower:

        return """
# Overfitting

Overfitting happens when a Machine Learning model learns the training data too closely.

It performs very well on training data but poorly on new/unseen data.

### Example

Imagine a student memorizes the exact answers to one question paper.

They may score very well on that paper.

But if the teacher changes the questions, the student struggles.

That is similar to overfitting.

### Simple idea

**Training performance: High**

**New-data performance: Low**

### Quick Check

Why is overfitting bad for a Machine Learning model?
"""

    # -----------------------------------------------------
    # GENERAL FALLBACK
    # -----------------------------------------------------

    return f"""
# {topic}

You asked:

**{message}**

For a **{level}** learner, start with the basic idea.

## What is {topic}?

{topic} is a concept used in Machine Learning to help a model learn patterns from data and make useful predictions or decisions.

## How to study it

1. Understand the definition.
2. Understand one real-world example.
3. Learn the important terms.
4. Understand the basic formula or process.
5. Practise with questions.

### Quick Check

Can you explain **{topic}** in one sentence using your own words?
"""


# ---------------------------------------------------------
# FALLBACK QUIZ
# ---------------------------------------------------------

def fallback_quiz(
    topic: str,
    level: str
):

    topic_lower = topic.lower()

    # Gradient Descent quiz
    if "gradient descent" in topic_lower:

        return [
            {
                "question": "What is the main purpose of Gradient Descent?",
                "options": [
                    "Minimize the loss/error",
                    "Increase the dataset size",
                    "Delete training data",
                    "Increase computer memory"
                ],
                "answer": 0,
                "explanation": "Gradient Descent adjusts model parameters to reduce the loss."
            },
            {
                "question": "What does the learning rate control?",
                "options": [
                    "The size of each update step",
                    "The number of classes",
                    "The dataset size",
                    "The number of CPUs"
                ],
                "answer": 0,
                "explanation": "Learning rate controls how large each parameter update is."
            },
            {
                "question": "What does the gradient tell us?",
                "options": [
                    "The direction of greatest increase in loss",
                    "The number of training examples",
                    "The model accuracy only",
                    "The size of the dataset"
                ],
                "answer": 0,
                "explanation": "The gradient gives the direction in which the loss increases most rapidly."
            },
            {
                "question": "Why do we subtract the gradient?",
                "options": [
                    "To move toward lower loss",
                    "To increase the error",
                    "To delete the model",
                    "To increase memory"
                ],
                "answer": 0,
                "explanation": "Moving opposite to the gradient takes us toward lower loss."
            },
            {
                "question": "What can happen if the learning rate is too large?",
                "options": [
                    "The algorithm may overshoot the minimum",
                    "The computer shuts down",
                    "The dataset disappears",
                    "The model always becomes perfect"
                ],
                "answer": 0,
                "explanation": "A very large learning rate can cause unstable updates or overshooting."
            }
        ]

    # General fallback
    return [
        {
            "question": f"What is the main purpose of {topic}?",
            "options": [
                "Learning useful patterns from data",
                "Deleting data",
                "Replacing the CPU",
                "Formatting a disk"
            ],
            "answer": 0,
            "explanation": f"{topic} is used as part of Machine Learning to learn from data."
        },
        {
            "question": "Which dataset is commonly used to evaluate generalisation?",
            "options": [
                "Test set",
                "Keyboard buffer",
                "BIOS",
                "Cache only"
            ],
            "answer": 0,
            "explanation": "A test set is used to evaluate performance on unseen data."
        },
        {
            "question": "What is a model parameter?",
            "options": [
                "A value learned during training",
                "A file name",
                "A screen resolution",
                "A network cable"
            ],
            "answer": 0,
            "explanation": "Parameters are values learned by the model during training."
        },
        {
            "question": "Why do we use validation data?",
            "options": [
                "To tune and compare model choices",
                "To turn off the computer",
                "To format the disk",
                "To increase RAM"
            ],
            "answer": 0,
            "explanation": "Validation data helps select models and tune hyperparameters."
        },
        {
            "question": "What is overfitting?",
            "options": [
                "Good training performance but poor unseen-data performance",
                "No training",
                "A hardware failure",
                "A database backup"
            ],
            "answer": 0,
            "explanation": "Overfitting occurs when a model fits training-specific patterns too closely."
        }
    ]


# ---------------------------------------------------------
# HEALTH
# ---------------------------------------------------------

@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "ai_configured": bool(API_KEY),
        "model": MODEL
    }


# ---------------------------------------------------------
# PROFILE
# ---------------------------------------------------------

@app.get("/api/profile")
def get_profile():

    conn = db()

    row = conn.execute(
        "SELECT * FROM profile WHERE id=1"
    ).fetchone()

    conn.close()

    return dict(row)


@app.put("/api/profile")
def update_profile(
    payload: ProfileUpdate
):

    conn = db()

    conn.execute(
        """
        UPDATE profile
        SET name=?, level=?
        WHERE id=1
        """,
        (
            payload.name,
            payload.level
        )
    )

    conn.commit()

    row = conn.execute(
        "SELECT * FROM profile WHERE id=1"
    ).fetchone()

    conn.close()

    return dict(row)


# ---------------------------------------------------------
# STATS
# ---------------------------------------------------------

@app.get("/api/stats")
def stats():

    conn = db()

    attempts = conn.execute(
        """
        SELECT *
        FROM quiz_attempts
        ORDER BY created_at DESC
        """
    ).fetchall()

    profile = conn.execute(
        "SELECT * FROM profile WHERE id=1"
    ).fetchone()

    conn.close()

    attempts = [
        dict(x)
        for x in attempts
    ]

    total = len(attempts)

    avg = (
        round(
            sum(
                (a["score"] / max(a["total"], 1)) * 100
                for a in attempts
            ) / total
        )
        if total
        else 0
    )

    topic_scores = {}

    for a in attempts:

        topic_scores.setdefault(
            a["topic"],
            []
        ).append(
            (a["score"] / max(a["total"], 1)) * 100
        )

    topic_summary = [
        {
            "topic": topic,
            "score": round(
                sum(scores) / len(scores)
            ),
            "attempts": len(scores)
        }
        for topic, scores
        in topic_scores.items()
    ]

    topic_summary.sort(
        key=lambda x: x["score"]
    )

    weak = (
        topic_summary[0]
        if topic_summary
        else {
            "topic": "Gradient Descent",
            "score": 0,
            "attempts": 0
        }
    )

    return {
        "name": profile["name"],
        "level": profile["level"],
        "avg_score": avg,
        "quizzes": total,
        "weak_topic": weak,
        "topics": topic_summary,
        "recent": attempts[:6]
    }


# ---------------------------------------------------------
# TUTOR
# ---------------------------------------------------------

@app.post("/api/tutor")
def tutor(
    payload: TutorRequest
):

    message = payload.message.strip()

    performance = json.dumps(
        payload.recent_performance or [],
        indent=2
    )

    # -----------------------------------------------------
    # Detect what the student actually wants
    # -----------------------------------------------------

    msg = message.lower()

    if (
        "quiz" in msg
        or "test me" in msg
        or "mcq" in msg
    ):
        action_instruction = """
The student is explicitly asking for a QUIZ.

Do NOT give a generic explanation.

Create a short quiz with multiple-choice questions.
Include the answer and a short explanation after each question.
"""

    elif (
        "practical" in msg
        or "real world" in msg
        or "real-world" in msg
        or "example" in msg
    ):
        action_instruction = """
The student wants a practical/real-world example.

Give one clear practical example.
Explain it step-by-step.
Connect it directly to the selected topic.
"""

    elif (
        "simple" in msg
        or "simpler" in msg
        or payload.action == "simpler"
    ):
        action_instruction = """
Explain the concept in extremely simple language.

Use:
1. Everyday analogy
2. Simple definition
3. Tiny example
4. Quick Check
"""

    elif payload.action == "example":

        action_instruction = """
Give a concrete example and explain it step-by-step.
"""

    else:

        action_instruction = """
Explain the concept clearly.
Start with intuition before technical details.
"""


    # -----------------------------------------------------
    # GEMINI PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are Vector Tutor, a personalised AI tutor.

Student level:
{payload.level}

Selected topic:
{payload.topic}

Student's recent performance:
{performance}

Student's exact request:
{message}

IMPORTANT:
Answer the student's EXACT request.

Do not change the topic.

Do not ignore words such as:
- quiz
- example
- practical
- simpler
- explain
- compare

Required teaching style:
{action_instruction}

Rules:
- Match the student's level exactly.
- Be clear and educational.
- Use simple language when possible.
- Do not invent student performance.
- Use headings and bullet points when useful.
- If mathematics is necessary, explain every symbol.
- End with a "Quick Check" when appropriate.
"""

    answer = gemini_text(prompt)

    # -----------------------------------------------------
    # If Gemini works
    # -----------------------------------------------------

    if answer:

        return {
            "answer": answer,
            "source": "gemini"
        }

    # -----------------------------------------------------
    # If Gemini is temporarily unavailable
    # Use local fallback instead of showing an error
    # -----------------------------------------------------

    fallback = fallback_tutor(
        message=message,
        topic=payload.topic,
        level=payload.level,
        action=payload.action
    )

    return {
        "answer": fallback,
        "source": "fallback"
    }


# ---------------------------------------------------------
# QUIZ GENERATION
# ---------------------------------------------------------

@app.post("/api/quiz")
def quiz(
    payload: QuizRequest
):

    prompt = f"""
You are an educational quiz generator.

Create EXACTLY 5 multiple-choice questions.

Topic:
{payload.topic}

Difficulty:
{payload.level}

Return ONLY valid JSON.

Format:

[
  {{
    "question": "question text",
    "options": [
      "option A",
      "option B",
      "option C",
      "option D"
    ],
    "answer": 0,
    "explanation": "short explanation"
  }}
]

Rules:

- Exactly 5 questions.
- Exactly 4 options per question.
- answer must be an integer from 0 to 3.
- Questions must test understanding.
- Avoid ambiguous questions.
- Do not include markdown.
"""

    text = gemini_text(prompt)

    if text:

        try:

            start = text.find("[")
            end = text.rfind("]") + 1

            if start != -1 and end > start:

                data = json.loads(
                    text[start:end]
                )

                if (
                    isinstance(data, list)
                    and len(data) == 5
                ):

                    valid = True

                    for q in data:

                        if not isinstance(q, dict):
                            valid = False
                            break

                        if "question" not in q:
                            valid = False
                            break

                        if (
                            "options" not in q
                            or len(q["options"]) != 4
                        ):
                            valid = False
                            break

                        if "answer" not in q:
                            valid = False
                            break

                    if valid:

                        return {
                            "topic": payload.topic,
                            "level": payload.level,
                            "questions": data,
                            "source": "gemini"
                        }

        except Exception as exc:

            print(
                f"Quiz JSON error: {exc}"
            )

    # -----------------------------------------------------
    # Fallback quiz
    # -----------------------------------------------------

    return {
        "topic": payload.topic,
        "level": payload.level,
        "questions": fallback_quiz(
            payload.topic,
            payload.level
        ),
        "source": "fallback"
    }


# ---------------------------------------------------------
# QUIZ SUBMISSION
# ---------------------------------------------------------

@app.post("/api/quiz/submit")
def submit_quiz(
    payload: QuizSubmit
):

    conn = db()

    conn.execute(
        """
        INSERT INTO quiz_attempts
        (topic, level, score, total, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            payload.topic,
            payload.level,
            payload.score,
            payload.total,
            datetime.utcnow().isoformat()
        )
    )

    conn.commit()
    conn.close()

    percentage = round(
        (
            payload.score
            / max(payload.total, 1)
        ) * 100
    )

    if percentage < 50:

        recommendation = (
            f"Revise {payload.topic} "
            "with a simpler explanation, "
            "then retry a short quiz."
        )

    elif percentage < 80:

        recommendation = (
            f"Review the questions you missed "
            f"in {payload.topic}, then practise "
            "another set."
        )

    else:

        recommendation = (
            f"Good progress in {payload.topic}. "
            "Move to a harder problem or "
            "the next concept."
        )

    return {
        "score": payload.score,
        "total": payload.total,
        "percentage": percentage,
        "recommendation": recommendation
    }