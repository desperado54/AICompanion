from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_redis import RedisChatMessageHistory
from langchain_community.llms import Ollama
import configurations
import redis_utility

dictionary = {}

def retrieve_history(bot_id: str) -> BaseChatMessageHistory: 
    if bot_id in dictionary:
        return dictionary[bot_id]
    else:
        prompt = redis_utility.read(bot_id)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompt),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

        llm = Ollama(model=configurations.MODEL)
        chain = prompt | llm
        def get_redis_history(session_id: str) -> BaseChatMessageHistory:
            return RedisChatMessageHistory(session_id, redis_url=configurations.REDIS_URL)
        
        history = RunnableWithMessageHistory(
                    chain, get_redis_history, input_messages_key="input", history_messages_key="history")
        dictionary[bot_id] = history
        return history
    
def get_response(bot_id: str, session_id: str, user_input: str) -> str:
    chain_with_history = retrieve_history(bot_id)
    response = chain_with_history.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    )
    return response;