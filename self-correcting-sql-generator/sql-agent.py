from typing import Annotated, Sequence, TypedDict, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph.message import add_messages
from groq import Groq
from langgraph.graph import StateGraph
import os
from dotenv import load_dotenv
from langgraph.graph import START, END
import sqlite3
import json

from state import AgentState
from sql_generator import generate_sql_node
from sql_executor import execute_sql_node

load_dotenv()

#Input node to preprocess input message if required
def input_node(state: AgentState) -> AgentState:
    return {"messages": [HumanMessage(content=state.get("user_input"))]}

def call_agent(state:AgentState):
    error = state.get("errors")
    if(error):
        return "call_agent"
    else:
        return "end"

graph = StateGraph(AgentState)

graph.add_node("input", input_node)
graph.add_node("sql_generator", generate_sql_node)
graph.add_node("execute_sql", execute_sql_node)

graph.add_edge(START, "input")
graph.add_edge("input", "sql_generator")
graph.add_edge("sql_generator", "execute_sql")
graph.add_conditional_edges("execute_sql", call_agent, 
                            {
                                "call_agent" : "sql_generator",
                                "end" : END
                            })

app = graph.compile()

schema = """
Table Users: user_id (PK), name, email, signup_date
Table Orders: order_id (PK), user_id (FK), product_name, amount, order_date
"""

user_input = "Who is the customer who spent the most money, and how much did they spend?"

state: AgentState={"messages":[], "schema": schema, "user_input" : user_input}

result = app.invoke(state)

for event in app.stream(state):
    # 'event' is a dictionary where the key is the node name
    for node_name, output in event.items():
        print(f"\n--- Finished Node: {node_name} ---")
        # You can see exactly what each node added to the state
        if "messages" in output:
            print(f"Latest Message: {output['messages'][-1].content}")

