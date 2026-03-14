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

def call_llm(converstation:str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant explaining langgraph and llm workflows."
        },
        {
            "role": "user",
            "content": "Here is the converstation so far: " + converstation + "\n. Provide answer in maximum of 5 sentence and in consice way" ,
        }
    ],
    model="llama-3.1-8b-instant") # You can also use "mixtral-8x7b-32768" or "gemma2-9b-it"

    return chat_completion.choices[0].message.content


class ChatState(TypedDict, total = False):
    messages: List[str]
    result: Optional[str]
    old_msg_summary: Optional[str]
    user_input: Optional[str]

def input_node(state:ChatState) -> ChatState:
    messages = state.get("messages", []).copy()
    messages.append("User: " + state.get("user_input"))

    #print("Recent Conversation: ", messages)

    return {**state, "messages":messages}


def llm_node(state:ChatState) -> ChatState:
    messages = state.get("messages", []).copy()
    transcript = "Old Conversation summary: " + state.get("old_msg_summary", "") + "Recent converstation: "+"\n".join(messages)
    response = call_llm(transcript)
    messages.append("Assistant: " + response)

    #print("llm message: ", response)

    return{**state, "messages": messages, "result": response}

def memory_mgmt_node(state:ChatState, max_messages:int = 3) -> ChatState:
    messages = state.get("messages").copy()
    
    old_msg_summary = ""
    if(len(messages) > max_messages):
        messages = messages[-max_messages:]
        old_msgs = messages[:max_messages]
        old_msg_summary = call_llm("Summarize the following lines: "+ state.get('old_msg_summary',"") + "\n".join(old_msgs))
    
    return{**state, "messages": messages, "old_msg_summary": old_msg_summary}


graph = StateGraph(ChatState)

graph.add_node("input", input_node)
graph.add_node("llm", llm_node)
graph.add_node("memory", memory_mgmt_node)

graph.set_entry_point("input")
graph.add_edge("input", "llm")
graph.add_edge("llm", "memory")
graph.add_edge("memory", END)

app =graph.compile()

state: ChatState = {"message" :[]}

quests = ["What is langgraph?","Explain graph, nodes and edges in simple terms?", 
          "what is the state in langgraph?"," How langgraph manages memory?"]

for q in quests:
    state["user_input"] = q
    state = app.invoke(state)
    print(f"(==After question q: {q} =====")

    for msg in state["messages"]:
        print(msg)
    print(f"(===Summary=== {state['old_msg_summary']}")
    print(f"(Number of messages stored: {len(state['messages'])}")
    print("==============================")

#print("finsfinal_state.get("result"))

#print("Final result: ", final_state.get("result"))

