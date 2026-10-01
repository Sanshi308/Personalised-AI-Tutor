# Architecture

```text
                         ┌──────────────────────┐
                         │       STUDENT        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     Next.js UI       │
                         │ Dashboard • Tutor    │
                         │ Quiz • Progress      │
                         └──────────┬───────────┘
                                    │ REST
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI         │
                         │ Profile • Tutor      │
                         │ Quiz • Diagnosis     │
                         └───────┬───────┬──────┘
                                 │       │
                         ┌───────▼───┐ ┌─▼─────────────┐
                         │  Gemini   │ │    SQLite     │
                         │    AI     │ │ Profile/Score │
                         └───────────┘ └───────────────┘
```

## Adaptive prompt inputs
- learner level
- selected topic
- recent topic scores
- current request
- requested teaching action

## Stored learning signals
- topic
- level
- score
- total questions
- timestamp

## Recommendation rule
- < 50% → revise with simpler explanation and retry
- 50–79% → review missed concepts and practise again
- ≥ 80% → move to a harder problem or next concept

The rule is intentionally transparent for the prototype.
