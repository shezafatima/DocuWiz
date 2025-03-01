import streamlit as st
import google.generativeai as genai
import pdfplumber

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


def extract_text_from_pdfs(uploaded_files):
    all_text = ""
    for uploaded_file in uploaded_files:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
    return all_text

def is_question_relevant_ai(question):
    """Uses AI to determine if a question is related to documents."""
    classification_prompt = f"Is this question related to document analysis? Respond with 'Yes' or 'No' only.\n\nQuestion: {question}"
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    response = model.generate_content(classification_prompt)
    return response.text.strip().lower() == "yes"

def ask_gemini(question, pdf_text):
    """Asks Gemini only if the AI classifier confirms relevance."""
    if not is_question_relevant_ai(question):
        return "I'm only able to answer document-related questions. Please ask something relevant."

    prompt = f"Here is a study document:\n\n{pdf_text[:4000]}\n\nAnswer the question: {question}"
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def summarize_text(pdf_text):
    prompt = f"Summarize the document below into key bullet points:\n\n{pdf_text[:4000]}"
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

st.set_page_config(
    page_title=("DocuWiz"),
    page_icon=("logo.png")
)

# --- Sidebar
st.sidebar.image("logo.png", width=120)  
st.sidebar.title("Chat History")
if st.sidebar.button("Delete History🗑️"):
    st.session_state.chat_history = []
    
if st.session_state.chat_history:
    for idx, entry in enumerate(st.session_state.chat_history, start=1):
        st.sidebar.markdown(f"**{idx}. Request:** {entry['question']}")
        st.sidebar.markdown(f"**Response:** {entry['answer']}")
else:
    st.sidebar.info("No chat history yet.")

col1, col2 = st.columns([0.4, 5], gap="small")

with col1:
    st.image("logo.png", width=80) 

with col2:
    st.markdown(
        "<span style='font-size: 2rem; font-weight: bold;'>DocuWiz</span>",
        unsafe_allow_html=True
    )
st.subheader("Unleashing the magic of AI on PDFs✨")
st.write("Upload your PDFs, generate summaries, and ask AI-powered questions!🤖")

# --- Upload PDFs Section ---
st.markdown(
        "<span style='font-size: 2rem; font-weight: bold;'>Upload PDFs</span>",
        unsafe_allow_html=True
    )
uploaded_files = st.file_uploader("Select one or more PDF files", type="pdf", accept_multiple_files=True)
if uploaded_files:
    st.session_state.pdf_text = extract_text_from_pdfs(uploaded_files)
    st.success("PDF(s) processed successfully!🎉")
    with st.expander("Preview Extracted Text"):
        st.text_area("Extracted Content", st.session_state.pdf_text[:1000], height=200)

st.markdown(
        "<span style='font-size: 2rem; font-weight: bold;'>Generate Summary</span>",
        unsafe_allow_html=True
    )
if st.session_state.pdf_text:
    if st.button("Generate Summary"):
        with st.spinner("Generating summary..."):
            st.session_state.summary = summarize_text(st.session_state.pdf_text)
        st.subheader("Summary")
        st.write(st.session_state.summary)
    if st.session_state.summary:
        st.download_button(
            label="Download Summary⬇️",
            data=st.session_state.summary,
            file_name="summary.txt",
            mime="text/plain"
        )
else:
    st.info("Please upload a PDF first. 🗎")

st.markdown(
        "<span style='font-size: 2rem; font-weight: bold;'>Ask a Question</span>",
        unsafe_allow_html=True
    )
if st.session_state.pdf_text:
    with st.form(key="question_form"):
        user_question = st.text_input("Enter your question here:")
        submit_button = st.form_submit_button("Submit Question")
    if submit_button:
        if user_question.strip():
            with st.spinner("Generating response..."):
                answer = ask_gemini(user_question, st.session_state.pdf_text)
            st.subheader("AI Answer")
            st.write(answer)
            # Append Q&A to chat history
            st.session_state.chat_history.append({
                "question": user_question,
                "answer": answer
            })
        else:
            st.warning("Please type in a question.")
else:
    st.info("Please upload a PDF to begin asking questions. 🗎")
