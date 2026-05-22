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
"""Runnability tests for the ADK agent sample project.

Verifies that the python code compiles, resolves all dependencies, and imports
correctly under zero-configuration CI/CD conditions without throwing errors.
"""

from google.adk.agents import Agent
from google.adk.apps import App
from fastapi import FastAPI


def test_fast_api_app_runnability() -> None:
    """Verifies fast_api_app.py compiles and initializes FastAPI successfully."""
    # Importing fast_api_app triggers the telemetry and mock global setups
    import app.fast_api_app

    assert app.fast_api_app.app is not None
    assert isinstance(app.fast_api_app.app, FastAPI)
    assert app.fast_api_app.app.title == "google-trends-agent"


def test_agent_runnability() -> None:
    """Verifies agent.py compiles and instantiates the agent flow successfully."""
    # Importing agent loads the MCP Toolset and the Agent runner configuration
    import app.agent

    # 1. Assert ADK App is initialized correctly
    assert app.agent.app is not None
    assert isinstance(app.agent.app, App)
    assert app.agent.app.name == "app"

    # 2. Assert Agent and its properties are built with matching parameters
    assert app.agent.root_agent is not None
    assert isinstance(app.agent.root_agent, Agent)
    assert app.agent.root_agent.name == "google_trends"
    assert app.agent.root_agent.model == "gemini-flash-latest"

    # 3. Assert Tools set contains expected analytical tools
    tools = app.agent.root_agent.tools
    assert len(tools) == 2

    # Find registered helper functions
    tool_names = [getattr(t, "__name__", type(t).__name__) for t in tools]
    assert "get_todays_date" in tool_names
    assert "McpToolset" in tool_names
