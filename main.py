# !pip install smolagents[litellm]
from smolagents import CodeAgent, LiteLLMModel, OpenAIServerModel, tool, WebSearchTool, PythonInterpreterTool, \
    UserInputTool, FinalAnswerTool, GradioUI

from src.tools.clean_system import clean_system
from src.tools.get_system_info import get_system_info
from src.tools.open_app import open_app
from src.tools.organize_folder import organize_folder
from src.tools.write_file import write_file

model = OpenAIServerModel(
    model_id="qwen3-4b",                # matches the model name in LM Studio
    api_base="http://localhost:1234/v1",  # LM Studio’s endpoint
    api_key="none"
)

agent = CodeAgent(tools=[
      write_file,
      open_app,
get_system_info
    ], max_steps=3, model=model, add_base_tools=True, additional_authorized_imports=['open','thefuzz','subprocess'])


GradioUI(agent).launch()