import os
from glob import glob
import random
import time
from datetime import datetime

import numpy as np
import pandas as pd
from PIL import Image

import gradio as gr

from view.login import create_login_view
from view.question import create_question_parent_view


SHOW_LOGO = True
USE_KR = False

CSS = """.warning {
    color: red;
    font-weight: bold;
    font-size: 1.5em;
    !important;
}
"""


with gr.Blocks(css=CSS, theme=gr.themes.Default(text_size=gr.themes.sizes.text_lg)) as demo:

    user_state_var = gr.State(value={
        "uuid": "",
        "agreed": False,
        "email": "",
        "age": "",
        "sex": "",
        "phone": "",
        "datetime": "",
        "question_id": "",
        "questions": [],
        "progress": -1, # -1: not started, 0: started, len(questions): ended
        "use_kr": USE_KR,
    })

    if SHOW_LOGO:
        title_txt = "# SIML\nGraduate School of AI, KAIST"
        title_txt_kr = "# SIML\n한국과학기술원 AI대학원"
        title = gr.Markdown(title_txt_kr if USE_KR else title_txt)

    with gr.Tab("Login") as login_tab:
        login_view = create_login_view(user_state_var)

    with gr.Tab("Question") as question_tab:    
        question_id_txt = gr.Markdown("Question ID: N/A")
        question_tab.select(
            lambda user_state: f"Question ID: {user_state['question_id']}" if user_state['question_id'] else "Question ID: N/A", 
            [user_state_var], [question_id_txt]
        )
        question_parent_view = create_question_parent_view(user_state_var, question_tab)
    
    with gr.Tab("Help") as help_tab:
        help_view = gr.Blocks()
        with help_view:
            gr.Markdown("# Help text")

demo.launch(share=False)


