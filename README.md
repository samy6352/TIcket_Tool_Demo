# Ticket Tool Demo

A small, safe demo that shows how an AI agent decides between two things:

- **searching a document** (a support playbook), and
- **calling a tool** (looking up a ticket's current status).

Every ticket and every line of the playbook is made up for training. The ticket tool is read-only, so the agent cannot change anything.

---

## Which section do you need?

| | Section 1: Offline tool | Section 2: Foundry agent |
|---|---|---|
| **What answers your questions** | Fixed rules on your computer | A real AI model in Microsoft Foundry |
| **Azure account needed** | No | Yes |
| **Time** | About 10 minutes | About 30 minutes |
| **Start here if** | You are new, or you want to see the decision logic | You want smarter, free-form answers |

**Start with Section 1.** You can skip Section 2 entirely.

---

## Before you start

You need:

1. **Python 3.10 or newer.** Check it by typing this in a terminal:
   ```
   python --version
   ```
   If you see an error, install Python from https://www.python.org/downloads/ and tick **Add python.exe to PATH** during setup.
2. **VS Code** (recommended): https://code.visualstudio.com/

For Section 2 you also need an Azure subscription, a Microsoft Foundry project, and a chat model deployed in that project.

---

# Section 1: Offline tool (no Azure needed)

This section runs entirely on your computer. Answers come from fixed rules, not an AI model.

### Step 1. Get the code

Either:
- click the green **Code** button on this page, choose **Download ZIP**, then unzip it, or
- run `git clone https://github.com/samy6352/TIcket_Tool_Demo.git`

### Step 2. Open the folder in VS Code

1. Open VS Code.
2. Choose **File > Open Folder**.
3. Select the `TIcket_Tool_Demo` folder and click **Select Folder**.

### Step 3. Open a terminal

Choose **Terminal > New Terminal**. The terminal opens at the bottom of the window, already in the `TIcket_Tool_Demo` folder.

### Step 4. Run the first example

Type this and press **Enter**:

```
python offline_rehearsal.py
```

You will see five results labelled A to E. Each one shows:

- **Route chosen:** whether the agent used the document (KNOWLEDGE), the tool (TOOL), both, or stopped (PAUSE).
- **Retrieval or tool call:** where the answer came from.

### Step 5. Chat with the offline tool

Type this and press **Enter**:

```
python chat_demo.py
```

At the `You [LOCAL]>` prompt, type a question. Try these:

```
What does our sample playbook say about Sev 2 updates?
What is the status of TCK-1042?
What cadence applies, and what is TCK-1042's current status?
Close TCK-1042.
```

Type `/prompts` to see the full list, `/help` for commands, and `/quit` to exit.

**Section 1 is finished.** Go to Section 2 only if you have Azure and want the AI model.

---

# Section 2: Foundry agent (live model, needs Azure)

This section sends your questions to a real AI model in your Microsoft Foundry project. Complete **Section 1, Steps 1 to 3** first, so the code and VS Code are ready.

### Step 1. Create a Foundry project and deploy a model (skip if you already have one)

You need a project and a chat model. Ask your admin if you are unsure whether one exists.

1. Sign in to https://ai.azure.com with your Azure account.
2. Make sure the **New Foundry** toggle is on. These steps refer to **Foundry (new)**.
3. If you have no project yet, select **Create a new project** from the project menu in the upper-left corner. Enter a name such as `my-foundry-project`, then select **Create project**. Wait until the project overview page appears.
4. Select **Build** in the upper-right navigation, then **Models** in the left pane.
5. Select **Deploy** > **Deploy a base model**, search for `gpt-5-mini`, then select **Deploy** > **Default settings**.
6. Note the deployment name (for example, `gpt-5-mini`). You need it in Step 4.

> **Note:** you need a role that can create resources, such as **Foundry Owner**, or your admin must set up the project for you. The Microsoft Learn page at https://learn.microsoft.com/azure/foundry/tutorials/quickstart-create-foundry-resources has the Azure CLI version of these steps.

### Step 2. Install the packages

In the terminal (in the `TIcket_Tool_Demo` folder), run:

```
python -m pip install -r requirements.txt
```

Wait until it finishes. This can take a minute.

### Step 3. Sign in to Azure

1. Install the Azure CLI from https://learn.microsoft.com/cli/azure/install-azure-cli
2. Run:
   ```
   az login
   ```
3. Your account needs the **Foundry User** role on the project. Ask your admin if you are not sure.

### Step 4. Copy two values from the Foundry portal

1. Open https://ai.azure.com and open your project.
2. **Project endpoint:** on the project welcome screen, copy the value that starts with `https://` and contains `/api/projects/`.
3. **Deployment name:** the name you noted in Step 1, for example `gpt-5-mini`.

### Step 5. Set the two values in the terminal

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

### Step 6. Run the live example

```
python foundry_demo.py
```

The script creates a temporary agent, runs prompts A to E, prints every tool call, and deletes the agent at the end.

### Step 7. Chat with the Foundry agent

```
python chat_demo.py --live
```

At the `You [FOUNDRY]>` prompt, ask anything. The model answers, and it calls the ticket tool when it needs live status. Use `/reset` to start a new conversation and `/quit` to end the session.

### Optional: let the agent search the playbook

Questions about the Sev 2 playbook need the playbook in a vector store. Without it, the agent says it has no playbook.

1. In the Foundry portal, create a **vector store** (in your project, under the knowledge or files area).
2. Upload `knowledge/sev2-playbook.md`.
3. Copy the vector store ID (it starts with `vs_`).
4. Set it in the terminal, then start the chat again:
   ```
   $env:VECTOR_STORE_ID="vs_xxxxxxxx"
   ```

---
## How to tell which one you're talking to

| What you see | Meaning |
|---|---|
| `You [LOCAL]>` | Section 1. Fixed rules on your computer. Nothing is sent over the network. |
| `You [FOUNDRY]>` | Section 2. The model in your Foundry project. |
| Banner with "CONNECTED TO MICROSOFT FOUNDRY" | Live mode started. The banner shows the project host and model. |
| `response id=` and `conversation id=` lines | Each answer came from Foundry. Local answers have no IDs. |
| `/where` | Shows the current mode at any time. |

**Quick proof:** turn off Wi-Fi and run `python chat_demo.py`. It still works. Run `python chat_demo.py --live` with Wi-Fi off, and it fails. That shows the live answers come from Foundry.

---

## Running the demo in front of people

Open `demo_examples.md`. It lists 22 prompts in six groups, with the route the agent should choose and what to point out for each one. Ask the room to guess the route before you press Enter.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| `python` is not recognised | Install Python and tick **Add python.exe to PATH**. Close and reopen VS Code. |
| `Set PROJECT_ENDPOINT and MODEL_DEPLOYMENT_NAME` | You are in a new terminal. Set both values again (Section 2, Step 5). |
| `ModuleNotFoundError` | Run `python -m pip install -r requirements.txt` in the same terminal. |
| Authentication or 401 or 403 errors | Run `az login` again. Check that you have the Foundry User role on the project. |
| `.\.venv\Scripts\Activate.ps1` is blocked | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then try again. |
| The agent says it has no playbook | Set `VECTOR_STORE_ID` (see the optional step in Section 2). |
| Pasted text runs as a command and shows errors | Only type the commands in code blocks. Do not paste example output into the terminal. |

---

## Files in this repo

| File | What it does |
|---|---|
| `README.md` | This guide. |
| `demo_examples.md` | The 22 prompts to run during the demo, with the expected result for each. |
| `ticket_tool.py` | The fake ticket lookup tool. It only reads. |
| `knowledge/sev2-playbook.md` | A made-up support playbook that the agent can search. |
| `offline_rehearsal.py` | Section 1. Runs a fixed set of prompts with no Azure needed. |
| `chat_demo.py` | Section 1 by default (offline chat). Section 2 with `--live`. |
| `foundry_demo.py` | Section 2. Runs the prompts against a real agent in Microsoft Foundry. |
| `requirements.txt` | The Python packages needed for Section 2. |

---

## Safety notes

- All tickets and policy text are fictional.
- The ticket tool can only read. There is no function that closes, changes or sends anything.
- Do not paste real customer data or real ticket IDs into this demo.
- Do not commit your project endpoint or any keys to this repository.