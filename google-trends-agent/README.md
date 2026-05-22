# google-trends-agent

Simple ReAct agent
Agent generated with `agents-cli` version `0.2.0`

## Project Structure

```
google-trends-agent/
├── app/         # Core agent code
│   ├── agent.py               # Main agent logic
│   └── app_utils/             # App utilities and helpers
├── tests/                     # Unit, integration, and load tests
├── GEMINI.md                  # AI-assisted development guide
└── pyproject.toml             # Project dependencies
```

> 💡 **Tip:** Use [Gemini CLI](https://github.com/google-gemini/gemini-cli) for AI-assisted development - project context is pre-configured in `GEMINI.md`.

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **agents-cli**: Agents CLI - Install with `uv tool install google-agents-cli`
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)


## Quick Start

Install `agents-cli` and its skills if not already installed:

```bash
uvx google-agents-cli setup
```

Install required packages:

```bash
agents-cli install
```

Configure environment variables:

1. Copy the template environment file to create your local configuration:
   ```bash
   cp .env.example .env
   ```

2. Open the newly created `.env` file and customize the environment configurations:
   * **`GOOGLE_CLOUD_PROJECT`**: Set this to your active Google Cloud Project ID.
   * **`GOOGLE_CLOUD_LOCATION`**: The regional endpoint used by Google Cloud API services (default: `us-east1`).
   * **`GOOGLE_GENAI_USE_VERTEXAI`**: Set to `True` to utilize enterprise-grade Vertex AI services.
   * **`MODEL_NAME`**: Specify the model tier to run (default: `gemini-flash-latest`).

Test the agent with a local web server:

```bash
agents-cli playground
```

You can also use features from the [ADK](https://adk.dev/) CLI with `uv run adk`.

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `agents-cli install` | Install dependencies using uv                                                         |
| `agents-cli playground` | Launch local development environment                                                  |
| `agents-cli lint`    | Run code quality checks                                                               |
| `uv run pytest tests/unit tests/integration` | Run unit and integration tests                                                        |

## Testing & Runnability Verification

This sample includes an **adaptive, zero-configuration runnability test harness** under the `tests/` directory. It is designed to act as a gold-standard template for automated PR pipelines (like GitHub Actions) and zero-config local validations.

The verification engine dynamically auto-detects your workspace and operates in two distinct execution tiers:

### 1. Local Development Mode (Real GCP Credentials exist)
When you have run `cp .env.example .env` and logged into Google Cloud (`gcloud auth application-default login`), running tests executes real E2E queries:

```bash
uv run pytest tests/unit tests/integration
```
* **Behavior:** Automatically detects credentials, disables all mocks, and executes actual unit and live connection integration tests (queries actual Gemini endpoints and active BigQuery trends datasets).

---

### 2. CI/CD Simulated Mode (Zero Configuration / PR gate)
For automated PR pipelines (where no default GCP credentials or active environment secrets exist), you can run verification in a **mock-isolated dry run state** simply by prefixing the execution command with `FORCE_MOCK=True`:

```bash
FORCE_MOCK=True uv run pytest tests/unit tests/integration
```
* **Behavior:** The test bootloader ([tests/conftest.py](file:///Users/shahins/projects/mine/google-trends-agent/tests/conftest.py)) intercepts and overrides standard authenticators and cloud logging boundaries in-memory.
* **Auto-Skip Engine:** Live E2E integration tests (under `tests/integration/`) are dynamically skipped with a descriptive warning, preventing unauthenticated 401 connection crashes.
* **Performance:** Executes zero external network handshakes, registers zero cloud service billing, and completes loading, compilation, and structure checks successfully in under **one second!**

---

### How to Port this Harness to Other Samples

To establish frictionless, zero-config runnability checks on pull requests for your own developer samples:

1. **Copy [tests/conftest.py](file:///Users/shahins/projects/mine/google-trends-agent/tests/conftest.py)** into the root of your new project's `tests/` folder.
2. **Tweak the Developer Configuration** dictionary block at the top of the file:
   * **`MOCK_ENVIRONMENT`**: Add all custom environmental variables that your agent logic validates upon launch (e.g., API keys, database URLs, deployment keys).
   * **`MOCK_SERVICES`**: Add any client libraries (Google-based like `google.cloud.aiplatform` or non-Google like `pinecone`, `slack_sdk`, `openai`) that execute live initialization routines at the module import level.
3. **Add a Load Verification test** (similar to [tests/unit/test_runnability.py](file:///Users/shahins/projects/mine/google-trends-agent/tests/unit/test_runnability.py)) to import the agent application and assert structure shapes.
4. Place any tests that require active live model connections or database integrations under the `tests/integration/` target directory.

---

## 🛠️ Project Management

| Command | What It Does |
|---------|--------------|
| `agents-cli scaffold enhance` | Add CI/CD pipelines and Terraform infrastructure |
| `agents-cli infra cicd` | One-command setup of entire CI/CD pipeline + infrastructure |
| `agents-cli scaffold upgrade` | Auto-upgrade to latest version while preserving customizations |

---

## Development

Edit your agent logic in `app/agent.py` and test with `agents-cli playground` - it auto-reloads on save.

## Deployment

```bash
gcloud config set project <your-project-id>
agents-cli deploy
```

To add CI/CD and Terraform, run `agents-cli scaffold enhance`.
To set up your production infrastructure, run `agents-cli infra cicd`.

## Observability

Built-in telemetry exports to Cloud Trace, BigQuery, and Cloud Logging.
