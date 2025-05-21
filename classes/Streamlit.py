import json
import streamlit as st
from langchain_core.messages import HumanMessage
from classes.MySQLAgent import MySQLAgent
import os

class Streamlit:

    def __init__(self):
        self.__user_input = st.chat_input("Ask your question...")
        self.sql_agent = MySQLAgent()
        self.__agent = self.sql_agent.get_agent_instance()

    def run_streamlit(self):
        # Title
        provider = os.getenv('PROVIDER')
        st.title("🧠 SQL Agent Assistant using {provider} {model}".format(provider=provider.upper(), model=self.sql_agent.model))
        # Input
        self.init_message_history()
        self.handle_user_input()
        
    def init_message_history(self):
        # Message history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message("user" if msg.type == "human" else "assistant"):
                st.markdown(msg.content)

    def show_thinking_process(self, type, content):
        with st.expander(f"**Type**: `{type}`"):
            st.markdown(f"**Content**:\n\n{content}")

    def handle_user_input(self):
        # Submit button
        if self.__user_input:
            # Show user message
            with st.chat_message("user"):
                st.markdown(self.__user_input)
            user_msg = HumanMessage(content=self.__user_input)
            st.session_state.messages.append(user_msg)

            for step in self.__agent.stream(
                {"messages": st.session_state.messages},
                stream_mode="values",
            ):
                msg = step["messages"][-1]  # get the latest message

                # AI message with tool calls
                if msg.type == "ai" and not msg.content:
                    tool_calls = getattr(msg, "tool_calls", [])
                    if tool_calls:
                        content = ""
                        for i, call in enumerate(tool_calls, 1):
                            formatted_call = json.dumps(call, indent=2, ensure_ascii=False)
                            content += f"**Tool Call {i}:**\n```json\n{formatted_call}\n```\n"
                    else:
                        content = "_No tool call info available._"

                # Tool message → format all fields as JSON
                elif msg.type == "tool":
                    
                    tool_data = {
                        "name": msg.name,
                        "tool_call_id": msg.tool_call_id,
                        "id": msg.id,
                        "content": msg.content,
                    }
                    content = f"```json\n{json.dumps(tool_data, indent=2, ensure_ascii=False)}\n```"

                # Regular human/assistant messages
                else:
                    content = msg.content

                # Collapsible display
                self.show_thinking_process(msg.type, content)
                    
            # Show assistant message
            if msg:
                with st.chat_message("assistant"):
                    st.markdown(msg.content)
                st.session_state.messages.append(msg)