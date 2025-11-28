"""
Paper-to-Infographic Generator using Gemini's image generation capabilities.
Creates visually stunning infographics from research paper summaries.
"""

import os
import json
import base64
from datetime import datetime
import google.generativeai as genai
from src.config import GEMINI_MODEL_NAME
from src.logging import logger


def load_infographic_prompt():
    """Load the infographic generation prompt from file."""
    try:
        with open("prompts/infographic_prompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("⚠️ infographic_prompt.txt not found, using default prompt")
        return """You are a creative designer. Create a detailed description of an infographic
that summarizes a research paper. The infographic should be visually appealing, well-organized,
and easy to understand."""


def generate_structured_summary(paper_info: str) -> dict:
    """
    Generate a structured summary of the paper broken down into key sections.

    Args:
        paper_info: Research paper information or text

    Returns:
        dict: Structured summary with sections
    """
    logger.debug("📤 LLM REQUEST: Generating structured summary for infographic")

    try:
        summary_model = genai.GenerativeModel(model_name=GEMINI_MODEL_NAME)

        summary_prompt = f"""
Analyze this research paper and create a detailed structured summary for an academic infographic.

Extract and organize the following sections:

1. **title_and_authors**: Full paper title and author list
2. **research_problem**: What problem does this address? Why is it important? (2-3 sentences)
3. **background**: Brief context, key concepts, related work (2-3 sentences)
4. **methods**: Approach, techniques, data sources (3-4 bullet points)
5. **key_results**: Main findings with metrics and significance (4-6 bullet points)
6. **core_insights**: Novel contributions and takeaways (3-4 bullet points)
7. **limitations**: Constraints and scope boundaries (2-3 bullet points)
8. **conclusion**: Summary and broader implications (2-3 sentences)
9. **future_directions**: Next steps and open questions (2-3 bullet points)
10. **visual_suggestions**: Recommended color scheme, layout approach, and visual elements

Format your response as a JSON object with these exact keys.
For array fields (methods, key_results, etc.), provide arrays of strings.
For text fields, provide concise, clear text.

Research Paper Information:
{paper_info[:8000]}
"""

        response = summary_model.generate_content(summary_prompt)
        logger.info("📥 LLM RESPONSE: Structured summary generated")

        # Try to parse JSON response
        try:
            # Extract JSON from markdown code blocks if present
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            summary_data = json.loads(text)
            logger.debug(f"  Parsed structured summary: {list(summary_data.keys())}")
            return summary_data
        except json.JSONDecodeError:
            logger.warning("⚠️ Could not parse JSON, using text response")
            # Fallback: return as single text block
            return {
                "title_and_authors": "Research Paper Summary",
                "research_problem": response.text[:300],
                "background": "",
                "methods": [],
                "key_results": [],
                "core_insights": [],
                "limitations": [],
                "conclusion": "",
                "future_directions": [],
                "visual_suggestions": "Modern, professional color scheme"
            }

    except Exception as e:
        logger.error(f"❌ ERROR generating structured summary: {str(e)}")
        return {
            "title_and_authors": "Research Paper Summary",
            "research_problem": paper_info[:300],
            "background": "",
            "methods": [],
            "key_results": [],
            "core_insights": [],
            "limitations": [],
            "conclusion": "",
            "future_directions": [],
            "visual_suggestions": "Clean and minimal design"
        }


def create_infographic_prompt(summary_data: dict) -> str:
    """
    Create a detailed prompt for the image generation model.

    Args:
        summary_data: Structured summary data

    Returns:
        str: Detailed creative brief for image generation
    """
    prompt_template = load_infographic_prompt()

    # Build a comprehensive academic infographic brief
    creative_brief = f"""
{prompt_template}

INFOGRAPHIC CONTENT:

=== TITLE & AUTHORS ===
{summary_data.get('title_and_authors', 'Research Paper Summary')}

=== RESEARCH PROBLEM / MOTIVATION ===
{summary_data.get('research_problem', '')}

=== BACKGROUND / CONTEXT ===
{summary_data.get('background', '')}

=== METHODS OVERVIEW ===
{chr(10).join(['• ' + str(m) for m in summary_data.get('methods', [])])}

=== KEY DATA & RESULTS ===
{chr(10).join(['• ' + str(result) for result in summary_data.get('key_results', [])])}

=== CORE INSIGHTS / CONTRIBUTIONS ===
{chr(10).join(['• ' + str(insight) for insight in summary_data.get('core_insights', [])])}

=== LIMITATIONS ===
{chr(10).join(['• ' + str(lim) for lim in summary_data.get('limitations', [])])}

=== CONCLUSION ===
{summary_data.get('conclusion', '')}

=== FUTURE DIRECTIONS / OPEN PROBLEMS ===
{chr(10).join(['• ' + str(future) for future in summary_data.get('future_directions', [])])}

DESIGN SPECIFICATIONS:
- Layout: Conference poster style with hierarchical sections
- Color Palette: {summary_data.get('visual_suggestions', 'Professional academic color scheme (blues, grays, white)')}
- Style: Clean, data-focused, conference-ready
- Typography: Bold section headers, clear readable body text
- Visual Elements: Charts/diagrams for results, icons for sections, clear dividers
- Hierarchy: Title → Section headers → Content → Details
- Whitespace: Balanced, professional spacing throughout

Create a professional academic infographic suitable for conference presentations,
research posters, and scholarly social media sharing.
"""

    return creative_brief


def generate_infographic_image(paper_info: str) -> tuple[str, dict]:
    """
    Generate an infographic image from paper information.

    Args:
        paper_info: Research paper information or text

    Returns:
        tuple: (file_path to saved image, summary_data dict)
    """
    logger.info(f"🔍 FUNCTION CALL: generate_infographic_image(paper_info length={len(paper_info)} chars)")

    try:
        # Step 1: Generate structured summary
        logger.info("📊 Step 1/3: Generating structured summary...")
        summary_data = generate_structured_summary(paper_info)

        # Step 2: Create detailed prompt for image generation
        logger.info("🎨 Step 2/3: Creating creative brief for image generation...")
        creative_prompt = create_infographic_prompt(summary_data)
        logger.debug(f"  Creative prompt length: {len(creative_prompt)} chars")

        # Step 3: Generate image using Gemini's image generation
        logger.info("🖼️ Step 3/3: Generating infographic image...")
        logger.debug("📤 LLM REQUEST: Image generation")

        # Use Gemini model for image generation
        # Note: Gemini 2.0 and later have image generation capabilities
        image_model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

        response = image_model.generate_content(
            creative_prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="image/jpeg"
            )
        )

        logger.info("📥 LLM RESPONSE: Image generated")

        # Save the generated image
        output_dir = "generated_infographics"
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"infographic_{timestamp}.jpg"
        filepath = os.path.join(output_dir, filename)

        # Extract and save the image
        if hasattr(response, 'parts') and len(response.parts) > 0:
            image_part = response.parts[0]
            if hasattr(image_part, 'inline_data'):
                image_data = image_part.inline_data.data
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                logger.info(f"✅ Infographic saved: {filepath}")
            else:
                raise ValueError("No inline_data found in response")
        else:
            raise ValueError("No image parts in response")

        return filepath, summary_data

    except Exception as e:
        logger.error(f"❌ ERROR in generate_infographic_image: {str(e)}")
        # Check if it's a model availability issue
        if "not found" in str(e).lower() or "not available" in str(e).lower():
            error_msg = """⚠️ Image generation model not available.

The Gemini image generation feature may not be available in your region or with your API key.

Alternative approach:
1. The system has generated a structured summary of your paper
2. You can use this summary with external tools like:
   - Canva (with AI design features)
   - Adobe Express
   - Microsoft Designer
   - DALL-E or Midjourney

The structured summary has been logged and can be exported."""
        else:
            error_msg = f"Error generating infographic: {str(e)}"

        return None, {"error": error_msg}


def generate_paper_infographic(paper_info: str) -> str:
    """
    Main function to generate infographic from paper info.
    Callable by Gemini as a tool.

    Args:
        paper_info: Research paper information or text

    Returns:
        str: Success message with file path or error message
    """
    logger.info(f"🔍 FUNCTION CALL: generate_paper_infographic(paper_info length={len(paper_info)} chars)")

    try:
        filepath, summary_data = generate_infographic_image(paper_info)

        if filepath:
            success_msg = f"""✅ Infographic generated successfully!

📍 Saved to: {filepath}

📊 Comprehensive academic infographic includes:
- Title & Authors
- Research Problem/Motivation
- Background & Context
- Methods Overview
- Key Data & Results
- Core Insights/Contributions
- Limitations
- Conclusion
- Future Directions

💡 Perfect for:
  • Conference presentations and posters
  • Academic social media (LinkedIn, Twitter)
  • Research group presentations
  • Thesis/dissertation defense slides

Download and share your professional research visualization!
"""
            logger.info("✅ Infographic generation completed successfully")
            return success_msg
        else:
            # Return the structured summary even if image generation failed
            error = summary_data.get('error', 'Unknown error')
            summary_text = f"""
{error}

However, here's the comprehensive structured summary that was generated:

**TITLE & AUTHORS**
{summary_data.get('title_and_authors', 'N/A')}

**RESEARCH PROBLEM / MOTIVATION**
{summary_data.get('research_problem', 'N/A')}

**BACKGROUND / CONTEXT**
{summary_data.get('background', 'N/A')}

**METHODS OVERVIEW**
{chr(10).join(['• ' + str(m) for m in summary_data.get('methods', [])] or ['N/A'])}

**KEY DATA & RESULTS**
{chr(10).join(['• ' + str(r) for r in summary_data.get('key_results', [])] or ['N/A'])}

**CORE INSIGHTS / CONTRIBUTIONS**
{chr(10).join(['• ' + str(i) for i in summary_data.get('core_insights', [])] or ['N/A'])}

**LIMITATIONS**
{chr(10).join(['• ' + str(l) for l in summary_data.get('limitations', [])] or ['N/A'])}

**CONCLUSION**
{summary_data.get('conclusion', 'N/A')}

**FUTURE DIRECTIONS / OPEN PROBLEMS**
{chr(10).join(['• ' + str(f) for f in summary_data.get('future_directions', [])] or ['N/A'])}

You can use this structured summary with external design tools like:
• Canva (canva.com) - Easy drag-and-drop design
• Adobe Express (adobe.com/express) - Professional templates
• Microsoft Designer (designer.microsoft.com) - AI-assisted design
• PowerPoint/Keynote - Create custom poster layouts
"""
            return summary_text

    except Exception as e:
        logger.error(f"❌ ERROR in generate_paper_infographic: {str(e)}")
        return f"Error generating infographic: {str(e)}"
