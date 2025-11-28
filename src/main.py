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
    generate_infographic_from_text,
    generate_infographic_from_pdf,
    verify_text_input,
    verify_pdf_input,
    quick_verify_text_references,
    quick_verify_text_claims,
    recommend_from_text,
    recommend_from_pdf,
    quick_recommend_by_id,
)
from src.tools import (
    retrieve_related_papers,
    explain_research_paper,
    write_social_media_post,
    process_uploaded_pdf,
    generate_paper_infographic,
    verify_document_sources,
    recommend_similar_papers,
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

            # Infographic Generator Tab
            with gr.Tab("🎨 Generate Infographic"):
                gr.Markdown("### Paper-to-Infographic Generator")
                gr.Markdown("Transform research papers into beautiful, shareable infographics! Perfect for social media and presentations.")

                with gr.Tabs():
                    # Tab for text input
                    with gr.Tab("📝 From Text"):
                        gr.Markdown("Paste your paper text or summary below:")
                        infographic_text_input = gr.Textbox(
                            label="📄 Paper Text or Summary",
                            placeholder="Paste the research paper text or a detailed summary here...",
                            lines=10,
                            max_lines=20
                        )
                        generate_text_btn = gr.Button("🎨 Generate Infographic", variant="primary", size="lg")

                        with gr.Row():
                            with gr.Column():
                                infographic_text_status = gr.Textbox(
                                    label="📋 Status",
                                    lines=8,
                                    interactive=False
                                )
                            with gr.Column():
                                infographic_text_image = gr.Image(
                                    label="🖼️ Generated Infographic",
                                    type="filepath",
                                    interactive=False
                                )

                        generate_text_btn.click(
                            fn=generate_infographic_from_text,
                            inputs=[infographic_text_input],
                            outputs=[infographic_text_status, infographic_text_image]
                        )

                    # Tab for PDF input
                    with gr.Tab("📄 From PDF"):
                        gr.Markdown("Use the PDF you uploaded in the 'Upload PDF' tab:")
                        pdf_path_display = gr.Textbox(
                            label="Current PDF",
                            placeholder="Upload a PDF in the 'Upload PDF' tab first",
                            interactive=False
                        )
                        generate_pdf_btn = gr.Button("🎨 Generate Infographic from PDF", variant="primary", size="lg")

                        with gr.Row():
                            with gr.Column():
                                infographic_pdf_status = gr.Textbox(
                                    label="📋 Status",
                                    lines=8,
                                    interactive=False
                                )
                            with gr.Column():
                                infographic_pdf_image = gr.Image(
                                    label="🖼️ Generated Infographic",
                                    type="filepath",
                                    interactive=False
                                )

                        # Update display when PDF is uploaded in the other tab
                        pdf_path_store.change(
                            fn=lambda x: x,
                            inputs=[pdf_path_store],
                            outputs=[pdf_path_display]
                        )

                        generate_pdf_btn.click(
                            fn=generate_infographic_from_pdf,
                            inputs=[pdf_path_store],
                            outputs=[infographic_pdf_status, infographic_pdf_image]
                        )

                gr.Markdown("---")
                gr.Markdown("""
                **💡 Tips:**
                - Infographics are saved in the `generated_infographics/` folder
                - Perfect for sharing on LinkedIn, Twitter, and Instagram
                - Use the download button (⬇️) to save the image
                - Works best with concise paper summaries (500-2000 words)
                """)

            # Source Verification Tab
            with gr.Tab("🔍 Verify Sources"):
                gr.Markdown("### Advanced Source Verification")
                gr.Markdown("""
                Rigorously fact-check your research documents! This tool:
                - ✅ Validates references against Semantic Scholar and CrossRef
                - 🔍 Detects hallucinated citations and metadata mismatches
                - 📊 Extracts and verifies key claims against external evidence
                - ⚠️ Identifies unsupported or contradicted claims
                """)

                with gr.Tabs():
                    # Tab for text input
                    with gr.Tab("📝 From Text"):
                        gr.Markdown("Paste your document text below:")
                        verify_text_area = gr.Textbox(
                            label="📄 Document Text",
                            placeholder="Paste the research document text here (including references section)...",
                            lines=10,
                            max_lines=20
                        )

                        with gr.Row():
                            verify_refs_check = gr.Checkbox(
                                label="Verify References & Citations",
                                value=True,
                                info="Validate DOIs, check metadata against databases"
                            )
                            verify_claims_check = gr.Checkbox(
                                label="Verify Claims",
                                value=True,
                                info="Extract and fact-check verifiable claims"
                            )

                        verify_text_btn = gr.Button("🔍 Run Verification", variant="primary", size="lg")

                        verification_text_report = gr.Textbox(
                            label="📋 Verification Report",
                            lines=30,
                            max_lines=50,
                            interactive=False
                        )

                        verify_text_btn.click(
                            fn=verify_text_input,
                            inputs=[verify_text_area, verify_refs_check, verify_claims_check],
                            outputs=[verification_text_report]
                        )

                    # Tab for PDF input
                    with gr.Tab("📄 From PDF"):
                        gr.Markdown("Use the PDF you uploaded in the 'Upload PDF' tab:")
                        verify_pdf_path_display = gr.Textbox(
                            label="Current PDF",
                            placeholder="Upload a PDF in the 'Upload PDF' tab first",
                            interactive=False
                        )

                        with gr.Row():
                            verify_pdf_refs_check = gr.Checkbox(
                                label="Verify References & Citations",
                                value=True,
                                info="Validate DOIs, check metadata against databases"
                            )
                            verify_pdf_claims_check = gr.Checkbox(
                                label="Verify Claims",
                                value=True,
                                info="Extract and fact-check verifiable claims"
                            )

                        verify_pdf_btn = gr.Button("🔍 Run Verification on PDF", variant="primary", size="lg")

                        verification_pdf_report = gr.Textbox(
                            label="📋 Verification Report",
                            lines=30,
                            max_lines=50,
                            interactive=False
                        )

                        # Update display when PDF is uploaded
                        pdf_path_store.change(
                            fn=lambda x: x,
                            inputs=[pdf_path_store],
                            outputs=[verify_pdf_path_display]
                        )

                        verify_pdf_btn.click(
                            fn=verify_pdf_input,
                            inputs=[pdf_path_store, verify_pdf_refs_check, verify_pdf_claims_check],
                            outputs=[verification_pdf_report]
                        )

                gr.Markdown("---")
                gr.Markdown("""
                **🔍 What Gets Verified:**

                **References:**
                - DOI validation against Semantic Scholar & CrossRef
                - Author/title/year metadata accuracy
                - URL accessibility checks
                - Detection of non-existent citations

                **Claims:**
                - Extraction of verifiable scientific claims
                - Evidence gathering from research databases
                - AI-powered fact-checking with confidence scores
                - Detection of unsupported or contradicted claims

                **⏱️ Processing Time:**
                - Typical document: 2-5 minutes
                - Large documents with many references: 5-10 minutes
                - Rate-limited to respect API usage policies

                **💡 Best Practices:**
                - Include the full document text (especially the references section)
                - Ensure citations follow standard academic format
                - For best results, use documents with DOIs in references
                """)

            # Similar Papers Recommender Tab
            with gr.Tab("📚 Find Similar Papers"):
                gr.Markdown("### Similar Paper Recommender")
                gr.Markdown("""
                Discover contextually similar research papers! This tool helps you:
                - 🔍 Find related work for literature reviews
                - 📊 Explore research in similar domains
                - 🎯 Identify influential papers in your area
                - 🔗 Build comprehensive reference lists
                """)

                with gr.Tabs():
                    # Tab for text/ID input
                    with gr.Tab("🔍 By DOI/arXiv/Title"):
                        gr.Markdown("Enter paper information:")
                        recommend_input = gr.Textbox(
                            label="📄 Paper Information",
                            placeholder="Enter DOI (10.xxxx/xxxx), arXiv ID (arXiv:2101.12345), or paper title...",
                            lines=3
                        )

                        num_recommendations = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=10,
                            step=1,
                            label="Number of Recommendations",
                            info="How many similar papers to find"
                        )

                        recommend_btn = gr.Button("📚 Find Similar Papers", variant="primary", size="lg")

                        recommendations_output = gr.Textbox(
                            label="📋 Similar Papers",
                            lines=30,
                            max_lines=50,
                            interactive=False
                        )

                        recommend_btn.click(
                            fn=recommend_from_text,
                            inputs=[recommend_input, num_recommendations],
                            outputs=[recommendations_output]
                        )

                    # Tab for PDF input
                    with gr.Tab("📄 From PDF"):
                        gr.Markdown("Get recommendations based on an uploaded PDF:")
                        recommend_pdf_path_display = gr.Textbox(
                            label="Current PDF",
                            placeholder="Upload a PDF in the 'Upload PDF' tab first",
                            interactive=False
                        )

                        num_recommendations_pdf = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=10,
                            step=1,
                            label="Number of Recommendations",
                            info="How many similar papers to find"
                        )

                        recommend_pdf_btn = gr.Button("📚 Find Similar Papers from PDF", variant="primary", size="lg")

                        recommendations_pdf_output = gr.Textbox(
                            label="📋 Similar Papers",
                            lines=30,
                            max_lines=50,
                            interactive=False
                        )

                        # Update display when PDF is uploaded
                        pdf_path_store.change(
                            fn=lambda x: x,
                            inputs=[pdf_path_store],
                            outputs=[recommend_pdf_path_display]
                        )

                        recommend_pdf_btn.click(
                            fn=recommend_from_pdf,
                            inputs=[pdf_path_store, num_recommendations_pdf],
                            outputs=[recommendations_pdf_output]
                        )

                gr.Markdown("---")
                gr.Markdown("""
                **🔍 How It Works:**

                **Input Methods:**
                - **DOI**: Most accurate (e.g., 10.1145/3394486.3403043)
                - **arXiv ID**: Great for preprints (e.g., arXiv:2101.12345)
                - **Paper Title**: Searches and finds similar papers
                - **PDF Upload**: Analyzes content for recommendations

                **Recommendation Quality:**
                - Powered by Semantic Scholar's citation network
                - Based on co-citations, references, and content similarity
                - Includes highly-cited and recent papers
                - Contextually relevant to your research area

                **Information Provided:**
                - Paper titles and authors
                - Publication year and venue
                - Citation counts (impact indicator)
                - Abstracts for quick relevance assessment
                - Direct links (DOI, arXiv, Semantic Scholar)

                **💡 Tips:**
                - Use DOI or arXiv ID for best results
                - Adjust number of recommendations based on your needs
                - Check abstracts to verify relevance
                - Follow links to access full papers
                - High citation counts often indicate influential work
                """)

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
                - 🎨 Infographic generation
                - 📊 Structured summary
                - 🖼️ Image generation
                """)

        # Register API endpoints
        gr.api(retrieve_related_papers, api_name="retrieve_papers")
        gr.api(explain_research_paper, api_name="explain_paper")
        gr.api(write_social_media_post, api_name="write_social_post")
        gr.api(process_uploaded_pdf, api_name="process_pdf")
        gr.api(generate_paper_infographic, api_name="generate_infographic")
        gr.api(verify_document_sources, api_name="verify_sources")
        gr.api(recommend_similar_papers, api_name="recommend_papers")

    return demo


def launch_app():
    """Launch the Gradio application."""
    logger.info("🚀 Starting Agentic Research Assistant with Logging...")
    demo = create_app()
    demo.launch(mcp_server=True, share=True)
