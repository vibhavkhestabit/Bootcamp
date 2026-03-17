import streamlit as st
from router import LocalLLMRouter

st.set_page_config(page_title="Local LLM Interface", layout="wide")

# 1. Cache the Router so the GGUF model stays in RAM between button clicks!
@st.cache_resource
def load_backend():
    return LocalLLMRouter()

router = load_backend()

st.title("⚡ Local Open-Source LLM UI")

# --- Sidebar: Generation Parameters ---
with st.sidebar:
    st.header(" Model Parameters")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.number_input("Max Tokens", min_value=10, max_value=2048, value=512)
    top_p = st.slider("Top P", 0.1, 1.0, 0.95, 0.05)
    top_k = st.number_input("Top K", min_value=1, max_value=100, value=40)
    stream = st.toggle("Enable Streaming", value=True)

# --- Setup Tabs ---
tab1, tab2 = st.tabs([" Chat Mode", " Instruct Generate"])

# TAB 1: CHAT INTERFACE
with tab1:
    st.markdown("### Conversational AI")
    
    # Initialize UI chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Message the local AI..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Call the router directly (no API requests needed!)
                response_data = router.chat(
                    ui_messages=st.session_state.messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    stream=stream
                )
                
                if stream:
                    # Streamlit magically handles the generator!
                    full_response = st.write_stream(response_data)
                else:
                    st.markdown(response_data)
                    full_response = response_data
                
                # Save the AI's response to the session state
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Inference Error: {str(e)}")


# TAB 2: RAW GENERATION
with tab2:
    st.markdown("### Raw Prompt Completion")
    
    raw_prompt = st.text_area("Enter your prompt:", height=150, placeholder="Write a Python script to...")
    
    if st.button("Generate Text", type="primary"):
        if not raw_prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            st.markdown("**Output:**")
            try:
                # Call the router directly
                response_data = router.generate(
                    prompt=raw_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    stream=stream
                )
                
                if stream:
                    st.write_stream(response_data)
                else:
                    st.info(response_data)
                    
            except Exception as e:
                st.error(f"Inference Error: {str(e)}")