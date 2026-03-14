# Define a simple state
# Create two nodes 
#   - input node - adds a user message to the state
#   - LLM node - simulates LLM call and create a response to user message
# Build a graph and run it

from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

def call_llm(user_input:str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant explaining langgraph and llm workflows."
        },
        {
            "role": "user",
            "content": user_input + "\n. Provide answer in maximum of 5 sentence and in consice way" ,
        }
    ],
    model="llama-3.1-8b-instant") # You can also use "mixtral-8x7b-32768" or "gemma2-9b-it"

    return chat_completion.choices[0].message.content


class ChatState(TypedDict, total = False):
    messages: List[str]
    result: Optional[str]

def input_node(state:ChatState) -> ChatState:
    messages = state.get("messages", []).copy()
    messages.append("User: what is langgraph?")

    print("Input message: ", messages)

    return {**state, "messages":messages}


def llm_node(state:ChatState) -> ChatState:
    messages = state.get("messages", []).copy()
#    mock_ans = "Assistant: Its a framework to build LLM Agents using graph model"
    input = "\n".join(messages)
    mock_ans = call_llm(input)
    messages.append(mock_ans)

    print("llm message: ", mock_ans)

    return{**state, "messages": messages, "result": mock_ans}


def postprocess_node(state:ChatState) -> ChatState:
    result = state.get("result")
    processed_msg = result.upper()

    print("post processed msg: ", processed_msg)

    return{**state, "result":processed_msg}


graph = StateGraph(ChatState)

graph.add_node("input", input_node)
graph.add_node("llm", llm_node)

graph.set_entry_point("input")
graph.add_edge("input", "llm")
graph.add_edge("llm", END)

app =graph.compile()

initial_state: ChatState = {"message" :[]}
final_state = app.invoke(initial_state)

#print("finsfinal_state.get("result"))

print("Final result: ", final_state.get("result"))

#print("Converstation trace")

#for msg in final_state["messages"]:
#    print(msg)