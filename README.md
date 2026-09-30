# PocketSmart AI

PocketSmart AI is a full-stack generative-AI budget and recommendation assistant.

The project provides:

- Home interior budget planning
- Party/event budget planning
- Jewelry recommendations
- Optional jewelry outfit-image analysis
- User registration
- User login/logout
- JWT authentication
- Recommendation history
- Gemini AI integration
- Budget enforcement
- SQLite persistence
- FastAPI REST APIs
- Responsive browser frontend
- Automated tests

---

# Architecture

```text
Browser
   |
   v
FastAPI
   |
   +-------------------+
   |                   |
   v                   v
Auth Services      Planner Routes
                       |
                       v
                Gemini Service
                       |
                       v
              Recommendation JSON
                       |
                       v
                 Budget Validation
                       |
                       v
                  SQLite History