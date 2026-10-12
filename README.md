# Ticket Tool Demo

A small, safe demo that shows how an AI agent decides between two things:

- **searching a document** (for example, a support playbook), and
- **calling a tool** (for example, looking up a ticket's current status).

Every ticket and every line of the playbook is made up for training. The ticket tool is read-only, so the agent cannot change anything.

You can run the whole demo on your own computer without any Azure account. Part 2 is optional and uses Microsoft Foundry.

---

## What is in this repository

| File | What it does |
|---|---|
| `README.md` | This guide. |
| `demo_examples.md` | The list of prompts to run during the demo, with the expected result for each. |
| `ticket_tool.py` | The fake ticket lookup tool. It only reads. |
| `knowledge/sev2-playbook.md` | A made-up support playbook that the agent can search. |
| `offline_rehearsal.py` | Runs a fixed set of prompts with no Azure needed. |
| `chat_demo.py` | A chat window in your terminal. Offline by default, live with `--live`. |
| `foundry_demo.py` | Runs the prompts against a real agent in Microsoft Foundry. |
| `requirements.txt` | The Python packages needed for the live demo. |

---

## Before you start

You need:

1. **Python 3.10 or newer.** Check it by typing this in a terminal:
   ```
   python --version
   ```
   If you see an error, install Python from https://www.python.org/downloads/ and tick **Add python.exe to PATH** during setup.
2. **VS Code** (recommended): https://code.visualstudio.com/
3. **For Part 2 only:** an Azure subscription, a Microsoft Foundry project, and a chat model deployed in that project.

---

## Part 1: Run the demo offline (about 10 minutes, no Azure)

### Step 1. Get the code

Either:
- click the green **Code** button on this page, choose **Download ZIP**, then unzip it, or
- run `git clone https://github.com/samy6352/TIcket_Tool_Demo.git`

### Step 2. Open the folder in VS Code

1. Open VS Code.
2. Choose **File > Open Folder**.
3. Select the `TIcket_Tool_Demo` folder and click **Select Folder**.

### Step 3. Open a terminal

Choose **Terminal > New Terminal**. A terminal opens at the bottom of the window. It should already be in the `TIcket_Tool_Demo` folder.

### Step 4. Run the first example

Type this and press **Enter**:

```
python offline_rehearsal.py
```

You will see five results labelled A to E. Each one shows:

- **Route chosen:** whether the agent used the document (KNOWLEDGE), the tool (TOOL), both, or stopped (PAUSE).
- **Retrieval or tool call:** where the answer came from.

### Step 5. Chat with the demo

Type this and press **Enter**:

```
python chat_demo.py
```

At the `You>` prompt, type a question. Try these:

```
What does our sample playbook say about Sev 2 updates?
What is the status of TCK-1042?
What cadence applies, and what is TCK-1042's current status?
Close TCK-1042.
```

Type `/prompts` to see the full list, `/help` for commands, and `/quit` to exit.

> **Note:** offline mode uses fixed rules, not an AI model. It shows how the decision works. Part 2 uses a real model.

---

## Part 2: Run the live demo with Microsoft Foundry (optional)

### Step 1. Install the packages

In the same terminal, run:

```
python -m pip install -r requirements.txt
```

Wait until it finishes. This can take a minute.

> **Tip:** if you want a separate environment, run `python -m venv .venv` first, then activate it:
> - Windows: `.\.venv\Scripts\Activate.ps1`
> - macOS or Linux: `source .venv/bin/activate`

### Step 2. Sign in to Azure

1. Install the Azure CLI from https://learn.microsoft.com/cli/azure/install-azure-cli
2. Run:
   ```
   az login
   ```
3. Your account needs the **Foundry User** role on the project. Ask your admin if you are not sure.

### Step 3. Copy two values from the Foundry portal

1. Open https://ai.azure.com and open your project.
2. **Project endpoint:** on the project **Overview** page, copy the value that starts with `https://` and contains `/api/projects/`.
3. **Deployment name:** open **Models + endpoints** and copy the name of your chat model, for example `gpt-4.1-mini`.

### Step 4. Set the two values in the terminal

On Windows (PowerShell), replace the placeholders with your values:

```
$env:PROJECT_ENDPOINT="https://<your-resource>.services.ai.azure.com/api/projects/<your-project>"
$env:MODEL_DEPLOYMENT_NAME="<your-deployment-name>"
```

On macOS or Linux:

```
export PROJECT_ENDPOINT="https://<your-resource>.services.ai.azure.com/api/projects/<your-project>"
export MODEL_DEPLOYMENT_NAME="<your-deployment-name>"
```

These values last only for this terminal window. Set them again if you open a new one.

### Step 5. Run the live example

```
python foundry_demo.py
```

The script creates a temporary agent, runs prompts A to E, prints every tool call, and deletes the agent at the end.

To chat with the live agent instead:

```
python chat_demo.py --live
```

Use `/reset` to start a new conversation.

### Optional: let the agent search the playbook

Prompts A to D need the playbook in a vector store, otherwise the agent says it has no playbook.

1. In the Foundry portal, create a **vector store** (in your project, under the knowledge or files area).
2. Upload `knowledge/sev2-playbook.md`.
3. Copy the vector store ID (it starts with `vs_`).
4. Set it in the terminal, then run the demo again:
   ```
   $env:VECTOR_STORE_ID="vs_xxxxxxxx"
   ```

---

## Running the demo in front of people

Open `demo_examples.md`. It lists 22 prompts in six groups, with the route the agent should choose and what to point out for each one. Ask the room to guess the route before you press Enter.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| `python` is not recognised | Install Python and tick **Add python.exe to PATH**. Close and reopen VS Code. |
| `Set PROJECT_ENDPOINT and MODEL_DEPLOYMENT_NAME` | You are in a new terminal. Set both values again (Part 2, Step 4). |
| `ModuleNotFoundError` | Run `python -m pip install -r requirements.txt` in the same terminal. |
| Authentication or 401 or 403 errors | Run `az login` again. Check that you have the Foundry User role on the project. |
| `.\.venv\Scripts\Activate.ps1` is blocked | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then try again. |
| The agent says it has no playbook | Set `VECTOR_STORE_ID` (see the optional step above). |
| Pasted text runs as a command and shows errors | Only type the commands in code blocks. Do not paste example output into the terminal. |

---

## Safety notes

- All tickets and policy text are fictional.
- The ticket tool can only read. There is no function that closes, changes or sends anything.
- Do not paste real customer data or real ticket IDs into this demo.
- Do not commit your project endpoint or any keys to this repository.
