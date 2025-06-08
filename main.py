# !pip install smolagents[litellm]
from smolagents import CodeAgent, LiteLLMModel, OpenAIServerModel, tool, WebSearchTool, FinalAnswerTool, PythonInterpreterTool, \
    UserInputTool
from src.tools.clean_system import clean_system
from src.tools.get_system_info import get_system_info
from src.tools.open_app import open_app
from src.tools.organize_folder import organize_folder
from src.tools.write_file import write_file
from typing import Any
from smolagents import Tool
from fastrtc import Stream, ReplyOnPause, get_stt_model, get_tts_model

from typing import Any
from smolagents import Tool

from smolagents import tool


model = OpenAIServerModel(
    model_id="deepseek-r1-0528-qwen3-8b",                # matches the model name in LM Studio
    api_base="http://localhost:1234/v1",  # LM Studio’s endpoint
    api_key="none"
)

agent = CodeAgent(tools=[
    ], max_steps=3, model=model, add_base_tools=True, additional_authorized_imports=['open','thefuzz','subprocess'] )


stt_model = get_stt_model()   # e.g. a tiny Whisper model
tts_model = get_tts_model()   # e.g. Orpheus-400M or Bark

# Optionally keep a transcript history if you want context in your prompts:
conversation = []

def handle_audio(audio_chunk):
    # 2) Convert speech bytes → text
    text = stt_model.stt(audio_chunk)
    if not text.strip():
        return  # sometimes VAD fires on noise

    print(f"[ASR] {text}")
    conversation.append({"role": "user", "content": text })

    # 3) Run your SmolAgent
    response = agent.run(text + "\n\n /no_think", reset=False)
    agent.stream_outputs = True

    conversation.append({"role": "assistant", "content": response})
    print(f"[Agent] {response}")

    # 4) Convert text → PCM chunks and stream back
    for pcm in tts_model.stream_tts_sync(response):
        yield pcm

# 5) Launch FastRTC’s Gradio UI
stream = Stream(
    handler=ReplyOnPause(handle_audio, input_sample_rate=16000, can_interrupt=True),
    modality="audio",
    mode="send-receive",

)

if __name__ == "__main__":
    stream.ui.launch(server_port=7860)
