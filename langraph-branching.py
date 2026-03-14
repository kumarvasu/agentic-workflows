from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END


class ChatState(TypedDict, total=False):
    messages : List[str]
    user_input: Optional[str]
    intent: Optional[str]
    result: Optional[str]

def input_node(state:ChatState) -> ChatState:
    messages = state.get('messages',[]).copy()
    messages.append("User: " + state.get('user_input'))

    #print(messages)

    return {**state, "messages": messages}


def classifier_node(state:ChatState) -> ChatState:
    input = state.get("user_input","").lower()
    support_keywords = ["support","issue","refund","problem","bug"]
    intent = ""
    for word in support_keywords:
        if word in input:
            intent = "support"
            break
    if intent == "":
        intent = "chit-chat"

    #print("Classified intent: " + intent)    
    return {**state, "intent": intent}
    
def support_node(state:ChatState) -> ChatState:
    #p#rint("support node")
    messages = state.get("messages").copy()
    messages.append("Assitant: Seems you need support. Please share your question")
    #print(messages)
    return {**state, "messages": messages}

def general_node(state:ChatState) -> ChatState:
    #print("general node")
    messages = state.get("messages").copy()
    messages.append("Assistant: Seems you have a general query. Please share your question")
    #print(messages)
    return {**state, "messages": messages}


graph = StateGraph(ChatState)

graph.add_node("input", input_node)
graph.add_node("classifier", classifier_node)
graph.add_node("support_agent", support_node)
graph.add_node("general_agent", general_node)

graph.set_entry_point("input")
graph.add_edge("input", "classifier")

def route_after_classifier(state:ChatState):
    if state.get('intent') == 'support':
        return "support_agent"
    return "general_agent"

graph.add_conditional_edges("classifier", route_after_classifier, {"support_agent":"support_agent","general_agent":"general_agent"})

graph.add_edge("support_agent", END)
graph.add_edge("general_agent", END)

app = graph.compile()

state:ChatState = {"messages":[]}

questions = ["I need help with my issue and to process my refund", "I would like to know more about your product","My refund has not yet processed"]

for q in questions:
    state["user_input"] = q
    result = app.invoke(state)

    print("== Converstation trace ==")
    for msg in result.get("messages"):
        print(msg)