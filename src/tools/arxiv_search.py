"""
arXiv paper search tool with LLM-enhanced query refinement and ranking.
"""

import arxiv
import google.generativeai as genai
from src.config import GEMINI_MODEL_NAME
from src.logging import logger


def retrieve_related_papers(query: str) -> str:
    """Retrieve up to 5 recent arXiv papers matching the query."""
    logger.info(f"🔍 FUNCTION CALL: retrieve_related_papers(query='{query}')")
    try:
        # Use Gemini to refine and expand the search query for better results
        logger.debug("📤 LLM REQUEST: Query refinement")
        query_model = genai.GenerativeModel(model_name=GEMINI_MODEL_NAME)
        refine_prompt = f"""Given this research topic query: "{query}"

Create an optimized arXiv search query that will find the most relevant papers. Consider:
- Technical terms and synonyms
- Related concepts
- Common paper titles in this area

Provide ONLY the search query text, no explanation. Make it specific and focused.
For example, if user asks about "transformers", return something like: "transformer architecture attention mechanism deep learning"
"""
        logger.debug(f"  Prompt: {refine_prompt[:100]}...")
        refined_query = query_model.generate_content(refine_prompt).text.strip()
        logger.info(f"📥 LLM RESPONSE: Refined query = '{refined_query}'")

        # Search with refined query, sorted by relevance
        logger.debug(f"🔎 Searching arXiv with refined query: '{refined_query}'")
        client = arxiv.Client()
        search = arxiv.Search(
            query=refined_query,
            max_results=10,  # Get more results to filter
            sort_by=arxiv.SortCriterion.Relevance,  # Sort by relevance instead of date
        )

        # Get results and use Gemini to filter for relevance
        all_results = list(client.results(search))
        logger.info(f"📚 Found {len(all_results)} papers from arXiv")

        # Use Gemini to rank results by relevance to original query
        papers_for_ranking = "\n\n".join([
            f"Paper {i+1}:\nTitle: {r.title}\nAbstract: {r.summary[:200]}..."
            for i, r in enumerate(all_results)
        ])

        ranking_prompt = f"""Given the user's search query: "{query}"

Rank these papers by relevance (most relevant first). Return ONLY the paper numbers in order, comma-separated.
For example: "3,1,5,2,4"

{papers_for_ranking}

Return only the top 5 most relevant paper numbers:"""

        logger.debug("📤 LLM REQUEST: Ranking papers by relevance")
        ranking_response = query_model.generate_content(ranking_prompt).text.strip()
        logger.info(f"📥 LLM RESPONSE: Ranking = '{ranking_response}'")
        ranked_indices = [int(x.strip()) - 1 for x in ranking_response.split(",")[:5]]
        logger.debug(f"  Top 5 indices: {ranked_indices}")

        # Build final results
        results = []
        for idx, paper_idx in enumerate(ranked_indices, 1):
            if paper_idx < len(all_results):
                result = all_results[paper_idx]
                title = result.title.strip().replace("\n", " ")
                authors = ", ".join([author.name for author in result.authors[:3]])
                if len(result.authors) > 3:
                    authors += " et al."
                published = result.published.strftime("%Y-%m-%d")
                summary = result.summary.strip().replace("\n", " ")[:300] + "..." if len(result.summary) > 300 else result.summary.strip().replace("\n", " ")
                url = result.pdf_url

                paper_info = f"""Paper {idx}:
Title: {title}
Authors: {authors}
Published: {published}
Summary: {summary}
PDF: {url}"""
                results.append(paper_info)

        logger.info(f"✅ FUNCTION COMPLETE: Returning {len(results)} papers")
        return "\n\n" + "="*80 + "\n\n".join(results) if results else "No papers found."

    except Exception as e:
        logger.error(f"❌ ERROR in retrieve_related_papers: {str(e)}")
        logger.warning("⚠️  Falling back to basic arXiv search without LLM ranking")
        # Fallback to basic search if Gemini fails
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=5,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        results = []
        for idx, result in enumerate(client.results(search), 1):
            title = result.title.strip().replace("\n", " ")
            authors = ", ".join([author.name for author in result.authors[:3]])
            if len(result.authors) > 3:
                authors += " et al."
            published = result.published.strftime("%Y-%m-%d")
            summary = result.summary.strip().replace("\n", " ")[:300] + "..." if len(result.summary) > 300 else result.summary.strip().replace("\n", " ")
            url = result.pdf_url

            paper_info = f"""Paper {idx}:
Title: {title}
Authors: {authors}
Published: {published}
Summary: {summary}
PDF: {url}"""
            results.append(paper_info)

        return "\n\n" + "="*80 + "\n\n".join(results) if results else "No papers found."
