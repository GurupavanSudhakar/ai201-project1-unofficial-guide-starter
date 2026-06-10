import gradio as gr
from query import ask


def handle(question):
    result = ask(question)
    sources_str = "\n".join(result["sources"])
    return result["answer"], sources_str


with gr.Blocks(title="The Unofficial Guide — CCNY EE Professor Reviews") as demo:
    gr.Markdown("## The Unofficial Guide — CCNY EE Professor Reviews")
    question = gr.Textbox(label="Your Question", lines=2)
    btn = gr.Button("Ask")
    answer_box = gr.Textbox(label="Answer", lines=8)
    sources_box = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(fn=handle, inputs=question, outputs=[answer_box, sources_box])
    question.submit(fn=handle, inputs=question, outputs=[answer_box, sources_box])

demo.launch()
