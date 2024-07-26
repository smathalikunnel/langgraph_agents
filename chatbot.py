from chatbot_helper import initialise
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.runnables import Runnable
import uuid

from typing import TypedDict, Annotated
from langchain_community.tools.tavily_search import TavilySearchResults

from dotenv import load_dotenv
import json

import shutil

backup_file = "travel2.backup.sqlite"
local_file = "travel2.sqlite"
db = local_file

_ = load_dotenv()



# define model
model = ChatOpenAI(model="gpt-3.5-turbo")
# call llm with tools

tools_list = initialise()
tools = {t.name:t for t in tools_list}

class State(TypedDict):
    messages : Annotated[list, add_messages]

class Assistant:

    def __init__(self, runnable: Runnable):

        self.runnable = runnable

    def __call__(self, state: State, config):
        config = config["configurable"]
        state = {**state, "user_info":config.get("passenger_id", None)}
        response = self.runnable.invoke(state, config)
        return {"messages": response}


def _call_tool_decision(state):
    
    tool_calls = state["messages"][-1].tool_calls
    return len(tool_calls) > 0

def _call_tool(state):

    tool_calls = state["messages"][-1].tool_calls
    print(f"-----------calling TOOLs : {tool_calls}")
    
    results = []
    for tool in tool_calls:
        result = json.dumps(tools[tool["name"]].invoke(tool["args"]))
        results.append(ToolMessage(content=result, tool_call_id=tool["id"]))

    return {"messages" : results}

primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful customer support assistant for Swiss Airlines. "
            " Use the provided tools to search for flights, company policies, and other information to assist the user's queries. "
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            " If a search comes up empty, expand your search before giving up."
            "\n\nCurrent user:\n<User>\n{user_info}\n</User>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())
part1_assistant_runnable = primary_assistant_prompt | model.bind_tools(tools_list)

graph = StateGraph(State)
graph.add_node("llm", Assistant(part1_assistant_runnable))
graph.add_conditional_edges("llm", _call_tool_decision, {True: "action", False: END})
graph.add_node("action", _call_tool)
graph.add_edge("action", "llm")

graph.set_entry_point("llm")
memory = SqliteSaver.from_conn_string(":memory:")
graph = graph.compile(checkpointer=memory)

# Let's create an example conversation a user might have with the assistant
tutorial_questions = [
    "Hi there, what time is my flight?",
    "Am i allowed to update my flight to something sooner? I want to leave later today.",
    # "Update my flight to sometime next week then",
    # "The next available option is great",
    # "what about lodging and transportation?",
    # "Yeah i think i'd like an affordable hotel for my week-long stay (7 days). And I'll want to rent a car.",
    # "OK could you place a reservation for your recommended hotel? It sounds nice.",
    # "yes go ahead and book anything that's moderate expense and has availability.",
    # "Now for a car, what are my options?",
    # "Awesome let's just get the cheapest option. Go ahead and book for 7 days",
    # "Cool so now what recommendations do you have on excursions?",
    # "Are they available while I'm there?",
    # "interesting - i like the museums, what options are there? ",
    # "OK great pick one and book it for my second day there.",
]

# Update with the backup file so we can restart from the original place in each section
shutil.copy(backup_file, db)
thread_id = str(uuid.uuid4())
config = {"configurable": {"passenger_id": "3442 587242", 
                           # checkpoints are accessed via threads
                           "thread_id":thread_id}}
# for question in tutorial_questions:
#     print(graph.invoke({"messages": question}, config))
#     break

for question in tutorial_questions:
    events = graph.stream({"messages": question}, config, stream_mode="values")
    print("++++++++++++++++++++++++++++++++++++++EVENT START+++++++++++++++++++++++++++")
    for event in events:
        print(event["messages"][-1])
    print("++++++++++++++++++++++++++++++++++++++EVENT END+++++++++++++++++++++++++++")
    

# print(graph.get_state(config))

