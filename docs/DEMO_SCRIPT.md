# 3-Minute Hackathon Demo Script

## 0:00 — Problem
"Students can ask generic AI tools questions, but they still have to decide what to practise, understand their mistakes, and choose what to study next."

## 0:20 — Product
"This is Vector Tutor, our personalised AI tutor for learning AI. It follows one loop: Learn → Practice → Diagnose → Adapt."

## 0:35 — Personalisation
"First I choose the learner level. The same topic is explained differently for a beginner, intermediate learner, or advanced learner."

## 0:50 — Learn
Ask:
> Explain gradient descent like I'm a beginner.

Then click:
> Explain simpler

Point out that the tutor uses the selected level and recent performance.

## 1:20 — Practice
Click:
> Quiz Me

Complete five questions.

## 1:50 — Diagnose
Submit with 2–3 intentionally wrong answers.

Say:
"The system converts quiz performance into a learning signal. It identifies the topic as a focus area rather than simply displaying a score."

## 2:10 — Adapt
Show the recommendation:
> Review the concept → practise retrieval → retry.

Return to dashboard and show the focus topic.

## 2:30 — Why it is different
"A normal chatbot ends after the answer. Vector Tutor closes the loop by connecting explanation, practice, diagnosis, and the next learning action."

## 2:50 — Technical close
"Next.js handles the learner experience, FastAPI provides the API layer, Gemini generates explanations and practice content, and SQLite stores learner profile and quiz history for the prototype."

## Judge questions
### Why Gemini?
It provides the generative reasoning layer for explanations, examples, quizzes, feedback and adaptive follow-ups.

### What makes it personalised?
The prompt includes the learner's selected level and recent quiz performance. Recommendations are derived from stored performance.

### How do you evaluate it?
Test the same AI/ML topics at beginner/intermediate/advanced levels and measure relevance, quiz correctness, personalisation quality and task completion time.

### Future scope?
- Firebase/Supabase cloud persistence
- richer learner knowledge graph
- spaced repetition
- teacher analytics
- multimodal learning with diagrams and uploaded notes
