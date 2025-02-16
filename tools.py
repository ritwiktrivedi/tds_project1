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
                        "type": "integer", "pattern": r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
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
            "description": "Generate an image representation of credit card details from a text file.",
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