from state import AgentState
from groq import Groq
import os
from langchain_core.messages import AIMessage, HumanMessage
import json

SYSTEM_MSG = """You are a SQL expert. Provide your response as a **JSON** object. 
                The JSON must have a single key called 'sql_query' containing the raw SQL code."""

def create_user_prompt(input, schema, sql, errors):
    if(errors):
        return f"""Database schema: {schema}. User query: {input}. Generated SQL: {sql}
                Generated SQL has following errors: {errors}. Fix the error and provide the correct query as per the user query."""
    else:
        return f"""Database schema: {schema}.
                Generate a sql as per the input: {input} using the provided DB schema."""
    

def generate_sql_node(state: AgentState) -> AgentState:
    schema = state.get("schema")
    input = state.get("user_input")
    sql = state.get("sql")
    errors = state.get("errors")

    user_prompt = create_user_prompt(input, schema, sql, errors)

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": SYSTEM_MSG
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ],
    response_format={"type":"json_object"},
    model="llama-3.1-8b-instant") 

    raw_json = json.loads(chat_completion.choices[0].message.content)
    sql = raw_json.get("sql_query") # Now you have pure SQL from a JSON key

    return {"sql":sql, "messages":[HumanMessage(content=user_prompt), AIMessage(content=f"Generated SQL: {sql}")]}

