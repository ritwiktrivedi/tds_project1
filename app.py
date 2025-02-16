# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "requests",
#     "python-dateutil",
#     "pandas",
#     "db-sqlite3",
#     "scipy",
#     "pybase64",
#     "python-dotenv",
#     "httpx",
#     "markdown",
#     "duckdb",
#     "bs4"
# ]
# ///


from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, PlainTextResponse
import uvicorn
import os
import requests
import subprocess
import json
import httpx
import duckdb
import markdown
import sqlite3
import re
import subprocess
from dateutil.parser import parse
from datetime import datetime
from pathlib import Path
from scipy.spatial.distance import cosine
from dotenv import load_dotenv

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET, POST"],
    allow_headers=["*"],
)

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

tools = [
    {
        "type": "function",
        "function": {
            "name": "task_a1",
            "description": "Install a package and run a script from a URL with provided arguments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "script_url": {
                        "type": "string",
                        "description": "The URL of the script to run."
                    },
                    "args": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "The arguments to pass to the script."
                    }
                },
                "required": ["script_url", "args"] 
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_a2",
            "description": "Format a markdown file using a specified version of Prettier.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prettier_version": {
                        "type": "string",
                        "description": "The version of the prettier formatter to use.",
                        "default": "prettier@3.4.2",
                        "pattern": r"prettier@\d+\.\d+\.\d+"
                    },
                    "filename": {
                        "type": "string",
                        "description": "The path to the markdown file to format.",
                        "default": "/data/format.md",
                        "pattern": r".*/(.*\.md)"
                    }
                },
                "required": ["prettier_version", "filename"] 
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_a3",
            "description": "Count the number of occurrences of a specific weekday in a date file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string", "pattern": r"/data/.*dates.*\.txt"
                    },
                    "targetfile": {
                        "type": "string", "pattern": r"/data/.*/(.*\.txt)"
                    },
                    "weekday": {
                        "type": "integer",
                        "enum": [0, 1, 2, 3, 4, 5, 6],
                        "description": "Weekday number (0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday)",
                    }
                },
                "required": ["filename", "targetfile", "weekday"] 
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_a4",
            "description": "Sort a JSON contacts file and save the sorted version to a target file.",
           "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                },
                "targetfile": {
                    "type": "string",
                    "pattern": r".*/(.*\.json)",
                }
            },
            "required": ["filename", "targetfile"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_a5",
            "description": "Retrieve the most recent log files from a directory and save their content to an output file.",
            "parameters": {
                "type": "object",
                 "properties": {
                    "log_dir_path": {
                        "type": "string",
                        "pattern": r".*/logs",
                        "default": "/data/logs"
                    },
                    "output_file_path": {
                        "type": "string",
                        "pattern": r".*/(.*\.txt)",
                        "default": "/data/logs-recent.txt"
                    },
                    "num_files": {
                        "type": "integer",
                        "minimum": 1,
                        "default": 10
                    }
                },
                "required": ["log_dir_path", "output_file_path", "num_files"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_a6",
            "description": "Generate an index of documents from a directory and save it as a JSON file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_dir_path": {
                        "type": "string",
                        "pattern": r".*/docs",
                        "default": "/data/docs"
                    },
                    "output_file_path": {
                        "type": "string",
                        "pattern": r".*/(.*\.json)",
                        "default": "/data/docs/index.json"
                    }
                },
                "required": ["doc_dir_path", "output_file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_a7",
            "description": "Extract the sender's email address from a text file and save it to an output file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "pattern": r".*/(.*\.txt)",
                        "default": "/data/email.txt"
                    },
                    "targetfile": {
                        "type": "string",
                        "pattern": r".*/(.*\.txt)",
                        "default": "/data/email-sender.txt"
                    }
                },
                "required": ["filename", "targetfile"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_a8",
            "description": "Identify the 16-digit credit card number in the image and return it without spaces.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "pattern": r".*/(.*\.txt)",
                        "default": "/data/credit-card.txt"
                    },
                    "image_path": {
                        "type": "string",
                        "pattern": r".*/(.*\.png)",
                        "default": "/data/credit-card.png"
                    }
                },
                "required": ["filename", "image_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_a9",
            "description": "Find similar comments from a text file and save them to an output file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "pattern": r".*/(.*\.txt)",
                        "default": "/data/comments.txt"
                    },
                    "output_filename": {
                        "type": "string",
                        "pattern": r".*/(.*\.txt)",
                        "default": "/data/comments-similar.txt"
                    }
                },
                "required": ["filename", "output_filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_a10",
            "description": "Identify high-value (gold) ticket sales from a database and save them to a text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "pattern": r".*/(.*\.db)",
                        "default": "/data/ticket-sales.db"
                    },
                    "output_filename": {
                        "type": "string",
                        "pattern": r".*/(.*\.txt)",
                        "default": "/data/ticket-sales-gold.txt"
                    },
                    "query": {
                        "type": "string",
                        "pattern": "SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'"
                    }
                },
                "required": ["filename", "output_filename", "query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_b12",
            "description": "Check if filepath starts with /data",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_b3",
            "description": "Download content from a URL and save it to the specified path.",
            "parameters": {
                "type": "object",
                "properties": {
                   "url": {
                    "type": "string",
                    "pattern": r"https?://.*",
                    "description": "URL to download content from."
                },
                "save_path": {
                    "type": "string",
                    "pattern": r".*/.*",
                    "description": "Path to save the downloaded content."
                }
                },
                "required": ["url", "save_path"]
            }    
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_b4",
            "description": "Clones a specific Git repository to a predefined location within the allowed data directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_url": {
                        "type": "string",
                        "description": "The url of the repository to clone (e.g., 'https://github.com/user/repo')."
                    },
                    "commit_message": {
                        "type": "string",
                        "description": "The commit message to include in the cloned repository."
                    }
                },
                "required": ["repo_name", "commit_message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_b5",
            "description": "Runs an SQL query on a database and saves the results to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_path": {
                        "type": "string",
                        "pattern": r".*/(.*\.db)",
                        "description": "The path to the database file."
                    },
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute on the database."
                    },
                    "output_filename": {
                        "type": "string",
                        "pattern": r".*/(.*\.txt)", 
                        "description": "The filename to save the query results to."
                    }    
                },
                "required": ["db_path", "query", "output_filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_b6",
            "description": "Scrapes content from a website and saves it to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "pattern": r"https?://.*",
                        "description": "The URL to scrape content from."
                    },
                    "output_filename": {
                        "type": "string",
                        "pattern": r".*/(.*\.txt)",
                        "description": "The filename to save the scraped content to."
                    }
                },
                "required": ["url", "output_filename"]
            }    
        }   
    },
    {
        "type": "function",
        "function": {
            "name": "task_b7",
            "description": "Compress or resize an image and save it to a specified path within the allowed data directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "pattern": r".*/(.*\.(jpg|jpeg|png|gif|bmp))",
                        "description": "Path to the input image file."
                    },
                    "output_path": {
                        "type": "string",
                        "pattern": r".*/.*",
                        "description": "Path to save the processed image."
                    },
                    "resize": {
                        "type": "array",
                        "items": {
                            "type": "integer",
                            "minimum": 1
                        },
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Optional. Resize dimensions as [width, height]."
                    }
                },
                "required": ["filename", "image_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_b8",
            "description": "Transcribes an audio file to text using OpenAI's Whisper model.",
            "parameters": {
                "type": "object",
                "properties": {
                    "audio_path": {
                        "type": "string",
                        "pattern": r".*/(.*\.(mp3|wav|ogg|flac))",
                        "description": "Path to the input audio file."
                    }
                },
                "required": ["audio_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_b9",
            "description": "Converts a Markdown file to HTML and saves the result to an output file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "md_path": {
                        "type": "string",
                        "pattern": r".*/(.*\.md)",
                        "description": "Path to the Markdown file to be converted."
                    },
                    "output_path": {
                        "type": "string",
                        "pattern": r".*/(.*\.html)",
                        "description": "Path to save the converted HTML file."
                    }
                },
                "required": ["md_path", "output_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "task_b10",
            "description": "Filter a CSV file using a specified query and return the filtered data as JSON.",
            "parameters": {
                "type": "object",
                "properties": {
                    "csv_path": {
                        "type": "string",
                        "pattern": r".*/(.*\.csv)",
                        "description": "Path to the input CSV file."
                    },
                    "query": {
                        "type": "string",
                        "description": "The query to filter the data."
                    }
                },
                "required": ["csv_path", "query"]
            }
        }
    },
]


# Phase A: LLM-based Automation Agent for DataWorks

# Task A1: Run a Python script from a given URL, passing an email as the argument.
def task_a1(script_url, args=['22f1000120@ds.study.iitm.ac.in']):
    # Download script and run it using uv
    subprocess.run(["curl", "-o", "/tmp/datagen.py", script_url], check=True)
    subprocess.run(["uv", "run", "/tmp/datagen.py", *args], check=True)

# Task A2: Format a markdown file using a specified version of Prettier.
def task_a2(prettier_version, filename):
    import os
    if not os.path.isfile(filename):
        raise Exception(f"File {filename} not found for formatting.")
    command = ["npx", f"prettier", "--write", filename]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("Prettier executed successfully.")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Prettier formatting failed:\n{e.stderr}")

# Task A3: Count the number of occurrences of a specific weekday in a date file.
def task_a3(filename, targetfile, weekday):
    from dateutil.parser import parse
    count = 0
    with open(filename, "r") as f:
        for line in f:
            try:
                # Force date-only to avoid time shifts
                dt = parse(line).date()
                if dt.strftime("%A").lower() == {0:"monday",1:"tuesday",2:"wednesday",3:"thursday",4:"friday",5:"saturday",6:"sunday"}[weekday]:
                    count += 1
            except:
                pass
    with open(targetfile, "w") as f:
        f.write(str(count))

# Task A4: Sort a JSON contacts file and save the sorted version to a target file.
def task_a4(filename, targetfile):
    with open(filename, "r") as f:
        contacts = json.load(f)
    sorted_contacts = sorted(contacts, key=lambda x: (x['last_name'], x['first_name']))
    with open(targetfile, "w") as f:
        json.dump(sorted_contacts, f, ensure_ascii=False)

# Task A5: List the most recent 10 log files in a directory and save the list to a target file.
def task_a5(log_dir_path, output_file_path, num_files):
    log_dir = Path(log_dir_path)
    output_file = Path(output_file_path)
    log_files = sorted(log_dir.glob('*.log'), key=os.path.getmtime, reverse=True)[:num_files]
    with output_file.open('w') as f_out:
        for log_file in log_files:
            with log_file.open('r') as f_in:
                first_line = f_in.readline().strip()
                f_out.write(f"{first_line}\n")

#Task A6: Scan a directory for markdown files, extract the first H1 title from each, and create an index.json file mapping file paths to titles.
def task_a6(doc_dir_path, output_file_path):
    index_data = {}
    try:
        doc_dir = Path(doc_dir_path)
        output_file = Path(output_file_path)
        for md_file in doc_dir.glob('*.md'):
            with md_file.open('r') as f:
                for line in f:
                    if line.startswith('# '):  # Find first H1
                        title = line[2:].strip()
                        relative_path = md_file.relative_to(doc_dir).with_suffix('').as_posix().replace('\\', '/')
                        index_data[relative_path] = title
                        break  # Stop after first H1
    except Exception as e:
        print(f"Error reading {md_file}: {e}")
    try:
        with output_file.open('w') as f_out:
            json.dump(index_data, f_out, indent=4)
    except Exception as e:
        print(f"Error writing {output_file}: {e}")

# from pathlib import Path

# def task_a6(doc_dir_path, output_file_path):
#     index_data = {}
#     try:
#         doc_dir = Path(doc_dir_path)  # Ensure doc_dir_path is a Path object
#         output_file = Path(output_file_path)

#         for md_file in doc_dir.glob('*.md'):
#             try:  # Inner try-except for individual files
#                 with md_file.open('r', encoding='utf-8') as f: # add encoding
#                     for line in f:
#                         if line.startswith('# '):
#                             title = line[2:].strip()
#                             # Key change: Construct relative path correctly
#                             relative_path = os.path.relpath(md_file, doc_dir).replace('\\', '/')
#                             index_data[relative_path] = title
#                             break
#             except Exception as e:
#                 print(f"Error reading {md_file}: {e}") # print specific error for each file

#     except Exception as e:
#         print(f"Error accessing directory: {e}")

#     try:
#         with output_file.open('w', encoding='utf-8') as f_out: # add encoding
#             json.dump(index_data, f_out, indent=2)  # Add indent for readability
#     except Exception as e:
#         print(f"Error writing {output_file}: {e}")

# Task A7: Extract the sender's email address from a text file and save it to an output file.
def task_a7(filename='/data/email.txt', targetfile='/data/email-sender.txt'):
     # Read the content of the email
    with open(filename, 'r') as file:
        email_content = file.readlines()

    sender_email = ""
    for line in email_content:
        if "From" == line[:4]:
            sender_email = (line.strip().split(" ")[-1]).replace("<", "").replace(">", "")
            break

    # Get the extracted email address

    # Write the email address to the output file
    with open(targetfile, 'w') as file:
        file.write(sender_email)
    
    
    # with open(filename, 'r') as file:
    #     email_content = file.readlines()

    # sender_email = ""
    # for line in email_content:
    #     # Look for a line starting with "From:" (case-insensitive)
    #     if line.strip().lower().startswith("from:"):
    #         # Remove quotes if any, and angle brackets
    #         cleaned = line.replace('"', '').replace('<','').replace('>','').strip()
    #         sender_email = cleaned.split()[-1]
    #         break

    # with open(targetfile, 'w') as file:
    #     file.write(str(sender_email))

import base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read()).decode('utf-8')
    return base64_string

# Task A8: Generate an image representation of credit card details from a text file.
def task_a8(filename, image_path):
    # Construct the request body for the AIProxy call
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "The image contains a number formatted in groups separated by spaces. "
                            "Extract the full number in credit card format exactly as it appears, remove all spaces, and "
                            "return only the digits without any extra characters."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_to_base64(image_path)}"
                        }
                    }                
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }

    response = requests.post("https://aiproxy.sanand.workers.dev/openai/v1/chat/completions", headers=headers, json=body)
    response_data = response.json()
    generated_text = response_data["choices"][0]["message"]["content"].replace(" ", "").strip()
    with open(filename, "w") as f:
        f.write(generated_text)


def get_embedding(text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    data = {
        "model": "text-embedding-3-small",
        "input": [text]
    }
    response = requests.post("http://aiproxy.sanand.workers.dev/openai/v1/embeddings", headers=headers, data=json.dumps(data))
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]

# Task A9: Find similar comments from a text file and save them to an output file.
def task_a9(filename, output_filename):
    # Joining path components
    file_path = Path("/data") / filename
    # Getting the absolute path
    abs_path = file_path.resolve()
    from scipy.spatial.distance import cosine
    # Read the comments
    with open(abs_path, 'r', encoding='utf-8') as f:
        comments = [line.strip() for line in f if line.strip()]
    # Get embeddings for all
    embeddings = [get_embedding(comment) for comment in comments]
    # Find the pair with the smallest cosine distance
    min_dist = float('inf')
    pair = ("","")
    for i in range(len(comments)):
        for j in range(i+1, len(comments)):
            dist = cosine(embeddings[i], embeddings[j])
            if dist < min_dist:
                min_dist = dist
                pair = (comments[i], comments[j])
    # Write them sorted by line
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(sorted([pair[0], pair[1]])))

# Task A10: Identify high-value (gold) ticket sales from a database and save them to a text file.
def task_a10(filename, output_filename, query):
    # Execute the query to find total sales
    conn = sqlite3.connect(f"/data/{filename}.db") if filename.endswith('.db') else duckdb.connect(filename)
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchone()
    conn.close()
    total = result[0] if result else 0
    with open(output_filename, "w") as f:
        f.write(str(total))


# Phase B: Handle Business Tasks

# Task B1:
# we are checking for this in the read endpoint

# Task B2: 
def task_b2(task_description):
    # Allow these keywords (case-insensitive)
    allowed_keywords = ["create", "edit", "modify", "write", "append", "generate", "process", "update"]

    # Block these keywords (case-insensitive)
    blocked_keywords = ["delete", "remove", "rm", "unlink", "erase", "destroy", "purge"]

    for keyword in blocked_keywords:
        if re.search(r"\b" + keyword + r"\b", task_description, re.IGNORECASE):  # Improved regex
            raise ValueError(f"Task description contains a request for file deletion ('{keyword}'), which is not allowed.")

# Task B3: Fetch Data from an API and save it
def task_b3(url, save_path):
    response = requests.get(url)
    with open(save_path, "w") as f:
        f.write(response.text)

# Task B4: Clone a Git Repo and Make a Commit
def task_b4(repo_url, commit_message):
    import subprocess
    subprocess.run(["git", "clone", repo_url, "/data/repo"])
    subprocess.run(["git", "-C", "/data/repo", "commit", "-m", commit_message])

# Task B5: Run SQL Query and save result in target file.
def task_b5(db_path, query, output_filename):
    conn = sqlite3.connect(db_path) if db_path.endswith('.db') else duckdb.connect(db_path)
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.close()
    with open(output_filename, 'w') as file:
        file.write(str(result))
    return result

# Task B6: Web Scraping
def task_b6(url, save_path):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    with open(save_path, 'w') as f:
        f.write(soup.prettify())

# Task B7: Compress or Resize an Image
def task_b7(image_path, save_path, resize=None):
    from PIL import Image
    img = Image.open(image_path)
    if resize:
        img = img.resize(resize)
    img.save(save_path)

# Task B8: Transcribe an Audio file
import subprocess

def task_b8(audio_path):
    try:
        # Run Whisper CLI via subprocess
        result = subprocess.run(
            ["npx","whisper", audio_path, "--model", "tiny"],  # Use "tiny" for lightweight processing
            capture_output=True,  # Capture the command output
            text=True  # Decode output as text
        )
        # Check if the command was successful
        if result.returncode == 0:
            return result.stdout  # Return the transcript
        else:
            return f"Error: {result.stderr}"  # Return error message if it fails

    except Exception as e:
        return f"Exception: {str(e)}"

# Task B9: Convert Markdown to HTML
def task_b9(markdown_path, html_path):
    import markdown
    with open(markdown_path, 'r') as f:
        markdown_text = f.read()
    html = markdown.markdown(markdown_text)
    with open(html_path, 'w') as f:
        f.write(html)

# Task B10: Filter a CSV file using a specified query and return the filtered data as JSON.
def task_b10(csv_path, query):
    import pandas as pd 
    df = pd.read_csv(csv_path)
    filtered = df.query(query)
    return filtered.to_json(orient='records')

@app.get("/")
def home():
    return {"message": "Hello World from TDS Project 1"}

@app.get("/read")
def read_file(path: str):
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return HTTPException(status_code=404, detail=str("File does not exist"))

# ALLOWED_DATA_PATH = "/data"
# @app.get("/read", response_class=PlainTextResponse)
# async def read_file(path: str):
#     try:
#         # Security check: Ensure path is within ALLOWED_DATA_PATH
#         abs_path = os.path.abspath(path)
#         if not abs_path.startswith(ALLOWED_DATA_PATH):
#             raise HTTPException(status_code=403, detail="Forbidden: Access outside /data is not allowed.")

#         with open(path, "r") as file:
#             return file.read()
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="File not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/run")
def task_runner(task: str):
    # try:
    #     task_b2(task)  # to handle deletion logic by checking for blocked keywords
    # except ValueError as ve:
    #     raise HTTPException(status_code=400, detail=str(ve))

    try:
        url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AIPROXY_TOKEN}",
        }
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": task
                },
                {
                    "role": "assistant",
                    "content": """
    You are an assistant who has to do a variety of tasks.
    If your task involves running a script, you can use the task_a1 tool.
    If your task involves formatting a markdown file, you can use the task_a2 tool.
    """
                }
            ],
            "tools": tools,
            "tool_choice": "auto"
        }
        response = requests.post(url=url, headers=headers, json=data)
        response.raise_for_status()

        arguments = response.json()["choices"][0]["message"]["tool_calls"][0]["function"]
        chosen_function = eval(arguments["name"])
        params = json.loads(arguments["arguments"])

        print(f"Chosen function: {chosen_function.__name__} with params: {params} was called")

        # Run the chosen function with the provided parameters
        chosen_function(**params)

        return {"Message": f'{chosen_function.__name__} has been executed with params {params}'}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error with API: {e}")
    except KeyError as ke:
        raise HTTPException(status_code=400, detail=f"Error in task: {ke}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)