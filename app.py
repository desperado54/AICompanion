from flask import Flask, render_template, request, jsonify
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import chatbot
import redis_utility

# --- Initialization ---
app = Flask(__name__)

# --- LangChain Setup ---

# 1. Initialize the LLM
# Make sure the model name matches the one you have pulled with Ollama.
# llm = Ollama(model="gpt-oss:20b")

# # 2. Setup Memory
# # This memory object will store and manage the conversation history.
# memory = ConversationBufferMemory()

# # 3. Create the Conversation Chain
# # This chain combines the LLM, memory, and a prompt structure.
# conversation = ConversationChain(
#     llm=llm,
#     memory=memory,
#     verbose=True  # Set to True to see the chain's internal workings
# )

# --- Routes ---

@app.route("/chat", methods=["GET"])
def index():
    bot_id = request.args.get('bot_id') 
    return render_template("chat.html", bot_id=bot_id)

@app.route("/chat", methods=["POST"])
def handle_chat():
    bot_id = request.json.get('botId')
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    try:
        # Use the conversation chain to predict the response
        # The chain automatically handles history.
        response = chatbot.get_response(bot_id=bot_id, session_id=bot_id + '-user001', user_input=user_message)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create', methods=['GET'])
def create():
    return render_template("create.html")

@app.route('/create', methods=['POST'])
def handle_create():
    bot_id = request.form.get('bot_id', '')
    content = request.form.get('content', '')
    if content and bot_id:
        redis_utility.create(bot_id, content)
        print('Content saved successfully!', 'success')
    else:
        print('No content provided!', 'error')
    return render_template("create.html")
if __name__ == "__main__":
    app.run(debug=True)