from state import AgentState
from langchain_core.messages import AIMessage
import sqlite3

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
