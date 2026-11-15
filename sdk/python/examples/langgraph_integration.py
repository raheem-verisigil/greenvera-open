"""Minimal LangGraph callback wiring.

Install: pip install './sdk/python[langgraph]' langgraph
Keep GREENVERA_API_KEY in a server-side secret manager/environment variable.
"""
import os

from greenvera_openspace import OpenSpaceClient
from greenvera_openspace.langgraph import OpenSpaceLangGraphHandler

client = OpenSpaceClient(os.environ["GREENVERA_API_KEY"])
agent_id = os.environ["GREENVERA_AGENT_ID"]
version_id = os.environ["GREENVERA_AGENT_VERSION_ID"]

# Supply this callback to a LangGraph/LangChain runnable or graph invocation:
# result = graph.invoke({"input": "..."}, config={"callbacks": [handler]})
handler = OpenSpaceLangGraphHandler(client, agent_id, version_id, fail_open=True)
print("OpenSpace LangGraph callback ready:", bool(handler))
