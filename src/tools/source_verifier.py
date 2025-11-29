"""
Advanced Source Verification Tool - Refactored with async and provider abstraction
Coordinates reference validation and claim verification pipelines.
"""

from typing import Dict, Any
from src.logging import logger
from src.providers.base import BaseLLMProvider
from src.tools.reference_validator import validate_all_references
from src.tools.claim_verifier import verify_all_claims


async def verify_document_sources(
    document_text: str,
    provider: BaseLLMProvider,
    verify_claims: bool = True,
    verify_references: bool = True
) -> str:
    """
    Main function to perform comprehensive source verification on a document.
    
    This is the primary tool that orchestrates the entire verification pipeline:
    1. Reference validation (DOIs, citations, metadata)
    2. Claim extraction and verification (fact-checking against research)
    
    Args:
        document_text: Full document text to verify
        provider: LLM provider instance
        verify_claims: Whether to verify claims (default: True)
        verify_references: Whether to verify references (default: True)
        
    Returns:
        Formatted verification report as text
    """
    logger.info("="*80)
    logger.info("🔍 ADVANCED SOURCE VERIFICATION - Starting comprehensive validation")
    logger.info("="*80)
    
    if not document_text or len(document_text) < 100:
        logger.warning("⚠️ Document too short for verification")
        return "⚠️ Error: Document is too short for verification (minimum 100 characters)"
    
    results = {
        'document_length': len(document_text),
        'reference_validation': None,
        'claim_verification': None
    }
    
    # Phase 1: Reference Validation
    if verify_references:
        logger.info("\n" + "="*80)
        logger.info("📚 PHASE 1: REFERENCE VALIDATION")
        logger.info("="*80)
        
        try:
            ref_results = await validate_all_references(document_text, provider)
            results['reference_validation'] = ref_results
            
            logger.info(f"✅ Reference validation complete: {ref_results['summary']}")
        except Exception as e:
            logger.error(f"❌ Reference validation failed: {str(e)}")
            results['reference_validation'] = {'error': str(e)}
    
    # Phase 2: Claim Verification
    if verify_claims:
        logger.info("\n" + "="*80)
        logger.info("🔍 PHASE 2: CLAIM VERIFICATION")
        logger.info("="*80)
        
        try:
            claim_results = await verify_all_claims(document_text, provider)
            results['claim_verification'] = claim_results
            
            logger.info(f"✅ Claim verification complete: {claim_results['summary']}")
        except Exception as e:
            logger.error(f"❌ Claim verification failed: {str(e)}")
            results['claim_verification'] = {'error': str(e)}
    
    logger.info("\n" + "="*80)
    logger.info("✅ VERIFICATION PIPELINE COMPLETE")
    logger.info("="*80)
    
    # Generate formatted report
    report = _generate_verification_report(results)
    
    return report


def _generate_verification_report(results: Dict[str, Any]) -> str:
    """Generate a formatted text report from verification results."""
    
    report_lines = []
    
    # Header
    report_lines.append("=" * 80)
    report_lines.append("🔍 ADVANCED SOURCE VERIFICATION REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")
    report_lines.append(f"📄 Document Length: {results['document_length']:,} characters")
    report_lines.append("")
    
    # Reference Validation Section
    if results.get('reference_validation'):
        ref_data = results['reference_validation']
        
        if 'error' in ref_data:
            report_lines.append("📚 REFERENCE VALIDATION: ❌ ERROR")
            report_lines.append(f"   Error: {ref_data['error']}")
        else:
            summary = ref_data.get('summary', {})
            total = ref_data.get('total_references', 0)
            
            report_lines.append("=" * 80)
            report_lines.append("📚 REFERENCE VALIDATION RESULTS")
            report_lines.append("=" * 80)
            report_lines.append("")
            report_lines.append(f"Total References Analyzed: {total}")
            report_lines.append("")
            report_lines.append("Summary:")
            report_lines.append(f"  ✅ Fully Verified:        {summary.get('verified', 0)}")
            report_lines.append(f"  ⚠️  With Issues:          {summary.get('with_issues', 0)}")
            report_lines.append(f"  ❌ Validation Failed:     {summary.get('failed', 0)}")
            report_lines.append(f"  ❓ Could Not Verify:      {summary.get('unverifiable', 0)}")
            report_lines.append("")
            
            # Detailed reference results
            if ref_data.get('validation_results'):
                report_lines.append("-" * 80)
                report_lines.append("DETAILED REFERENCE ANALYSIS:")
                report_lines.append("-" * 80)
                report_lines.append("")
                
                for i, val_result in enumerate(ref_data['validation_results'], 1):
                    ref = val_result['original_reference']
                    status = val_result['validation_status']
                    
                    report_lines.append(f"[{i}] {status}")
                    
                    title = ref.get('title', 'No title')
                    if title:
                        report_lines.append(f"    Title: {title[:80]}{'...' if len(title) > 80 else ''}")
                    
                    if ref.get('doi'):
                        report_lines.append(f"    DOI: {ref['doi']}")
                    
                    if val_result.get('issues'):
                        report_lines.append(f"    Issues:")
                        for issue in val_result['issues']:
                            report_lines.append(f"      • {issue}")
                    
                    report_lines.append("")
    
    # Claim Verification Section
    if results.get('claim_verification'):
        claim_data = results['claim_verification']
        
        if 'error' in claim_data:
            report_lines.append("🔍 CLAIM VERIFICATION: ❌ ERROR")
            report_lines.append(f"   Error: {claim_data['error']}")
        else:
            summary = claim_data.get('summary', {})
            total = claim_data.get('total_claims', 0)
            
            report_lines.append("=" * 80)
            report_lines.append("🔍 CLAIM VERIFICATION RESULTS")
            report_lines.append("=" * 80)
            report_lines.append("")
            report_lines.append(f"Total Claims Analyzed: {total}")
            report_lines.append("")
            report_lines.append("Summary:")
            report_lines.append(f"  ✅ Supported:              {summary.get('supported', 0)}")
            report_lines.append(f"  ⚠️  Partially Supported:   {summary.get('partially_supported', 0)}")
            report_lines.append(f"  ❌ Contradicted:           {summary.get('contradicted', 0)}")
            report_lines.append(f"  ❓ No Consensus:           {summary.get('no_consensus', 0)}")
            report_lines.append(f"  📊 Insufficient Evidence:  {summary.get('insufficient_evidence', 0)}")
            report_lines.append("")
            
            # Detailed claim results
            if claim_data.get('verification_results'):
                report_lines.append("-" * 80)
                report_lines.append("DETAILED CLAIM ANALYSIS:")
                report_lines.append("-" * 80)
                report_lines.append("")
                
                for i, ver_result in enumerate(claim_data['verification_results'], 1):
                    claim = ver_result.get('original_claim', {})
                    status = ver_result.get('status', 'Unknown')
                    confidence = ver_result.get('confidence_score', 0)
                    
                    # Status emoji mapping
                    status_emoji = {
                        'SUPPORTED': '✅',
                        'PARTIALLY SUPPORTED': '⚠️',
                        'CONTRADICTED': '❌',
                        'NO CONSENSUS': '❓',
                        'INSUFFICIENT EVIDENCE': '📊'
                    }
                    emoji = status_emoji.get(status, '❓')
                    
                    report_lines.append(f"[{i}] {emoji} {status} (Confidence: {confidence}%)")
                    report_lines.append(f"    Claim: {claim.get('claim_text', 'Unknown')[:120]}...")
                    report_lines.append(f"    Type: {claim.get('claim_type', 'unknown')}")
                    
                    if ver_result.get('reasoning'):
                        report_lines.append(f"    Reasoning: {ver_result['reasoning'][:200]}...")
                    
                    if ver_result.get('evidence_count', 0) > 0:
                        report_lines.append(f"    Evidence Sources: {ver_result['evidence_count']} research papers")
                    
                    report_lines.append("")
    
    # Final summary
    report_lines.append("=" * 80)
    report_lines.append("VERIFICATION COMPLETE")
    report_lines.append("=" * 80)
    report_lines.append("")
    report_lines.append("💡 Tips:")
    report_lines.append("  • Review any references with validation issues")
    report_lines.append("  • Investigate contradicted or low-confidence claims")
    report_lines.append("  • Check DOIs and URLs for accessibility")
    report_lines.append("  • Cross-reference findings with original sources")
    report_lines.append("")
    
    return "\n".join(report_lines)


async def quick_verify_references(
    document_text: str,
    provider: BaseLLMProvider
) -> str:
    """
    Quick reference-only verification.
    
    Args:
        document_text: Document text to verify
        provider: LLM provider instance
        
    Returns:
        Reference validation report
    """
    logger.info("🔍 Quick reference verification (claims skipped)")
    return await verify_document_sources(
        document_text,
        provider,
        verify_claims=False,
        verify_references=True
    )


async def quick_verify_claims(
    document_text: str,
    provider: BaseLLMProvider
) -> str:
    """
    Quick claim-only verification.
    
    Args:
        document_text: Document text to verify
        provider: LLM provider instance
        
    Returns:
        Claim verification report
    """
    logger.info("🔍 Quick claim verification (references skipped)")
    return await verify_document_sources(
        document_text,
        provider,
        verify_claims=True,
        verify_references=False
    )
