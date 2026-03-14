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

load_dotenv()

#Agent State
class AgentState(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages] #Message trace
    sql: Optional[str] 
    schema: Optional[str]
    errors: Optional[str]
    user_input: Optional[str]
    chaos_done: bool = False


def input_node(state: AgentState) -> AgentState:
    input = state.get("user_input")
    human_msg = HumanMessage(content=input)
    return {"messages": [human_msg]}


def chaos_node(state: AgentState):
    # Simulate a syntax error manually
    return {
        "sql": "SELECT * FROM NonExistentTable", 
        "chaos_done" : True,
        "messages": [AIMessage(content="Generated SQL: SELECT * FROM NonExistentTable")]
    }

def should_chaos_run(state: AgentState):
    # If we already did chaos, go to the real generator
    if state.get("chaos_done"):
        return "skip_to_generator"
    return "run_chaos"

def execute_sql_node(state:AgentState) -> AgentState:
    sql = state.get("sql")
    print("executing query: "+ sql)
    try:
        with sqlite3.connect("ecommerce.db") as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            return {"messages":[AIMessage(content=f"Results: {results}")], "errors":""}
    except Exception as e:
        return {"errors" : str(e), "messages":[AIMessage(content=f"(error: {str(e)})")]}

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
graph.add_node("chaos", chaos_node)

graph.add_edge(START, "input")
graph.add_conditional_edges("input", should_chaos_run, 
               {
                    "run_chaos" : "chaos",
                    "skip_to_generator": "sql_generator"
                })
#graph.add_edge("input", "sql_generator")
graph.add_edge("chaos", "execute_sql")
graph.add_edge("sql_generator", "execute_sql")
graph.add_conditional_edges("execute_sql", call_agent, 
                            {
                                "call_agent" : "sql_generator",
                                "end" : END
                            })
#graph.add_edge("execute_sql", END)

app = graph.compile()

schema = """
Table Users: user_id (PK), name, email, signup_date
Table Orders: order_id (PK), user_id (FK), product_name, amount, order_date
"""

user_input = "Who is the customer who spent the most money, and how much did they spend?"

state: AgentState={"messages":[], "schema": schema, "user_input" : user_input}

#result = app.invoke(state)

for event in app.stream(state):
    # 'event' is a dictionary where the key is the node name
    for node_name, output in event.items():
        print(f"\n--- Finished Node: {node_name} ---")
        # You can see exactly what each node added to the state
        if "messages" in output:
            print(f"Latest Message: {output['messages'][-1].content}")

#print("Generated sql " + result.get("sql"))

#print(len(result["messages"]))

#print("--------------------Trace--------------------------")

#for msg in result.get("messages",[]):
#    print(f"{type(msg).__name__}")
#    print(msg.content)