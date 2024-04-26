from functional_agent import FunctionalAgent

import time

from typing_extensions import Annotated

import autogen
from autogen.cache import Cache
import os

import asyncio

import logging

# Configure logging to write to 'devlog' in the current directory
logging.basicConfig(filename='devlog',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set up API
llm_config = {"model": "gpt-3.5-turbo",
              "api_key": os.environ["OPENAI_API_KEY"]}

mycounter = 0

def myfunc():
    global mycounter
    mycounter += 1
    print(f"Counter: {mycounter}")
    return str(mycounter)

# Create Agents (Just copy pasted these from another project for spot check, should customize them later)
coder = FunctionalAgent(
    name="chatbot",
    system_message="For coding tasks, only use the functions you have been provided with. You have a stopwatch and a timer, these tools can and should be used in parallel. Reply TERMINATE when the task is done.",
    llm_config=llm_config,
    function=myfunc,
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    system_message="A proxy for the user for executing code.",
    is_termination_msg=lambda x: x.get("content", "") and x.get(
        "content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding", "use_docker": False},
)

# NEXT: Add another agent to interact with the functional agent, test it out
# NEXT: Add code to generate function inputs with LLM, test it out

def test_functional_agent():
    with Cache.disk() as cache:
        user_proxy.initiate_chat(
                coder,
                message="Create a timer for 5 seconds and then a stopwatch for 5 seconds.",
                cache=cache,
        )
    for key, value in user_proxy.chat_messages.items():
        print(f"{key}: {value}")
        logging.debug(f"{key}: {value}")
    

if __name__ == "__main__":
    test_functional_agent()