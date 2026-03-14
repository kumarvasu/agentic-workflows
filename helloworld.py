# Define a simple state
# Create two nodes 
#   - input node - adds a user message to the state
#   - LLM node - simulates LLM call and create a response to user message
# Build a graph and run it

from pyexpat.errors import messages
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END


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
    mock_ans = "Assistant: Its a framework to build LLM Agents using graph model"
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
graph.add_node("postprocess", postprocess_node)

graph.set_entry_point("input")
graph.add_edge("input", "llm")
graph.add_edge("llm", "postprocess")
graph.add_edge("postprocess", END)

app =graph.compile()

initial_state: ChatState = {"message" :[]}
final_state = app.invoke(initial_state)

#print("finsfinal_state.get("result"))

print("Final result: ", final_state.get("result"))

#print("Converstation trace")

#for msg in final_state["messages"]:
#    print(msg)