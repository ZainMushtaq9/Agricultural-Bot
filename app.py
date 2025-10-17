import streamlit as st
from groq import Groq

def main():
    """
    This function is the main entry point of the Streamlit application.
    """

    st.set_page_config(
        page_title="Zarai Dost - Agri-Chatbot",
        page_icon="🧑‍🌾",
        layout="centered"
    )

    st.title("🧑‍🌾 Zarai Dost - Your Agricultural Assistant")
    st.write("Welcome! I am an AI assistant specialized in Pakistani agriculture. Ask me about crops, soil health, weather patterns, or pest control.")

    # Initialize api_key to None
    api_key = None
    
    # Try to get the API key from Streamlit's secrets management (for cloud deployment)
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        # This will catch StreamlitSecretNotFoundError on local runs if secrets are not set.
        # It allows the app to fall back to manual input.
        st.sidebar.title("Configuration")
        api_key = st.sidebar.text_input("Enter your Groq API Key", type="password")

    # Check if the API key is provided
    if api_key:
        client = Groq(api_key=api_key)

        # Initialize chat history in session state with a system prompt and welcome message
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "system",
                    "content": "You are 'Zarai Dost', an expert AI assistant for Pakistani agriculture. Your goal is to provide helpful, accurate, and locally relevant advice to farmers and agricultural professionals in Pakistan. All your responses must be focused on agriculture. When asked a question, provide answers considering Pakistan's specific climate, soil types, common crops (like wheat, cotton, rice, sugarcane), and regional challenges. If a question is not related to agriculture, you must politely state that you can only answer agricultural questions."
                },
                {
                    "role": "assistant",
                    "content": "Hello! How can I help you with your farming questions today?"
                }
            ]

        # Display past chat messages, skipping the system message
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("Ask about crops, soil, or weather..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Display assistant's response
            with st.chat_message("assistant"):
                try:
                    # Create a streaming chat completion
                    stream = client.chat.completions.create(
                        messages=[
                            {
                                "role": m["role"],
                                "content": m["content"],
                            }
                            for m in st.session_state.messages
                        ],
                        model="llama-3.3-70b-versatile",
                        stream=True,
                    )
                    
                    # Create a generator function to yield text content from the stream
                    def response_generator(stream):
                        for chunk in stream:
                            content = chunk.choices[0].delta.content
                            if content:
                                yield content

                    # Use st.write_stream to display the generated content
                    response = st.write_stream(response_generator(stream))
                    st.session_state.messages.append({"role": "assistant", "content": response})

                except Exception as e:
                    st.error(f"An error occurred: {e}", icon="🚨")
    else:
        st.info("Please provide your Groq API key in the sidebar to start chatting.", icon="🔑")


if __name__ == "__main__":
    main()

