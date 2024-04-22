from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Type, TypeVar, Union
from autogen import ConversableAgent
from autogen.agentchat.agent import Agent

# Do we want to build guidance in from the beginning?

# 1. Implement a wrapper function that executes our function, no args so far, and add it to the list
# 2. Update wrapper to apply args / kwargs to the function but keep them preset for now
# 3. Add new registered function which generates formatter args / kwargs (with guidance?) and save it to a variable accessible by the wrapper (wipes to NULL after use)
# 4. Update human input to allow for adding arguments, add protections to make sure they are valid, use decorator strings to inform user for input and go through the arg list
#   a. change default arg generation to only occur if arguments are not already set (still NULL)
# 5. Add configuration for what information is returned to the chat and what isn't (by default beforehand only include return value, maybe argument prompt?)
# 6. Provide guidelines, missing value checks, demo, etc. Run test cases to ensure it works as intended

class FunctionalAgent(ConversableAgent):
    """A class for reliable function execution in group chats"""

    def __init__(
        self,
        function: Callable = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        # Register function to be executed
        self.function = function

        if self.function is None:
            raise ValueError("No function provided to execute")
        
        # Init function will need additional inputs for registered function and supporting information, can do this last

    # We can include an option for the agent to generate replies based on the result of the function 
    # call if so desired, if we are making this a child or part of conversable agent, that seems appropriate 
    # (response generation further down from function execution which is non final)
    # This is how existing function calling / code execution and response generation are ordered

    def generate_reply(self, messages: List[Dict[str, Any]] | None = None, sender: Agent | None = None, **kwargs: Any) -> str | Dict | None:
        return super().generate_reply(messages, sender, **kwargs)
        # Need to register new functions and possibly remove certain registered functions and ensure intended order, one of those
        #   Instead of removing may just default to no contents for things like code execution or function calling (original)
        # new functions will be our input function to execute or a wrapper around it
        # Probably don't need to actually modify this function, just add our own registered functions
    
    def a_generate_reply(self, messages: List[Dict[str, Any]] | None = None, sender: Agent | None = None, **kwargs: Any) -> Coroutine[Any, Any, str | Dict[str, Any] | None]:
        return super().a_generate_reply(messages, sender, **kwargs)
    
    # check_termination_and_human_reply will need to be modified to cleanly support function inputs
    # This is independent of any instructions / context coming from other agents in message history which may inform the generation but are not direct inputs

    def get_human_input(self, prompt: str) -> str:
        return super().get_human_input(prompt)
    
    def a_get_human_input(self, prompt: str) -> Coroutine[Any, Any, str]:
    
    def check_termination_and_human_reply(self, messages: List[Dict] | None = None, sender: Agent | None = None, config: Any | None = None) -> Tuple[bool, str | None]:
        return super().check_termination_and_human_reply(messages, sender, config)
    
    def a_check_termination_and_human_reply(self, messages: List[Dict] | None = None, sender: Agent | None = None, config: Any | None = None) -> Coroutine[Any, Any, Tuple[bool, str | None]]:
        return super().a_check_termination_and_human_reply(messages, sender, config)
    
    # Local code execution support will need to be added (or modified from existing code) to execute function
    # Should just be a wrapper that takes the input recieved from the LLM and calls the function with it
    # Possibly have functions without inputs? If so, need to handle that case

    def functional_wrapper(self) -> str:
        pass

    def functional_args(self, *args, **kwargs) -> bool:
        pass

    