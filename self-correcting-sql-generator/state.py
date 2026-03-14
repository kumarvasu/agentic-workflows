from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

#Agent State
class AgentState(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages] #Message trace
    sql: Optional[str] 
    schema: Optional[str]
    errors: Optional[str]
    user_input: Optional[str]
    chaos_done: bool = False