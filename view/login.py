from datetime import datetime
import time
import uuid

import gradio as gr

from data import check_email_exists, get_user_info, add_user, get_new_question_id
from utils import is_valid_email


ACCEPT_PHONE_NUMBER = False


info_text = """
## Experiment
### Introduction
This is an experiment to annotate harmful or copyrighted content generated from
large-scale image generation models. This experiment is conducted by SIML lab
at Graduate School of AI, KAIST (POC: Sanghyun Kim) and the purpose of this
is to collect human feedback on the harmfulness of generated images and to 
use them to improve the safety of AI models. The experiment will take about 10-20
minutes to complete. You will be asked to perform a series of tasks
to answer the harmfulness or the similarlity of images. 

### By participating in this experiment, you agree to the following:
- You are at least 18 years old.
- You are participating voluntarily.
- You understand that you may stop at any time.
- You understand that you will not be compensated for your participation.
- You understand that you may contact the researcher at any time at [nannullna@kaist.ac.kr].

### Privacy policy
- You understand that your data will be used for research purposes only.
- You understand that your data will be anonymized.
- You understand that your responses will be recorded.

### More information
- Do NOT refresh the page or close the browser window during the experiment. This page is highly unstable and may crash. 
- Some of the images may contain sexual, harmful, or violent content. If you are not comfortable with this, please do not participate in this experiment.
- This experiment page works best on **a desktop or laptop computer**. Please do NOT use a mobile device.
"""

info_text_kr = """
## 실험
### 소개
이 실험은 대규모 이미지 생성 모델에서 생성된 유해한 이미지를 주석으로 달아주는 실험입니다.
본 실험은 한국과학기술원 AI대학원 SIML 연구실 (담당자: 김상현)에서 진행되며,
대규모 이미지 생성 모델에서 생성된 이미지의 유해성을 평가하기 위한 인간의 피드백을 수집하고,
이를 통해 AI 모델의 안전성을 향상시키는 것을 목적으로 합니다.
본 실험은 약 10-20분 정도 소요됩니다. 참여자분들께서는 이미지의 유해성 또는 유사성을 평가하는 일련의 작업을 수행하게 됩니다.

### 본 실험에 참여함으로써 다음 사항에 동의합니다:
- 본인은 18세 이상임을 확인합니다.
- 본인은 자발적으로 참여합니다.
- 본인은 언제든지 실험을 중단할 수 있음을 이해합니다.
- 본인은 참여에 대한 보상을 받지 않을 것을 이해합니다.
- 본인은 실험 참여에 대한 문의를 언제든지 [nannullna@kaist.ac.kr]로 할 수 있음을 이해합니다.

### 개인정보 처리방침
- 본 실험에서 수집된 데이터는 연구 목적으로만 사용됩니다.
- 본 실험에서 수집된 데이터는 익명화됩니다.
- 본 실험에서 수집된 데이터는 기록됩니다.

### 추가 정보
- 실험 도중 페이지를 새로고침하거나 브라우저 창을 닫지 마세요. 이 페이지는 매우 불안정하며, 오류가 발생할 수 있습니다.
- 일부 이미지에는 성적, 유해, 폭력적인 내용이 포함될 수 있습니다. 이에 불편하신 분은 참여하지 말아주세요.
- 본 실험은 **데스크탑 또는 랩탑 컴퓨터**에서 가장 잘 작동합니다. 모바일 기기에서는 사용하지 마세요.
"""


def create_login_view(user_state_var: gr.State):

    login_view = gr.Blocks()

    with login_view:
        with gr.Row() as row:
            with gr.Column(scale=2):
                with gr.Tab("English"):
                    gr.Markdown(info_text)
                with gr.Tab("한국어"):
                    gr.Markdown(info_text_kr)

            login_column = gr.Column(scale=1)
            with login_column:
                email = gr.Textbox(label="Email (이메일)")
                age = gr.Dropdown(label="Age (나이)", choices=["18-24", "25-34", "35-44", "45-54", "55-64", "65+"])
                sex = gr.Radio(choices=["Male (남성)", "Female (여성)", "Others (기타)", "Not disclose (밝히지 않음)"], label="Sex (성별)")
                agree = gr.Checkbox(label="I agree to participate in this experiment. 본인은 본 실험에 참여함으로써 다음 사항에 동의합니다.")

                lang = gr.Radio(choices=["English", "한국어"], label="Language (언어)", value="English")
                
                if ACCEPT_PHONE_NUMBER:
                    gr.Markdown("If you provide your phone number, we will randomly select 10 participants to receive a gift card worth 10,000 KRW. (휴대폰 번호를 제공하시면, 10명의 참여자 중 10,000원 상당의 상품권을 드립니다.)")
                phone = gr.Textbox(label="(Optional) Phone number (휴대번호, 선택사항)", visible=ACCEPT_PHONE_NUMBER)
                
                error_txt = gr.Markdown("Error message to be shown.", visible=False, label="Error", elem_classes=["warning"])
                start_btn = gr.Button("Start Experiment - 실험 시작")


    def submit_user_info(email, age, sex, lang, phone, agree, user_state):
        if not is_valid_email(email):
            return {error_txt: gr.update(value="Please enter a valid email address.\n올바른 이메일 주소를 입력해주세요.", visible=True)}
        if not age:
            return {error_txt: gr.update(value="Please select your age.\n나이를 선택해주세요.", visible=True)}
        if not sex:
            return {error_txt: gr.update(value="Please select your sex.\n성별을 선택해주세요.", visible=True)}
        if not agree:
            return {error_txt: gr.update(value="Please agree to participate in this experiment.\n참가를 원하시면 동의해주세요.", visible=True)}

        if not check_email_exists(email):
            print("Creating new user.")
            uuid_ = str(uuid.uuid4())
            datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
            # TODO: question logic
            question_id = get_new_question_id(uuid_)

            user_state['uuid'] = uuid_
            user_state['email'] = email
            user_state['age'] = age
            user_state['sex'] = sex
            user_state['phone'] = phone
            user_state['agreed'] = agree
            user_state['datetime'] = datetime_str
            user_state['question_id'] = question_id

            user_state['use_kr'] = lang == "한국어"

            add_user(uuid_, email, age, sex, phone, agree, datetime_str, question_id)

        else:
            print("User already exists.")
            user_info = get_user_info(email)
            user_state['uuid'] = user_info[0]
            user_state['email'] = user_info[1]
            user_state['age'] = user_info[2]
            user_state['sex'] = user_info[3]
            user_state['phone'] = user_info[4]
            user_state['agreed'] = user_info[5]
            user_state['datetime'] = user_info[6]
            user_state['question_id'] = user_info[7]

            user_state['use_kr'] = lang == "한국어"

        print(user_state)

        return {
            start_btn: gr.update(interactive=False),
            error_txt: gr.update(value="### Please continue to the **Question tab**\nlocated on the top of the page.\n**Question** 탭을 눌러주세요.", visible=True),
        }
    

    start_btn.click(
        submit_user_info, 
        [email, age, sex, lang, phone, agree, user_state_var], 
        [start_btn, error_txt]
    )

    def update_view(user_state):
        return {
            login_column: gr.update(visible=user_state['question_id'] == ""),
            error_txt: gr.update(visible=False),
        }

    login_view.load(update_view, [user_state_var], [login_column, error_txt])
    
    return login_view
