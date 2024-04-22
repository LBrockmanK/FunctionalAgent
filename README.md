[Original Discussion](https://www.reddit.com/r/AutoGenAI/comments/1c08e7l/more_deterministic_function_calling/)

[Example project using autogen and guidance inside a broader application](https://github.com/disler/multi-agent-postgres-data-analytics/tree/v6-control-flow-and-structured-response) (Multiple versions through project, we probably want 6 or later)

###### Goal / Outline

---

Autogen agents with function calling or code execution suffer from both overhead and ambiguity, many application do not require the flexibility they offer, and that added flexibility comes with increased cost in time and inference, as well as reduced reliability (I am not aware of any model that can do either reliably, in this new version, function execution will be determined by group chat manager selecting the agent if agent selection is open ended, by agent order if deterministic, or both depending on the structure of the group chat). Thus we want to make a minimalist implementation of agent function calling based on the following core principles:

1. Minimal LLM usage, LLM should only be used for tasks that cannot be done by traditional computing
   1. LLM will be used only to generate arguments for the function based on predefined decorator / definition system prompt
   2. Option should exist to use user input for arguments instead
   3. Setting should exist to limit viable inputs (range of values, selection of options from a list, etc)
      1. Should be able to retry if invalid input is received, configurable number of retries
2. All flexibility should be front loaded in the creation of the agent, allowing developers to customize it for their needs
3. The agent should be self contained, using message history for context, but not requiring particular inputs from them
4. Wherever possible use existing features of autogen and already required libraries to minimize long term upkeep effort
5. Different portions of information (inputs / outputs / instructions) may be configured to determine whether or not they will be returned to the conversation and added to the message history
   1. Not all functions will exist to contribute to the conversation, some may exist to take actions in a broader application based on the conversation
6. The functions being used will be defined externally and passed as arguments, care should be given to allow easy integration with a broader application
   1. If possible, include a way for return values to be sent to the broader application, or if not provide guidelines on structuring functions to do this internally and update data in the broader application as needed

###### Initial Technical Thoughts

- Guidance library is not used in base autogen, but can be used with it though I haven't looked at the examples yet, review them and maintain the usability with this
- Other specialized agents are children of ConversableAgent class, we could will start with that method, might need to override certain functionality we don't want to include with blank functions
  - Ideally override the existing function calling code to modify it for our needs
  - Need to do more research into existing function calling logic, it's possible the desired behavior could be achieved just by hard coding some of the variables in the parent class to restrict functionality along with minor alterations
  - On the other hand, I wouldn't exactly call this agent 'conversable'

###### Research into Autogen Code:

- Review conversable agent and related code in detail
  - Conversable Agent Class Info
    - To modify auto reply, override `generate_reply` method.
      - We could override this and throw out a lot of the existing routines related to it, it would be straightforward but remove any compatibility with the existing features for the most part
      - Adding handling for our function to the start of the registered reply list and always returning final would be an easy way to prevent the later code from firing, or not and allowing more general agent behavior to follow if we were to simply add deterministic function calling to the available code execution options.
        - Alternatively might have our LLM call for input to the list of registered reply list followed by our actual function execution
        - Users may still want to possibly execute other registered replies like termination check, possibly not function / tool calls
          - While there might be a theoretical use case to continuing on to function / tool calls, this can just as well be left to another agent but if it doesn't cause trouble we can leave the possibility in
        - Only change needed would be an expanded init function for new inputs and to add replies to the list, and creation of the new reply functions (not insignificant since those need to be very flexible, but much less than it could be)
        - This case could work without even needing to make a child class, though it would add to the clutter of Conversable Agent
    - To disable/enable human response in every turn, set `human_input_mode` to "NEVER" or "ALWAYS".
      - While it wouldn't be common, I can see cases where one might want to go back and forth with the functional agent in a format akin to a conversation like with conversable agents, such as if you're using it to control an application with natural language.
    - To modify the way to get human input, override `get_human_input` method.
      - Might be relevant if we want to allow user to provide function inputs directly, might need to include some kind of format checks before accepting and change the prompt to provide format guidelines / required fields
        - This one is a point in favor of a child class, it would really clutter things up to add these special cases along with what's already there
    - To modify the way to execute code blocks, single code block, or function call, override `execute_code_blocks`,`run_code`, and `execute_function` methods respectively.
      - We obviously don't won't to use openai function calling, we want this to be generic and also not rely on an LLM handling the code
      - Possible we may modify execute function to serve our purposes if we intend to remove other code execution as a possibility, we will likely steal a lot of the code for our own
        - execute_function seems to be what we want as a basis? It calls out the openai API in the descriptor but doesn't actually seem to use it
          - It seems like the only way it gets inputs is OpenAI function calls in a sort of wrapper function, might work for us if we just give it an actual function but not sure until tested
  - Other
    - Conversable Agent class seems like a bit of a mess with different features added. Since LLMAgent its parent is just an API it would be nice if Conversable Agent was just a conversational implementation with function calling or code execution added further down the line of inheritance. That might make things more confusing for specialized agent classes included with the library if they then also need different versions based on supported features.
- Review examples of Guidance library used with Autogen
  - [Example](https://github.com/microsoft/autogen/blob/main/notebook/agentchat_guidance.ipynb)
    - Basically just registering a new response function for the agent like we intend to do so easy to implement
    - Theoretically we could make a proof of concept of our agent in a similar manner, but it would likely require a custom agent for each function we want to test (registering a reply with a registered function)

###### Results of Initial Review

- Desired functionality should be achievable with the addition of new a new function (or possibly two) to the agent register reply list, this could be achieved inside Conversable Agent or as a child class
  - Child class likely a better choice of initial implementation, less likely to butt heads if merged to main library and can be worked back into Conversable Agent if needed and resolve some of the complexities at that time
- We can include an option for the agent to generate replies based on the result of the function call if so desired, if we are making this a child or part of conversable agent, that seems appropriate (response generation further down from function execution which is non final)
  - This is how existing function calling / code execution and response generation are ordered
- Key functions to add / extend
  - Init function will need additional inputs for registered function and supporting information
  - Local code execution support will need to be added (or modified from existing code) to execute function
  - check_termination_and_human_reply will need to be modified to cleanly support function inputs
    - This is independent of any instructions / context coming from other agents in message history which may inform the generation but are not direct inputs
