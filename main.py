# !pip install smolagents[litellm]
from smolagents import CodeAgent, LiteLLMModel, OpenAIServerModel, tool, WebSearchTool, PythonInterpreterTool, \
    UserInputTool, FinalAnswerTool

from src.tools.clean_system import clean_system
from src.tools.organize import organize_folder
import subprocess
from pathlib import Path

@tool
def write_file(file_path: str, content: str) -> str:
    """
    Writes content to a file at the specified path.

    Args:
        file_path: Full path where to save the file. Examples:
            - "~/Documents/report.txt"
            - "/tmp/summary.log"
            - "../data/results.json"
            - "output.txt" (current directory)
            Can use ~ for home directory.
        content: String content to write to the file.

    Returns:
        str: Confirmation message with file path and size written.
    """
    try:
        path = Path(file_path).expanduser().resolve()
        print(f"Writing to file: {path}")

        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write the content
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        file_size = path.stat().st_size
        print(f"Successfully wrote {file_size} bytes to {path}")

        return f"File saved: {path} ({file_size} bytes)"

    except PermissionError as e:
        error_msg = f"Permission denied writing to {file_path}: {str(e)}"
        print(error_msg)
        raise
    except Exception as e:
        error_msg = f"Failed to write file {file_path}: {str(e)}"
        print(error_msg)
        raise


model = OpenAIServerModel(
    model_id="qwen3-4b",                # matches the model name in LM Studio
    api_base="http://localhost:1234/v1",  # LM Studio’s endpoint
    api_key="none"
)

agent = CodeAgent(tools=[
      write_file,
      organize_folder,
      clean_system,
    ], model=model, add_base_tools=True, additional_authorized_imports=['open'])

agent.run("""
How much storage can i clean? /no_think.
""")