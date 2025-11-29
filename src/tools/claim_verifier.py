"""
Claim Extraction and Verification Module - Refactored with async and provider abstraction
Uses LLM to extract verifiable claims and validate them against evidence.
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from src.logging import logger
from src.providers.base import BaseLLMProvider
from src.utils.api_clients import SemanticScholarAPI, RateLimiter


class ClaimExtractor:
    """Extract verifiable claims from academic documents."""
    
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
    
    def load_extraction_prompt(self) -> str:
        """Load claim extraction prompt."""
        try:
            with open("prompts/claim_extraction_prompt.txt", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("⚠️ claim_extraction_prompt.txt not found, using default")
            return self._get_default_extraction_prompt()
    
    def _get_default_extraction_prompt(self) -> str:
        """Default claim extraction prompt."""
        return """You are a scientific fact-checker analyzing an academic document.

Your task: Extract the most significant, verifiable claims from this document.

Focus on:
1. **Empirical claims**: Specific findings, measurements, experimental results
2. **Comparative claims**: "X is better than Y", "A outperforms B"
3. **Causal claims**: "X causes Y", "A leads to B"
4. **Statistical claims**: Percentages, correlations, significance levels
5. **Novel contributions**: New methods, discoveries, or insights

DO NOT extract:
- Vague statements or opinions
- Background information or established facts
- Methodological descriptions (unless claiming novelty)
- Future work suggestions

For each claim, provide:
1. **claim_text**: The exact claim statement (1-2 sentences)
2. **claim_type**: empirical|comparative|causal|statistical|contribution
3. **importance**: high|medium|low (based on centrality to paper's thesis)
4. **specificity**: specific|moderate|vague
5. **context**: Brief context (where in paper, what section)

Extract 5-10 of the MOST IMPORTANT, VERIFIABLE claims.

Format as JSON array of objects."""
    
    async def extract_claims(self, document_text: str, max_claims: int = 10) -> List[Dict[str, str]]:
        """
        Extract verifiable claims from document.
        
        Args:
            document_text: Full document text
            max_claims: Maximum number of claims to extract
            
        Returns:
            List of claim dictionaries
        """
        logger.info("🔍 Extracting verifiable claims from document...")
        
        try:
            extraction_prompt = self.load_extraction_prompt()
            
            full_prompt = f"""{extraction_prompt}

Document text (first 12000 characters):
{document_text[:12000]}
"""
            
            logger.debug("📤 LLM REQUEST: Claim extraction")
            response = await self.provider.generate_simple(full_prompt, temperature=0.3)
            logger.info("📥 LLM RESPONSE: Claims extracted")
            
            # Parse JSON response
            text = response.strip()
            
            # Extract JSON from markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            claims = json.loads(text)
            
            # Limit to max_claims
            claims = claims[:max_claims]
            
            logger.info(f"✅ Extracted {len(claims)} verifiable claims")
            
            return claims
        
        except Exception as e:
            logger.error(f"❌ Error extracting claims: {str(e)}")
            return []


class ClaimVerifier:
    """Verify claims against external evidence."""
    
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
        self.semantic_scholar = SemanticScholarAPI()
        self.rate_limiter = RateLimiter(calls_per_second=1.5)
    
    def load_verification_prompt(self) -> str:
        """Load claim verification prompt."""
        try:
            with open("prompts/claim_verification_prompt.txt", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("⚠️ claim_verification_prompt.txt not found, using default")
            return self._get_default_verification_prompt()
    
    def _get_default_verification_prompt(self) -> str:
        """Default claim verification prompt."""
        return """You are a rigorous scientific fact-checker.

Your task: Verify a scientific claim against gathered evidence.

Process:
1. Read the claim carefully
2. Analyze all provided evidence (research papers, citations, data)
3. Determine if the evidence supports, contradicts, or is inconclusive about the claim
4. Provide a confidence score (0-100%)

Verification Status Guidelines:
- **SUPPORTED**: Strong evidence directly supports the claim (>70% confidence)
- **PARTIALLY SUPPORTED**: Some evidence supports, but not conclusive (40-70%)
- **CONTRADICTED**: Evidence contradicts the claim (>70% confidence)
- **NO CONSENSUS**: Mixed or insufficient evidence (<40% confidence either way)
- **INSUFFICIENT EVIDENCE**: Not enough evidence to evaluate

For your response, provide:
1. **status**: SUPPORTED | PARTIALLY SUPPORTED | CONTRADICTED | NO CONSENSUS | INSUFFICIENT EVIDENCE
2. **confidence_score**: 0-100 (integer)
3. **reasoning**: 2-3 sentences explaining your verdict
4. **supporting_evidence**: Brief summary of evidence FOR the claim
5. **contradicting_evidence**: Brief summary of evidence AGAINST the claim (if any)
6. **limitations**: What evidence is missing or uncertain

Be skeptical and rigorous. Default to "NO CONSENSUS" or "INSUFFICIENT EVIDENCE" when uncertain.

Format as JSON object."""
    
    async def verify_claim(self, claim: Dict[str, str]) -> Dict[str, Any]:
        """
        Verify a single claim against external evidence.
        
        Args:
            claim: Claim dictionary with claim_text and metadata
            
        Returns:
            Verification result with status, confidence, and evidence
        """
        claim_text = claim.get('claim_text', '')
        logger.info(f"🔍 Verifying claim: '{claim_text[:80]}...'")
        
        # Step 1: Gather evidence
        await asyncio.sleep(self.rate_limiter.wait_time())
        evidence = await self._gather_evidence(claim_text)
        
        # Step 2: LLM-based verification
        await asyncio.sleep(self.rate_limiter.wait_time())
        verification_result = await self._llm_verify(claim, evidence)
        
        # Add claim metadata
        verification_result['original_claim'] = claim
        
        logger.info(f"✅ Verification complete: {verification_result.get('status', 'Unknown')} ({verification_result.get('confidence_score', 0)}%)")
        
        return verification_result
    
    async def _gather_evidence(self, claim_text: str) -> List[Dict[str, Any]]:
        """Gather research evidence for a claim."""
        logger.debug(f"📚 Gathering evidence for: '{claim_text[:50]}...'")
        
        evidence = []
        
        # Search Semantic Scholar for relevant papers
        try:
            # Run synchronous API call in executor
            loop = asyncio.get_event_loop()
            papers = await loop.run_in_executor(
                None,
                lambda: self.semantic_scholar.search_paper(claim_text, limit=5)
            )
            
            for paper in papers:
                evidence.append({
                    'source': 'Semantic Scholar',
                    'title': paper.get('title', 'Unknown'),
                    'authors': [a.get('name', '') for a in paper.get('authors', [])],
                    'year': paper.get('year'),
                    'abstract': paper.get('abstract', ''),
                    'citation_count': paper.get('citationCount', 0),
                    'url': paper.get('url', '')
                })
            
            logger.info(f"📚 Found {len(papers)} research papers as evidence")
        
        except Exception as e:
            logger.error(f"❌ Error gathering evidence: {str(e)}")
        
        return evidence
    
    async def _llm_verify(self, claim: Dict[str, str], evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use LLM to verify claim against evidence."""
        logger.debug("📤 LLM REQUEST: Claim verification")
        
        try:
            verification_prompt = self.load_verification_prompt()
            
            # Format evidence for prompt
            evidence_text = self._format_evidence(evidence)
            
            full_prompt = f"""{verification_prompt}

CLAIM TO VERIFY:
{claim.get('claim_text', '')}

Claim Type: {claim.get('claim_type', 'unknown')}
Claim Context: {claim.get('context', 'not specified')}

GATHERED EVIDENCE:
{evidence_text}

Provide your verification in JSON format.
"""
            
            response = await self.provider.generate_simple(full_prompt, temperature=0.2)
            logger.debug("📥 LLM RESPONSE: Verification complete")
            
            # Parse JSON response
            text = response.strip()
            
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(text)
            result['evidence_count'] = len(evidence)
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Error in LLM verification: {str(e)}")
            return {
                'status': 'ERROR',
                'confidence_score': 0,
                'reasoning': f'Verification failed: {str(e)}',
                'supporting_evidence': '',
                'contradicting_evidence': '',
                'limitations': 'Verification process encountered an error',
                'evidence_count': len(evidence)
            }
    
    def _format_evidence(self, evidence: List[Dict[str, Any]]) -> str:
        """Format evidence for LLM prompt."""
        if not evidence:
            return "No evidence found."
        
        formatted = []
        for i, paper in enumerate(evidence, 1):
            formatted.append(f"""
Evidence {i}:
Title: {paper.get('title', 'Unknown')}
Authors: {', '.join(paper.get('authors', []))[:200]}
Year: {paper.get('year', 'N/A')}
Citations: {paper.get('citation_count', 0)}
Abstract: {paper.get('abstract', 'No abstract')[:500]}
""")
        
        return "\n".join(formatted)


async def verify_all_claims(
    document_text: str,
    provider: BaseLLMProvider
) -> Dict[str, Any]:
    """
    Main function to extract and verify all claims in a document.
    
    Args:
        document_text: Full document text
        provider: LLM provider instance
        
    Returns:
        Dictionary with extraction and verification results
    """
    logger.info("🔍 Starting claim verification pipeline...")
    
    extractor = ClaimExtractor(provider)
    verifier = ClaimVerifier(provider)
    
    # Extract claims
    claims = await extractor.extract_claims(document_text)
    
    if not claims:
        logger.warning("⚠️ No claims extracted")
        return {
            'total_claims': 0,
            'claims': [],
            'verification_results': [],
            'summary': {
                'supported': 0,
                'partially_supported': 0,
                'contradicted': 0,
                'no_consensus': 0,
                'insufficient_evidence': 0
            }
        }
    
    # Verify each claim
    verification_results = []
    for i, claim in enumerate(claims, 1):
        logger.info(f"📋 Verifying claim {i}/{len(claims)}...")
        result = await verifier.verify_claim(claim)
        verification_results.append(result)
    
    # Generate summary
    summary = {
        'supported': sum(1 for r in verification_results if 'SUPPORTED' in r.get('status', '') and 'PARTIALLY' not in r.get('status', '')),
        'partially_supported': sum(1 for r in verification_results if 'PARTIALLY' in r.get('status', '')),
        'contradicted': sum(1 for r in verification_results if 'CONTRADICTED' in r.get('status', '')),
        'no_consensus': sum(1 for r in verification_results if 'NO CONSENSUS' in r.get('status', '')),
        'insufficient_evidence': sum(1 for r in verification_results if 'INSUFFICIENT' in r.get('status', ''))
    }
    
    logger.info(f"✅ Claim verification complete: {summary['supported']} supported, {summary['contradicted']} contradicted")
    
    return {
        'total_claims': len(claims),
        'claims': claims,
        'verification_results': verification_results,
        'summary': summary
    }
