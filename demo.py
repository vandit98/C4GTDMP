import streamlit as st
import src.st_login_form as st_login_form

from utils.translator import main
# Define session state class for page navigation
class SessionState:
    def __init__(self):
        self.page = "login"  # Default page is login

# Initialize session state
session_state = SessionState()

# Login page
if session_state.page == "login":
    st.set_page_config(
        page_title="Belongg AI Login Form",
        page_icon="🔐",
        menu_items={
            "About": f"Belongg Language Translation Login Form 🔐   "
            f"\nApp contact: [Vandit Tyagi](mail to:grindandeat786@gmail.com)",
        },
    )

    st.title("🔐 `Belong AI Language Translation Login UI`")

    st.write(
        "This app shows how you can use the `st-login-form` component to create user-login forms for belongg ai Employee only"
    )

    # Initialize the login form
    client = st_login_form.login_form(
        title="Authentication",
        user_tablename="belongg_users",
        username_col="username",
        password_col="password",
        login_title="Login to existing account :prince: ",
        login_username_label="Enter your unique username",
        login_password_label="Enter your password",
        login_submit_label="Login",
        login_success_message="Login succeeded :tada:",
        login_error_message="Wrong username/password :x: ",
    )

    st.write(
        "On authentication, `login_form()` sets `st.session_state['authenticated']` to `True`. This also collapses and disables the login form."
    )
    st.write(
        "`st.session_state['username']` is set to the provided username for a new or existing user"
    )

    # Check if the user is authenticated and redirect to the new page if so
    if st.session_state["authenticated"]:
        if st.session_state["username"]:
            st.success(f"Welcome {st.session_state['username']}")
            session_state.page = "upload" 
            main()
