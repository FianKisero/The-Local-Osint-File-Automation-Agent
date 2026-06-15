import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from tools.file_ops import TOOL_REGISTRY, TOOLS_SCHEMA

load_dotenv()

# Pointing to local running Ollama instance server engine setup configurations
client = OpenAI(base_url="http://localhost:11434/v1/", api_key="ollama")
MODEL = "llama3.1"

# Folder configuration rules
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/logs"))
os.makedirs(LOG_DIR, exist_ok=True)

# Generate a unique markdown document log audit record file for the session
SESSION_LOG_FILE = os.path.join(LOG_DIR, f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

def append_to_audit_log(heading, body_content):
    """FEATURE 3: Logs agent execution steps into structural Markdown files cleanly."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SESSION_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"### [{timestamp}] - {heading}\n\n")
        f.write(f"```text\n{body_content}\n```\n\n---\n\n")

def initialize_audit_file():
    with open(SESSION_LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"# Agent Session Execution Audit Log Trail\n")
        f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Target Execution Architecture Local Processing Engine: {MODEL}\n\n---\n\n")

def run_agent_chat_system():
    initialize_audit_file()
    
    messages = [
        {
            "role": "system", 
            "content": "You are an advanced local workspace OSINT automation assistant. You have full multi-functional local tool tracking capabilities. Respond using neat Markdown layout formats."
        }
    ]
    
    print("🤖 Agent Conversational Workspace Framework activated!")
    print("👉 Type your instructions below. Type 'quit' or 'exit' to terminate session.\n")
    
    while True:
        user_input = input("\n👤 You: ")
        if user_input.lower() in ["quit", "exit"]:
            print("👋 Session ended safely. Audit records stored inside data/logs/")
            break
            
        messages.append({"role": "user", "content": user_input})
        append_to_audit_log("User Input Prompt Command Received", user_input)
        
        while True:
            # Call Ollama local runtime instance engine models
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            messages.append(response_message)
            
            # If there are no tool calls, print final conversational output statements
            if not response_message.tool_calls:
                print(f"\n🤖 Agent: {response_message.content}")
                if response_message.content:
                    append_to_audit_log("Agent Final Text Output Phrase Answer", response_message.content)
                break
                
            # If tool calls are generated, iterate over invocation arrays cleanly
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"\n⚡ Thought Process: LLM requests operation call '{function_name}'")
                append_to_audit_log(f"Agent Request Action: Tool [{function_name}]", json.dumps(function_args, indent=2))
                
                # ==========================================
                # FEATURE 2: HUMAN-IN-THE-LOOP (HITL) GATE
                # ==========================================
                if function_name in ["write_workspace_file", "run_terminal_command"]:
                    print(f"⚠️  CRITICAL ACTION AUTHORIZATION GATE REQUESTED:")
                    print(f"   Target Tool Operation: [{function_name}]")
                    print(f"   Arguments Payload: {function_args}")
                    user_gate = input("👉 Authorize tool execution? (y/n): ")
                    
                    if user_gate.lower() != 'y':
                        observation = "Operation rejected: Access authorization denied by User Controller Interface."
                        print("❌ Execution Intercepted & Blocked.")
                        append_to_audit_log("HITL Gate Result Decision Action", "BLOCKED BY USER INTERACTION GATES")
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": observation
                        })
                        continue  # Skip to next step sequence processing blocks loop tracking
                
                # Execute valid tools dynamically safely
                if function_name in TOOL_REGISTRY:
                    observation = TOOL_REGISTRY[function_name](**function_args)
                else:
                    observation = f"Error missing tool identifier registration link reference context."
                
                print(f"🛠️  Observation Response Generated Successfully.")
                append_to_audit_log(f"Tool Result Observation Output Capture: [{function_name}]", str(observation))
                
                # Feed result strings directly back into memory space pipelines
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(observation)
                })

if __name__ == "__main__":
    run_agent_chat_system()