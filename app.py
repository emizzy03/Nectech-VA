from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import os
from src.schemas.user_account import Create_Account
from src.schemas.manager_info import select_manager, train_model, assign_manager, load_account_managers_info
from src.services.agent import ask_assistant

load_dotenv()
# Path to the CSV file
CSV_FILE_PATH = "user_accounts.csv"
ACCOUNT_MANAGERS_FILE_PATH = "account_managers_info.csv"

if not os.path.exists(CSV_FILE_PATH):
    df = pd.DataFrame(columns=["Name", "Email", "Company Address", "Phone", "Assigned To"])
    df.to_csv(CSV_FILE_PATH, index=False)

# Train the model and get the list of managers
model, managers = train_model(ACCOUNT_MANAGERS_FILE_PATH)

logo_html = """
    <div style="background-color:#f1f1f1;padding:10px;border-radius:10px">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/CDW_Logo.svg/2560px-CDW_Logo.svg.png" alt="Logo" style="height:50px;">
    </div>
"""

st.markdown(logo_html, unsafe_allow_html=True)

st.title("NECTECH AI Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initial assistant message and form display
if not st.session_state.messages:
    initial_prompt="You are to welcome the user and tell them to fill out the form below"
    initial_response = ask_assistant(initial_prompt)
    st.session_state.messages.append({"role": "assistant", "content": initial_response})
    st.session_state.show_form = True

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to display the user details form
def user_details_form():
    """
    Display a form to collect user details and save them to a CSV file.
    """
    if "show_form" not in st.session_state:
        st.session_state.show_form = False

    if st.session_state.show_form:
        with st.form(key="user_details_form"):
            name = st.text_input(label="Name", key="name")
            email = st.text_input(label="Email", key="email")
            company_address = st.text_input(label="Company Address", key="company_address")
            phone = st.text_input(label="Phone", key="phone")
            submit_button = st.form_submit_button(label="Submit")

            if submit_button:
                if all([name, email, company_address, phone]):
                    user_details = Create_Account(
                        name=name,
                        email=email,
                        CompanyAddress=company_address,
                        phone=int(phone)
                    )
                    st.success("User details submitted successfully.")
                    st.session_state.user_details = user_details
                    st.session_state.show_form = False

                    assigned_manager = select_manager(managers, model).name
                    assign_manager(ACCOUNT_MANAGERS_FILE_PATH, assigned_manager)

                    # Save user details to CSV
                    df = pd.read_csv(CSV_FILE_PATH)
                    df.loc[len(df)] = [name, email, company_address, phone, assigned_manager]
                    df.to_csv(CSV_FILE_PATH, index=False)

                    st.session_state.confirmation_message = (
                        "Thank you for filling out the form and successfully creating an account."
                    )

                    return user_details
    return None



# Display the form if the state is set
if st.session_state.get("show_form"):
    user_details_form()

# React to user input
if prompt := st.chat_input("What is up?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if "create a new account" in prompt.lower():
        st.session_state.show_form = True
    else:
        response = ask_assistant(prompt)
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Display the confirmation message if available
if "confirmation_message" in st.session_state:
    thank_prompt = ask_assistant(st.session_state.confirmation_message)
    st.chat_message("assistant").markdown(thank_prompt)
    st.session_state.messages.append({"role": "assistant", "content": thank_prompt})
    del st.session_state.confirmation_message
