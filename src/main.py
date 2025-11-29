"""
Main Gradio Application for Research Arena
Streamlined 2-tab interface: Chat + Logs
"""

import gradio as gr
from src.logging import logger, log_buffer
from src.ui.chat import chat
from src.ui.logs import get_logs, clear_logs, refresh_logs, change_log_level


def create_app():
    """Create and configure the Gradio application with 2-tab interface."""
    
    with gr.Blocks(
        title="Research Arena - Agentic Research Assistant"
    ) as demo:
        # Header
        gr.Markdown("""
        # 🔬 Research Arena
        ### AI-Powered Research Assistant with Advanced MCP Tools
        
        Powered by Google Gemini with intelligent tool calling, source verification, and multi-modal analysis.
        """)
        
        # Main Tabs
        with gr.Tabs() as tabs:
            # ============================================================
            # TAB 1: CHAT INTERFACE
            # ============================================================
            with gr.Tab("💬 Chat", id="chat_tab"):
                gr.Markdown("""
                ### Multimodal Research Assistant
                
                **What I can do:**
                - 📄 **Analyze PDFs**: Upload research papers for instant analysis
                - 🔍 **Search arXiv**: Find relevant papers on any topic
                - 📝 **Explain Research**: Get clear explanations in Arabic or English
                - 📱 **Create Social Posts**: Generate engaging summaries for social media
                - 🎨 **Generate Infographics**: Transform papers into beautiful visuals
                - ✅ **Verify Sources**: Fact-check references and claims rigorously
                - 🔗 **Recommend Papers**: Discover similar research based on DOI/title
                
                **How to use:**
                - Type your question or request in the chat
                - Attach files (PDFs, images) for analysis
                - I'll automatically call the right tools to help you!
                """)
                
                # Chat Interface
                chat_interface = gr.ChatInterface(
                    fn=chat,
                    type="messages",
                    multimodal=True,
                    examples=[
                        {"text": "Find recent papers on transformer models in NLP"},
                        {"text": "Explain this paper in simple terms", "files": []},
                        {"text": "Create a social media post about this research"},
                        {"text": "Generate an infographic from this paper summary"},
                        {"text": "Verify the sources and claims in this document"},
                        {"text": "Recommend similar papers to arXiv:2103.14030"},
                    ],
                    cache_examples=False,
                )
            
            # ============================================================
            # TAB 2: LOGS
            # ============================================================
            with gr.Tab("📋 Logs", id="logs_tab"):
                gr.Markdown("""
                ### System Logs & LLM Thinking Process
                
                Monitor the AI's reasoning process, tool calls, and API interactions in real-time.
                This helps you understand how the agent makes decisions and troubleshoot issues.
                """)
                
                with gr.Row():
                    with gr.Column(scale=3):
                        log_level_dropdown = gr.Dropdown(
                            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                            value="INFO",
                            label="🎚️ Log Level",
                            info="Filter logs by severity level"
                        )
                    
                    with gr.Column(scale=1):
                        refresh_btn = gr.Button("🔄 Refresh Logs", variant="secondary", size="sm")
                        clear_btn = gr.Button("🗑️ Clear Logs", variant="stop", size="sm")
                
                logs_display = gr.Textbox(
                    label="📋 System Logs",
                    lines=30,
                    max_lines=50,
                    interactive=False,
                    value=get_logs(),
                    elem_classes=["logs-display"]
                )
                
                gr.Markdown("""
                **Log Levels:**
                - 🐛 **DEBUG**: Detailed diagnostic information (LLM requests/responses, function args)
                - ℹ️ **INFO**: General informational messages (tool calls, major steps)
                - ⚠️ **WARNING**: Warning messages (fallbacks, non-critical issues)
                - ❌ **ERROR**: Error messages (failures, exceptions)
                """)
                
                # Event Handlers
                refresh_btn.click(
                    fn=refresh_logs,
                    outputs=[logs_display]
                )
                
                clear_btn.click(
                    fn=clear_logs,
                    outputs=[logs_display]
                )
                
                log_level_dropdown.change(
                    fn=change_log_level,
                    inputs=[log_level_dropdown],
                    outputs=[logs_display]
                )
        
        # Footer
        gr.Markdown("""
        ---
        **Research Arena** | Built for the MCP 1st Birthday Competition | Powered by Google Gemini API
        
        🔗 [GitHub](https://github.com/Ahmed-Ezzat20/research_arena) | 📧 [Report Issues](https://github.com/Ahmed-Ezzat20/research_arena/issues)
        """)
        
        # Custom CSS for better styling
        demo.css = """
        .logs-display textarea {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
        }
        """
    
    return demo


def main():
    """Main entry point for the application."""
    logger.info("="*80)
    logger.info("🚀 Starting Research Arena Application")
    logger.info("="*80)
    
    app = create_app()
    
    # Launch the app
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )


if __name__ == "__main__":
    main()
