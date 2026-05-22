# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import textwrap
from datetime import date

import google.auth
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)
from google.auth.transport.requests import Request

# Load environment variables from local .env configuration file
load_dotenv()

gemini_model = os.environ.get("MODEL_NAME")
if not gemini_model:
    raise ValueError("MODEL_NAME environment variable is not set")

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
if not project_id:
    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set")


def get_agent_instruction(project_id: str) -> str:
    """Generates a clear and formatted prompt for the data analyst."""
    instruction = f"""
    # ROLE
    You are a Google Search Trends Analyst. Your mission is to provide clear answers using SQL data.

    # DATA CONSTRAINTS
    - BigQuery tool `execute_sql` requires explicit billing project mapping. Use: '{project_id}'.
    - Target dataset strictly: `bigquery-public-data.google_trends`

    # SCHEMA DISCOVERY (CRITICAL)
    1. DO NOT call `get_table_info` or `list_table_ids` (Triggers Permission Errors).
    2. Run `SELECT * FROM table LIMIT 0` via `execute_sql` for field definition mapping.

    # OUTPUT PRESENTATION
    - Render purely as a cleanly aligned Markdown table.
    - Use clear and descriptive headers for each column.
    - Remove conversational preambles. Output only the results.
    """
    return textwrap.dedent(instruction).strip()


def get_auth_headers() -> dict[str, str]:
    """Fetch auth headers for the project using Google Cloud Platform scopes."""
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    request = Request()
    credentials.refresh(request)

    return {"Authorization": f"Bearer {credentials.token}"}

def get_todays_date() -> str:
    """Returns today's date in YYYY-MM-DD format."""
    return date.today().isoformat()


# Apply target deployment context defaults
if "GOOGLE_CLOUD_LOCATION" not in os.environ:
    os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
if "GOOGLE_GENAI_USE_VERTEXAI" not in os.environ:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

mcp_headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
} | get_auth_headers()

# Configure BigQuery Tools via MCP
bq_tools = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://bigquery.googleapis.com/mcp",
        headers=mcp_headers,
    )
)

# Initialize the LLM Agent
root_agent = Agent(
    name="google_trends",
    model=gemini_model,
    tools=[get_todays_date, bq_tools],
    instruction=get_agent_instruction(project_id),
)

# Create the ADK App
app = App(name="app", root_agent=root_agent)
