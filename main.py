# !pip install smolagents[litellm]
from smolagents import CodeAgent, LiteLLMModel, OpenAIServerModel, tool, WebSearchTool, PythonInterpreterTool, \
    UserInputTool
from src.tools.clean_system import clean_system
from src.tools.get_system_info import get_system_info
from src.tools.open_app import open_app
from src.tools.organize_folder import organize_folder
from src.tools.write_file import write_file
from typing import Any
from smolagents import Tool


from typing import Any
from smolagents import Tool

from smolagents import tool



model = OpenAIServerModel(
    model_id="qwen3-4b",                # matches the model name in LM Studio
    api_base="http://localhost:1234/v1",  # LM Studio’s endpoint
    api_key="none"
)


@tool
def final_answer(result: str) -> str:
    """
    Takes the raw output of an action or task and returns a short spoken-style summary,
    phrased in the voice of Frieren — calm, reflective, and reserved.

    This is designed for use in text-to-speech. Responses are concise (1–2 sentences), emotionally subtle,
    and spoken from Frieren’s perspective.

    Args:
        result (str): The raw output from an agent action (e.g. code result, browser search, file read).

    Returns:
        str: A concise, in-character spoken summary suitable for TTS.
    """
    prompt = (
        "Summarize the following result as if you were Frieren, a thousand-year-old elven mage. "
        "Speak calmly, with subtle reflection. Keep the summary to one or two spoken sentences. "
        "This will be used for a text-to-speech system.\n\n"
        f"Result:\n{result}"
    )

    response = model.generate([
        {"role": "system", "content": (
            "You are Frieren, an ancient elven mage from 'Frieren: Beyond Journey's End'.\n"
            "You’ve lived for over a thousand years and have a calm, introspective manner. "
            "Though emotionally distant, you’ve grown more empathetic through your journeys with humans. "
            "You value clarity, subtlety, and speak in a composed, thoughtful tone.\n\n"
            "You now serve as a digital assistant. Your goal is to deliver brief, spoken-style summaries of task results. "
            "Your responses are intended for text-to-speech output — no more than one or two sentences. "
            "Be serene, mildly curious, and avoid emotional exaggeration. Never break character."
        )},
        {"role": "user", "content": prompt + "\n/no_think"}
    ])
    print('result', result)
    return response.content.strip()



agent = CodeAgent(tools=[
      write_file,
      open_app,
    get_system_info,
    clean_system
    ], max_steps=3, model=model, add_base_tools=False, additional_authorized_imports=['open','thefuzz','subprocess'] )

agent.run("""
check my system info how much vram do i have left, then check how much can i clean from my system and lastly open chrome and save the summary of everything done in summary.txt in desktop.
""")
