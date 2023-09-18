import gradio as gr

from data import get_questions, submit_response


ALLOW_PREVIOUS = False
REF_ALWAYS_OPEN = False
DEBUG = False


def create_question_parent_view(user_state_var: gr.State, question_tab: gr.Tab):

    parent_view = gr.Blocks()

    with parent_view:

        with gr.Row():
            prev_btn = gr.ClearButton(value="Previous", size="sm")
            next_btn = gr.ClearButton(value="Next", size="sm")

        with gr.Column() as question_column:

            instruction_md = gr.Markdown("")
            question_type_md = gr.Markdown("", visible=DEBUG)

            accordion = gr.Accordion(label="Reference images")
            with accordion:
                ref_gallery = gr.Gallery(label="See the following images for your reference.", value=[], columns=5, height=300, show_download_button=False)

            img_view = gr.Image(value=None, label="Answer to the following image", visible=False, width=400, height=400, show_download_button=False)
            gallery_view = gr.Gallery(value=[], columns=5, label="Answer to the following images", visible=False, show_download_button=False, height=480)
        
        with gr.Column() as response_column:
            response_msg = gr.Markdown("", visible=False, elem_classes=["warning"])
            response_rank = gr.Row(variant="compact")
            with response_rank:
                dropdowns = []
                for i in range(5):
                    d = gr.Radio(label=f"Image {i+1}", choices=["1", "2", "3", "4", "5", "X"])
                    dropdowns.append(d)
                    prev_btn.add(d)
                    next_btn.add(d)
            checkboxes = gr.CheckboxGroup(label="Labels", choices=[], visible=True, interactive=True)
            prev_btn.add(checkboxes)
            next_btn.add(checkboxes)
            
    def update_view(user_state):

        questions = user_state['questions']
        question_id = user_state['question_id']
        progress = user_state['progress']
        use_kr = user_state['use_kr']
        
        prev_btn_txt = "이전" if use_kr else "Previous"
        next_btn_txt = "다음" if use_kr else "Next"

        if question_id and len(questions) == 0:
            user_state['questions'] = get_questions(question_id)
            questions = user_state['questions']

        question_type = "none" # ["none", "start", "binary", "rank", "end"]
        if progress == -1 and len(questions) == 0:
            question_type = "none"
        elif progress == -1 and len(questions) > 0:
            question_type = "start"
        elif len(questions) > 0 and progress < len(questions):
            question_type = questions[progress]['type'] # ["binary", "rank"]
        elif len(questions) > 0 and progress >= len(questions):
            question_type = "end"

        print(question_type, progress, len(questions))

        if question_type == "end":
            end_txt = "## Thank you for participating in this experiment.\nYou may close the window."
            end_txt_kr = "## 이번 실험에 참여해주셔서 감사합니다.\n창을 닫으셔도 좋습니다."
            return {
                prev_btn: gr.update(value=prev_btn_txt, interactive=False),
                next_btn: gr.update(value=next_btn_txt, interactive=False),
                instruction_md: gr.update(value=end_txt_kr if use_kr else end_txt, visible=True),
                question_type_md: gr.update(value=f"Question type: {question_type}"),
                accordion: gr.update(open=False, visible=False),
                ref_gallery: gr.update(value=[], visible=False),
                img_view: gr.update(value=None, visible=False),
                gallery_view: gr.update(value=[], visible=False),
                response_rank: gr.update(visible=False),
                checkboxes: gr.update(choices=[], visible=False),
            }
        elif question_type == "binary":
            current_question = questions[progress]
            return {
                prev_btn: gr.update(value=prev_btn_txt, interactive=ALLOW_PREVIOUS),
                next_btn: gr.update(value=next_btn_txt, interactive=True),
                instruction_md: gr.update(value=current_question['text_kr'] \
                    if use_kr and 'text_kr' in current_question \
                    else current_question['text'], visible=True),
                question_type_md: gr.update(value=f"Question type: {question_type}"),
                accordion: gr.update(open=False, visible=False),
                ref_gallery: gr.update(value=[], visible=False),
                img_view: gr.update(value=current_question['images'][0], visible=True),
                gallery_view: gr.update(value=None, visible=False),
                response_rank: gr.update(visible=False),
                checkboxes: gr.update(choices=current_question['labels'], visible=True),
            }
        elif question_type == "rank":
            current_question = questions[progress]
            return {
                prev_btn: gr.update(value=prev_btn_txt, interactive=ALLOW_PREVIOUS),
                next_btn: gr.update(value=next_btn_txt, interactive=True),
                instruction_md: gr.update(value=current_question['text_kr'] \
                    if use_kr and 'text_kr' in current_question \
                    else current_question['text'], visible=True),
                question_type_md: gr.update(value=f"Question type: {question_type}"),
                accordion: gr.update(open=True, visible=(
                    REF_ALWAYS_OPEN if 'references' in current_question else False
                )),
                ref_gallery: gr.update(value=current_question['references'], visible=True) \
                    if 'references' in current_question \
                    else gr.update(value=[], visible=False),
                img_view: gr.update(value=None, visible=False),
                gallery_view: gr.update(value=current_question['images'], visible=True),
                response_rank: gr.update(visible=True),
                checkboxes: gr.update(choices=current_question['labels'], visible=True) \
                    if 'labels' in current_question \
                    else gr.update(choices=[], visible=False),
            }
        elif question_type == "start":
            start_txt = "## Start\nPlease move on to the questions by clicking the **<Next>** button on the top."
            start_txt_kr = "## 시작\n위의 **<다음>** 버튼을 눌러 질문에 답해주세요."
            return {
                prev_btn: gr.update(value=prev_btn_txt, interactive=False),
                next_btn: gr.update(value=next_btn_txt, interactive=True),
                instruction_md: gr.update(value=start_txt_kr if use_kr else start_txt, visible=True),
                question_type_md: gr.update(value=f"Question type: {question_type}"),
                accordion: gr.update(open=False, visible=False),
                ref_gallery: gr.update(value=[], visible=False),
                img_view: gr.update(value=None, visible=False),
                gallery_view: gr.update(value=[], visible=False),
                response_rank: gr.update(visible=False),
                checkboxes: gr.update(choices=[], visible=False),
            }
        elif question_type == "none":
            return {
                prev_btn: gr.update(value=prev_btn_txt, interactive=False),
                next_btn: gr.update(value=next_btn_txt, interactive=False),
                instruction_md: gr.update(value="## Please login first at the login tab.", visible=True),
                question_type_md: gr.update(value=f"Question type: {question_type}"),
                accordion: gr.update(open=False, visible=False),
                ref_gallery: gr.update(value=[], visible=False),
                img_view: gr.update(value=None, visible=False),
                gallery_view: gr.update(value=[], visible=False),
                response_rank: gr.update(visible=False),
                checkboxes: gr.update(choices=[], visible=False),
            }
        
    def check_inputs_and_progress(user_state, binary_responses, *rank_responses):
        num_questions = len(user_state['questions'])
        current_progress = user_state['progress']

        user_state['progress'] += 1
        if user_state['progress'] >= num_questions:
            user_state['progress'] = num_questions

        # Check if rank_responses have no duplicates
        if len(rank_responses) > 0:
            all_responses = []
            for r in rank_responses:
                if r is not None:
                    if r in all_responses:
                        user_state['progress'] -= 1
                        return user_state, gr.update(value="## Ties not allowed. Please select **different rank values**.", visible=True)
                    elif r != "X":
                        all_responses.append(r)

        submit_response(
            user_state['uuid'], user_state['question_id'], user_state['progress'], binary_responses, *rank_responses
        )
        return user_state, gr.update(value="", visible=False)

    def go_previous(user_state):
        user_state['progress'] -= 1
        if user_state['progress'] < -1:
            user_state['progress'] = -1
        # submit_response()
        return user_state

    parent_view.load(
        update_view, 
        [user_state_var], 
        [prev_btn, next_btn, instruction_md, question_type_md, accordion, ref_gallery, img_view, gallery_view, response_rank, checkboxes]
    )

    question_tab.select(
        update_view, 
        [user_state_var], 
        [prev_btn, next_btn, instruction_md, question_type_md, accordion, ref_gallery, img_view, gallery_view, response_rank, checkboxes]
    )

    next_btn.click(
        check_inputs_and_progress, 
        [user_state_var, checkboxes, *dropdowns],
        [user_state_var, response_msg]
    ).then(
        update_view,
        [user_state_var], 
        [prev_btn, next_btn, instruction_md, question_type_md, accordion, ref_gallery, img_view, gallery_view, response_rank, checkboxes]
    )

    prev_btn.click(
        go_previous, 
        [user_state_var],
        [user_state_var]
    ).then(
        update_view,
        [user_state_var], 
        [prev_btn, next_btn, instruction_md, question_type_md, accordion, ref_gallery, img_view, gallery_view, response_rank, checkboxes]
    )

    return parent_view



    