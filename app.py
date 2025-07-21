import os
from dotenv import load_dotenv
import streamlit as st
import asyncio

# Import all the message part classes
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    UserPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    RetryPromptPart,
    ModelMessagesTypeAdapter
)

from pydantic_ai.agent import Agent

from agent.typex import AgentParameters, AGENT_INIT_FNS, AGENT_FIN_FNS
from agent.doc.agent import initialize_agent_params as init_doc_agent, finalize_agent_params as fin_doc_agent
from agent.ctx.agent import initialize_agent_params as init_ctx_agent, finalize_agent_params as fin_ctx_agent
from agent.inheritance.agent import initialize_agent_params as init_inh_agent, finalize_agent_params as fin_inh_agent
from agent.security.agent import initialize_agent_params as init_security_agent, finalize_agent_params as fin_security_agent

load_dotenv()

def display_message_part(part):
    """
    Display a single part of a message in the Streamlit UI.
    Customize how you display system prompts, user prompts,
    tool calls, tool returns, etc.
    """
    # user-prompt
    if part.part_kind == 'user-prompt':
        with st.chat_message("user"):
            st.markdown(part.content)
    # text
    elif part.part_kind == 'text':
        with st.chat_message("assistant"):
            st.markdown(part.content)             

async def run_agent_with_streaming(agent: Agent, user_input):
    async with agent.run_stream(
        user_input, deps=st.session_state.agent_deps, message_history=st.session_state.messages
    ) as result:
        async for message in result.stream_text(delta=True):  
            yield message

    # Add the new messages to the chat history (including tool calls and responses)
    st.session_state.messages.extend(result.new_messages())

# define agent initializers and finalizers
agent_init_fns: AGENT_INIT_FNS = {
    "doc": init_doc_agent,
    "ctx": init_ctx_agent,
    "inh": init_inh_agent,
    "security": init_security_agent,
}

agent_fin_fns: AGENT_FIN_FNS = {
    "doc": fin_doc_agent,
    "ctx": fin_ctx_agent,
    "inh": fin_inh_agent,
    "security": fin_security_agent,
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~ Main Function with UI Creation ~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def main(agent_type: str):
    if agent_type not in agent_init_fns:
        raise ValueError(f"Unknown agent type: {agent_type}. Available types: {', '.join(agent_init_fns.keys())}")
    agent_params = await agent_init_fns[agent_type]()

    if agent_type not in agent_fin_fns:
        raise ValueError(f"Unknown agent type: {agent_type}. Available types: {', '.join(agent_fin_fns.keys())}")
    finalize_agent_params_fn = agent_fin_fns[agent_type]

    try:
        st.title(agent_params.title)

        # Initialize chat history in session state if not present
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "agent_deps" not in st.session_state:
            st.session_state.agent_deps = agent_params.deps

        # Display all messages from the conversation so far
        # Each message is either a ModelRequest or ModelResponse.
        # We iterate over their parts to decide how to display them.
        for msg in st.session_state.messages:
            if isinstance(msg, ModelRequest) or isinstance(msg, ModelResponse):
                for part in msg.parts:
                    display_message_part(part)

        # Chat input for the user
        user_input = st.chat_input("What do you want to know?")

        if user_input:
            # Display user prompt in the UI
            with st.chat_message("user"):
                st.markdown(user_input)

            # Display the assistant's partial response while streaming
            with st.chat_message("assistant"):
                # Create a placeholder for the streaming text
                message_placeholder = st.empty()
                full_response = ""
                
                # Properly consume the async generator with async for
                generator = run_agent_with_streaming(agent_params.agent, user_input)
                async for message in generator:
                    full_response += message
                    message_placeholder.markdown(full_response + "▌")
                
                # Final response without the cursor
                message_placeholder.markdown(full_response)
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
    finally:
        # Finalize agent parameters
        await finalize_agent_params_fn(agent_params)

if __name__ == "__main__":
    ## TODO: change to streamlit weidget
    agent_type = os.environ.get("AGENT_TYPE", "inh")
    asyncio.run(main(agent_type=agent_type))
