import re
import gradio as gr


# Check if the given string is a valid email address
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def show_component():
    return gr.update(visible=True)

def hide_component():
    return gr.update(visible=False)
