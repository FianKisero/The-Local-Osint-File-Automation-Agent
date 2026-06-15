import os
import subprocess
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

# System sandbox constraints
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/workspace"))
os.makedirs(WORKSPACE_DIR, exist_ok=True)

def safe_path(filename):
    """Ensures file access stays strictly inside data/workspace."""
    target_path = os.path.abspath(os.path.join(WORKSPACE_DIR, filename))
    if not target_path.startswith(WORKSPACE_DIR):
        raise PermissionError("Access denied: Attempted to leave sandbox workspace.")
    return target_path

# ==========================================
# 1. CORE FILE TOOLS
# ==========================================
def list_workspace_files():
    """Lists all files available in the local workspace sandbox."""
    try:
        return os.listdir(WORKSPACE_DIR)
    except Exception as e:
        return f"Error listing files: {str(e)}"

def read_workspace_file(filename):
    """Reads raw text content from a specific file within the workspace."""
    try:
        path = safe_path(filename)
        if not os.path.exists(path):
            return f"Error: File '{filename}' does not exist."
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()[:3000]
    except Exception as e:
        return str(e)

def write_workspace_file(filename, content):
    """Writes or overwrites text content to a file inside the workspace."""
    try:
        path = safe_path(filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Success: Content written to {filename}."
    except Exception as e:
        return str(e)

# ==========================================
# 2. FEATURE 1: WEB SCRAPING & RESEARCH
# ==========================================
def scrape_web_page(url):
    """Fetches a web page URL and strips out HTML to return clean text."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Strip script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text(separator="\n")
        # Clean up excessive spacing chunks
        cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(cleaned_lines)[:4000]  # Cap context injection safety
    except Exception as e:
        return f"Failed to scrape web page: {str(e)}"

# ==========================================
# 3. FEATURE 4: TERMINAL EXECUTION SANDBOX
# ==========================================
def run_terminal_command(command):
    """Executes safe, basic runtime terminal scripts strictly within the workspace."""
    # Strict safety constraint checklist
    forbidden_keywords = ["rmdir /s", "del /f", "rm -rf", "format", "shutdown"]
    if any(forbidden in command.lower() for forbidden in forbidden_keywords):
        return "Security Violation: Command contains restricted operational destructive keywords."
        
    try:
        # Enforce execution entirely inside the data/workspace folder context
        result = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE_DIR,
            text=True,
            capture_output=True,
            timeout=15
        )
        output = result.stdout if result.stdout else ""
        errors = result.stderr if result.stderr else ""
        return f"STDOUT:\n{output}\nSTDERR:\n{errors}"
    except Exception as e:
        return f"Execution error: {str(e)}"

# ==========================================
# 4. FEATURE 5: MULTI-FORMAT PARSER (PDF Reader)
# ==========================================
def read_pdf_document(filename):
    """Extracts raw text text layouts sequentially page-by-page from a local workspace PDF file."""
    try:
        path = safe_path(filename)
        if not os.path.exists(path):
            return f"Error: PDF '{filename}' does not exist."
            
        reader = PdfReader(path)
        extracted_text = []
        for index, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_text.append(f"--- Page {index + 1} ---\n{page_text}")
                
        full_text = "\n".join(extracted_text)
        return full_text[:4000] if full_text else "Warning: PDF contains no readable text stream layout."
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# ==========================================
# TOOL REGISTRIES AND SCHEMAS
# ==========================================
TOOL_REGISTRY = {
    "list_workspace_files": list_workspace_files,
    "read_workspace_file": read_workspace_file,
    "write_workspace_file": write_workspace_file,
    "scrape_web_page": scrape_web_page,
    "run_terminal_command": run_terminal_command,
    "read_pdf_document": read_pdf_document
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "list_workspace_files",
            "description": "Lists files within your workspace directory.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_workspace_file",
            "description": "Reads text contents from a specific workspace file.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string", "description": "Filename string"}},
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_workspace_file",
            "description": "Writes or overwrites standard content onto files inside the workspace sandbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Output filename targeting workspace location"},
                    "content": {"type": "string", "description": "Raw data stream message payload template body text"}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_web_page",
            "description": "Scrapes a remote URL link address target source code and strips out HTML down to pure clean readable markdown paragraphs.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "The precise web url to read"}},
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_terminal_command",
            "description": "Runs localized terminal CLI commands inside the workspace directory (e.g. running python scripts, check status).",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "The literal CLI string instruction"}},
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_pdf_document",
            "description": "Reads and extracts readable raw structural text page arrays from local PDF file targets saved inside workspace directories.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string", "description": "The target PDF file name target"}},
                "required": ["filename"]
            }
        }
    }
]