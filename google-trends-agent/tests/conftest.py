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
"""ADK Sample Runnability Verification Template.

To adapt this verification harness to other ADK samples, simply edit the 
DEVELOPER CONFIGURATION block below. No other code modifications are required.
"""

import os
from unittest.mock import MagicMock

import google.auth
import google.cloud.logging
from google.auth.exceptions import DefaultCredentialsError

# ==============================================================================
# DEVELOPER CONFIGURATION (Tweak this section for your sample)
# ==============================================================================

# Define all environment variables required by your sample agent
MOCK_ENVIRONMENT = {
    "MODEL_NAME": "gemini-flash-latest",
    "GOOGLE_CLOUD_PROJECT": "mock-gcp-project",
    "GOOGLE_CLOUD_LOCATION": "global",
    "GOOGLE_GENAI_USE_VERTEXAI": "True",
    "LOGS_BUCKET_NAME": "mock-logs-bucket",
    # Add your sample-specific env variables below:
}

# List standard client library modules (both Google and non-Google based) that
# your application imports at the top-level (module scope) and that might
# trigger active network connections, credential checks, or API key lookups.
#
# Because Python's runtime module loading is completely provider-agnostic,
# adding any identifier here (e.g. "pinecone", "slack_sdk") intercepts its import under CI,
# providing a virtual stub in-memory so your file runs without external dependencies.
MOCK_SERVICES = [
    # Google-based dependencies:
    #"google.cloud.aiplatform",
    #"google.cloud.bigquery",

    # Non-Google dependencies (databases, messaging, external APIs):
    #"pinecone",
    #"slack_sdk",
    #"openai",
]


# ==============================================================================
# RUNNABILITY BOOTSTRAP (Static boilerplate - DO NOT MODIFY)
# ==============================================================================

# 1. Detect if active GCP default authentication environment exists
has_active_gcp = False
if os.environ.get("FORCE_MOCK") != "True":
    try:
        creds, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        has_active_gcp = creds is not None
    except (DefaultCredentialsError, Exception):
        has_active_gcp = False


# 2. Apply mock layer selectively under zero-configuration runs
if not has_active_gcp:
    # Load fallback environments in-memory
    for key, val in MOCK_ENVIRONMENT.items():
        os.environ.setdefault(key, val)

    # Dynamically patch standard authentication & logging SDK boundaries
    mock_creds = MagicMock()
    mock_creds.universe_domain = "googleapis.com"
    mock_creds.token = "mock-ci-token-value"

    google.auth.default = MagicMock(
        return_value=(mock_creds, os.environ["GOOGLE_CLOUD_PROJECT"])
    )
    google.cloud.logging.Client = MagicMock()

    # Stub optional service modules to prevent import-time connection errors
    for module_path in MOCK_SERVICES:
        import sys

        sys.modules[module_path] = MagicMock()


# 3. Self-healing check: Skip live integrations in zero-config pipelines
def pytest_collection_modifyitems(session, config, items) -> None:
    """Automatically skips integration tests in blank credential runtimes."""
    if not has_active_gcp:
        import pytest

        skip_live = pytest.mark.skip(
            reason="GCP credentials not available in environment. Skipping integration."
        )
        for item in items:
            if "tests/integration" in str(item.fspath):
                item.add_marker(skip_live)
