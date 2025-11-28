"""
Main Gradio application for the Agentic Research Assistant.
"""

import gradio as gr
from src.logging import logger, log_buffer
from src.ui import (
    chat,
    handle_pdf_upload,
    analyze_uploaded_pdf,
    explain_pdf,
    post_from_pdf,
    get_logs,
    clear_logs,
    refresh_logs,
    change_log_level,
)
from src.tools import (
    retrieve_related_papers,
    explain_research_paper,
    write_social_media_post,
    process_uploaded_pdf,
)


def create_app():
    """Create and configure the Gradio application."""
    with gr.Blocks(title="Agentic Research Assistant with Logging") as demo:
        gr.Markdown("# 🤖 Agentic Research Assistant")
        gr.Markdown("AI-powered research assistant using Gemini API with **comprehensive LLM thinking process logging**")

        with gr.Tabs():
            # Chat Tab
            with gr.Tab("💬 Chat"):
                gr.Markdown("""
                ### 💬 Multimodal Research Assistant
                Upload PDFs, images, or any files directly in the chat! The AI can:
                - 📄 Read and analyze PDF research papers
                - 🖼️ Analyze images and figures
                - 🔍 Search for papers on arXiv
                - 📝 Explain research in simple terms
                - 📱 Create social media posts
                """)
                gr.ChatInterface(
                    fn=chat,
                    title="Research Assistant Chat",
                    description="Type a message or attach files (PDFs, images, etc.). The AI will analyze them directly!",
                    multimodal=True,
                )

            # PDF Upload Tab
            with gr.Tab("📄 Upload PDF"):
                gr.Markdown("### Upload and Analyze Research Papers")
                gr.Markdown("Upload a PDF file of a research paper and get an AI-powered analysis, explanation, or social media post.")

                with gr.Row():
                    with gr.Column():
                        pdf_upload = gr.File(
                            label="📎 Upload PDF File",
                            file_types=[".pdf"],
                            type="filepath"
                        )
                        upload_status = gr.Textbox(
                            label="Status",
                            lines=10,
                            interactive=False
                        )

                    with gr.Column():
                        pdf_path_store = gr.Textbox(
                            label="Uploaded PDF Path",
                            visible=False
                        )
                        analyze_btn = gr.Button("🔍 Analyze PDF", variant="primary", size="lg")
                        explain_btn = gr.Button("📝 Get Detailed Explanation", variant="secondary")
                        post_btn = gr.Button("📱 Create Social Media Post", variant="secondary")

                pdf_output = gr.Textbox(
                    label="📋 Analysis Result",
                    lines=20,
                    interactive=False
                )

                # Event handlers
                pdf_upload.change(
                    fn=handle_pdf_upload,
                    inputs=[pdf_upload],
                    outputs=[upload_status, pdf_path_store]
                )

                analyze_btn.click(
                    fn=analyze_uploaded_pdf,
                    inputs=[pdf_path_store],
                    outputs=[pdf_output]
                )

                explain_btn.click(
                    fn=explain_pdf,
                    inputs=[pdf_path_store],
                    outputs=[pdf_output]
                )

                post_btn.click(
                    fn=post_from_pdf,
                    inputs=[pdf_path_store],
                    outputs=[pdf_output]
                )

            # Logs Tab
            with gr.Tab("📊 LLM Thinking Process Logs"):
                gr.Markdown("### View the LLM's Thinking Process")
                gr.Markdown("See detailed logs of all LLM API calls, tool executions, and the agentic decision-making process. Click 'Refresh Logs' to update.")

                with gr.Row():
                    with gr.Column(scale=3):
                        log_level_dropdown = gr.Dropdown(
                            choices=["ALL", "DEBUG", "INFO", "WARNING", "ERROR"],
                            value="INFO",
                            label="🎚️ Log Level Filter",
                            info="Filter logs by severity level"
                        )
                    with gr.Column(scale=1):
                        refresh_btn = gr.Button("🔄 Refresh Logs", variant="secondary")
                        clear_btn = gr.Button("🗑️ Clear Logs", variant="stop")

                log_output = gr.Textbox(
                    label="📋 Log Output",
                    lines=25,
                    max_lines=50,
                    value=log_buffer.format_logs("INFO"),
                    interactive=False
                )

                status_text = gr.Textbox(label="Status", visible=False)

                # Event handlers
                refresh_btn.click(
                    fn=refresh_logs,
                    inputs=[log_level_dropdown],
                    outputs=[log_output]
                )

                clear_btn.click(
                    fn=clear_logs,
                    outputs=[status_text]
                ).then(
                    fn=refresh_logs,
                    inputs=[log_level_dropdown],
                    outputs=[log_output]
                )

                log_level_dropdown.change(
                    fn=refresh_logs,
                    inputs=[log_level_dropdown],
                    outputs=[log_output]
                )

            # Settings Tab
            with gr.Tab("⚙️ Settings"):
                gr.Markdown("### Logging Configuration")
                gr.Markdown("Control the verbosity of logging for the LLM system.")

                with gr.Row():
                    log_level_radio = gr.Radio(
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        value="INFO",
                        label="🎚️ Global Log Level",
                        info="DEBUG = All details | INFO = Key events | WARNING = Issues only | ERROR = Errors only"
                    )

                change_level_btn = gr.Button("💾 Apply Log Level", variant="primary")
                level_status = gr.Textbox(label="Status", interactive=False)

                change_level_btn.click(
                    fn=change_log_level,
                    inputs=[log_level_radio],
                    outputs=[level_status]
                )

                gr.Markdown("---")
                gr.Markdown("### Log Legend")
                gr.Markdown("""
                **Emoji Guide:**
                - 💬 User message received
                - 📤 LLM request sent
                - 📥 LLM response received
                - 🛠️ Tool call requested by LLM
                - ⚙️ Tool executing
                - ✅ Operation completed successfully
                - 🔄 Agentic loop iteration
                - 💭 Final response generation
                - ❌ Error occurred
                - ⚠️ Warning or fallback
                - 🔍 Function called
                - 📚 Data retrieved
                """)

        # Register API endpoints
        gr.api(retrieve_related_papers, api_name="retrieve_papers")
        gr.api(explain_research_paper, api_name="explain_paper")
        gr.api(write_social_media_post, api_name="write_social_post")
        gr.api(process_uploaded_pdf, api_name="process_pdf")

    return demo


def launch_app():
    """Launch the Gradio application."""
    logger.info("🚀 Starting Agentic Research Assistant with Logging...")
    demo = create_app()
    demo.launch(mcp_server=True, share=True)
