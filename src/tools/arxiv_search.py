"""
arXiv Search Tool - Refactored with async and provider abstraction
Retrieves related research papers from arXiv using LLM-refined queries.
"""

import asyncio
import arxiv
from typing import List, Dict, Any
from src.logging import logger
from src.providers.base import BaseLLMProvider


async def retrieve_related_papers(
    query: str,
    provider: BaseLLMProvider,
    max_results: int = 5
) -> str:
    """
    Retrieve related papers from arXiv using LLM-refined query.
    
    Args:
        query: The search query
        provider: LLM provider instance for query refinement
        max_results: Maximum number of papers to retrieve
        
    Returns:
        Formatted string with paper information
    """
    logger.info(f"🔍 Searching arXiv for: '{query}'")
    
    try:
        # Step 1: Refine the query using LLM
        refined_query = await _refine_search_query(query, provider)
        logger.info(f"✨ Refined query: '{refined_query}'")
        
        # Step 2: Search arXiv
        papers = await _search_arxiv(refined_query, max_results * 2)  # Get more for ranking
        
        if not papers:
            logger.warning("⚠️ No papers found")
            return "No papers found for the given query."
        
        # Step 3: Rank papers using LLM
        ranked_papers = await _rank_papers(query, papers, provider, max_results)
        
        # Step 4: Format results
        result = _format_papers(ranked_papers)
        
        logger.info(f"✅ Retrieved {len(ranked_papers)} papers")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error retrieving papers: {str(e)}")
        return f"Error retrieving papers: {str(e)}"


async def _refine_search_query(query: str, provider: BaseLLMProvider) -> str:
    """Refine the search query using LLM."""
    logger.debug("📤 LLM REQUEST: Refining search query")
    
    prompt = f"""You are a research assistant helping to search for academic papers.
    
Given this user query: "{query}"

Generate a concise, effective arXiv search query that will find the most relevant papers.
Focus on key technical terms and concepts. Keep it under 10 words.

Return ONLY the refined query, nothing else."""

    try:
        refined = await provider.generate_simple(prompt, temperature=0.3)
        return refined.strip()
    except Exception as e:
        logger.warning(f"⚠️ Query refinement failed, using original: {str(e)}")
        return query


async def _search_arxiv(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Search arXiv and return paper metadata."""
    logger.debug(f"🔍 Searching arXiv with query: '{query}'")
    
    def _sync_search():
        """Synchronous arXiv search (runs in executor)."""
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for result in search.results():
            papers.append({
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'summary': result.summary,
                'published': result.published.strftime('%Y-%m-%d'),
                'url': result.entry_id,
                'pdf_url': result.pdf_url,
            })
        return papers
    
    # Run synchronous search in executor to avoid blocking
    loop = asyncio.get_event_loop()
    papers = await loop.run_in_executor(None, _sync_search)
    
    logger.info(f"📚 Found {len(papers)} papers from arXiv")
    return papers


async def _rank_papers(
    original_query: str,
    papers: List[Dict[str, Any]],
    provider: BaseLLMProvider,
    max_results: int
) -> List[Dict[str, Any]]:
    """Rank papers by relevance using LLM."""
    if len(papers) <= max_results:
        return papers[:max_results]
    
    logger.debug("📤 LLM REQUEST: Ranking papers by relevance")
    
    # Create paper summaries for ranking
    paper_summaries = []
    for i, paper in enumerate(papers):
        summary = f"{i+1}. {paper['title']}\n   {paper['summary'][:200]}..."
        paper_summaries.append(summary)
    
    prompt = f"""You are a research assistant. Rank these papers by relevance to the query: "{original_query}"

Papers:
{chr(10).join(paper_summaries)}

Return ONLY a comma-separated list of the top {max_results} paper numbers in order of relevance (most relevant first).
Example: 3,1,5,2,4"""

    try:
        ranking_str = await provider.generate_simple(prompt, temperature=0.1)
        ranking_str = ranking_str.strip()
        
        # Parse ranking
        rankings = [int(x.strip()) - 1 for x in ranking_str.split(',') if x.strip().isdigit()]
        rankings = rankings[:max_results]  # Take only top N
        
        # Reorder papers
        ranked_papers = []
        for idx in rankings:
            if 0 <= idx < len(papers):
                ranked_papers.append(papers[idx])
        
        # Add any missing papers at the end until we have max_results
        for i, paper in enumerate(papers):
            if len(ranked_papers) >= max_results:
                break
            if i not in rankings:
                ranked_papers.append(paper)
        
        logger.info("✅ Papers ranked by relevance")
        return ranked_papers[:max_results]
        
    except Exception as e:
        logger.warning(f"⚠️ Ranking failed, using original order: {str(e)}")
        return papers[:max_results]


def _format_papers(papers: List[Dict[str, Any]]) -> str:
    """Format papers as a readable string."""
    if not papers:
        return "No papers found."
    
    formatted = f"Found {len(papers)} relevant papers:\n\n"
    
    for i, paper in enumerate(papers, 1):
        authors = ", ".join(paper['authors'][:3])
        if len(paper['authors']) > 3:
            authors += " et al."
        
        formatted += f"{i}. **{paper['title']}**\n"
        formatted += f"   Authors: {authors}\n"
        formatted += f"   Published: {paper['published']}\n"
        formatted += f"   Summary: {paper['summary'][:300]}...\n"
        formatted += f"   URL: {paper['url']}\n"
        formatted += f"   PDF: {paper['pdf_url']}\n\n"
    
    return formatted
