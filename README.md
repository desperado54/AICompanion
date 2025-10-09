### AI Companion (Flask + LangChain + SQLite)

Quickstart:

1. Create a virtualenv and install requirements:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment (Ollama):
```bash
cp .env.example .env
# edit .env and set MODEL_NAME and OLLAMA_BASE_URL if needed
# ensure Ollama is running and the model is pulled, e.g.:
#   ollama pull llama3.1:8b
```

3. Run the app:
```bash
python -m app.app
```

4. Example usage with curl:
```bash
# Create user
curl -sX POST localhost:5000/api/users -H 'Content-Type: application/json' -d '{"username":"alice"}'

# Create companion for user 1
curl -sX POST localhost:5000/api/companions -H 'Content-Type: application/json' -d '{
  "user_id": 1,
  "name": "Kai",
  "age": 28,
  "gender": "non-binary",
  "birth_country": "Japan",
  "personality": "curious, encouraging, playful",
  "education": "Computer Science BSc",
  "background": "Loves literature and robotics"
}'

# Create conversation (session)
curl -sX POST localhost:5000/api/conversations -H 'Content-Type: application/json' -d '{
  "user_id": 1,
  "companion_id": 1,
  "session_key": "alice-kai-1"
}'

# Chat
curl -sX POST localhost:5000/api/chat -H 'Content-Type: application/json' -d '{
  "user_id": 1,
  "companion_id": 1,
  "session_key": "alice-kai-1",
  "input": "Hey Kai, can you remember my favorite color is green?"
}'

# History
curl -s "localhost:5000/api/history?session_key=alice-kai-1" | jq .
```

Notes:
- LangChain `SQLChatMessageHistory` persists messages in SQLite so each `session_key` has its own memory.
- Persona variables (age, gender, birth country, personality, education, background) customize the companion prompt.
- Uses local Ollama via `MODEL_NAME` and `OLLAMA_BASE_URL`. Make sure the model is available in Ollama.
