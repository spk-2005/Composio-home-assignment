import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

api_key = os.getenv("COMPOSIO_API_KEY")

if not api_key:
    raise RuntimeError("COMPOSIO_API_KEY is missing")

composio = Composio(api_key=api_key)

session = composio.sessions.create(
    user_id="appscout-test"
)

print("Composio session created!")
print("Session ID:", session.session_id)

tools = session.tools()

print("Available Composio tools:", len(tools))