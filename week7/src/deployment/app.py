import streamlit as st
from router import CapstoneRouter 

# 1. Page Configuration
st.set_page_config(page_title="Enterprise AI Capstone", layout="wide")

# 2. Cache the Router so models don't reload on every button click!
@st.cache_resource
def load_backend():
    with st.spinner("Spinning up AI Pipelines... Please wait."):
        return CapstoneRouter()

router = load_backend()

# 3. Sidebar for Memory / History
# 3. Sidebar for Memory / History
with st.sidebar:
    st.header(" Conversation History")
    if st.button("Refresh History"):
        history = router.memory.get_last_n_messages(n=5)
        
        if history:
            # If it is a single giant string block
            if isinstance(history, str):
                st.text(history)
            
            # If it is a list of strings
            elif isinstance(history, list):
                for i, msg in enumerate(history):
                    st.markdown(f"**Message {i+1}:**")
                    st.text(msg)
                    st.divider()
            
            # Fallback just in case
            else:
                st.write(history)
        else:
            st.info("Memory stack is currently empty.")

# 4. Main UI Layout
st.title(" Enterprise Multimodal AI")
st.markdown("Query structured SQL data, unstructured PDFs, or Image vectors using the endpoints below.")

# User Inputs
col1, col2 = st.columns([1, 4])
with col1:
    endpoint = st.selectbox("Select Endpoint", ["/ask", "/ask-sql", "/ask-image"])
with col2:
    query = st.text_input("Enter your query:", placeholder="e.g., Show me the top 5 customers")

# Initialize session state to hold our results so buttons don't clear the screen
if "current_result" not in st.session_state:
    st.session_state.current_result = None

# 5. Process the Request
if st.button("Submit Query", type="primary"):
    if query:
        with st.spinner("Processing request and running agentic evaluation..."):
            result = router.process_query(endpoint, query)
            st.session_state.current_result = result
    else:
        st.warning("Please enter a query.")

# 6. Display Results & Gather Feedback
if st.session_state.current_result:
    res = st.session_state.current_result
    
    st.subheader("Final Answer")
    st.info(res["final_answer"])
    
    # Expandable section for Evaluation metrics
    with st.expander(" View Agentic Evaluation Details"):
        st.metric(label="Confidence Score", value=f"{res['confidence_score']}/100")
        st.markdown("**AI Critique:**")
        st.write(res["critique_text"])
        st.markdown("**Context Used:**")
        st.write(res["context_used"])
        st.markdown("**Original Draft Answer (Pre-Refinement):**")
        st.write(res["draft_answer"])
        
    st.write("---")
    st.write("**Was this answer helpful?**")
    
    # Feedback Buttons
    fb_col1, fb_col2, _ = st.columns([1, 1, 8])
    with fb_col1:
        if st.button(" Yes"):
            router.save_feedback(
                res["endpoint"], res["query"], res["final_answer"], 
                res["confidence_score"], res["critique_text"], "Positive"
            )
            st.success("Feedback saved to memory!")
            st.session_state.current_result = None # Reset for next query
            st.rerun()
            
    with fb_col2:
        if st.button(" No"):
            router.save_feedback(
                res["endpoint"], res["query"], res["final_answer"], 
                res["confidence_score"], res["critique_text"], "Negative"
            )
            st.error("Feedback saved. We will improve!")
            st.session_state.current_result = None # Reset for next query
            st.rerun()