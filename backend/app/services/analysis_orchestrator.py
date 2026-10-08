"""
InvestiLens — Analysis Orchestrator Service

Manages the execution of the full analysis pipeline as a background task.
Coordinates retrieval, LLM generation, and report synthesis.
"""

import asyncio
import traceback
from datetime import datetime
from typing import List

from app.core.logging import logger
from app.models.analysis import Analysis, AnalysisStatus
from app.services import db_service
from app.rag.retriever import retrieve_for_analysis
from app.rag.context_builder import build_context
from app.llm import chains


async def run_analysis_pipeline(analysis_id: str, company_name: str, years: List[int] = None):
    """
    Execute the full intelligence analysis pipeline.
    Intended to be run as a background task.
    """
    analysis = db_service.get_analysis(analysis_id)
    if not analysis:
        logger.error(f"Analysis {analysis_id} not found to run pipeline")
        return

    try:
        # Step 1: Initialization
        db_service.update_analysis(analysis_id, {
            "status": AnalysisStatus.ANALYZING,
            "progress": 5,
            "current_step": "Retrieving context..."
        })
        logger.info(f"Starting analysis pipeline {analysis_id} for {company_name}")

        # Step 2: Retrieve Broad Context
        # In a more advanced version, each agent might do its own retrieval.
        # For this MVP, we retrieve a large, robust context block once.
        broad_queries = [
            f"{company_name} business model, products, and overview",
            f"{company_name} financial performance, revenue, profit, cash flow",
            f"{company_name} strategic priorities, investments, R&D",
            f"{company_name} risks, threats, competition, regulation",
            f"{company_name} management outlook, future expectations"
        ]

        chunks = retrieve_for_analysis(
            queries=broad_queries,
            company=company_name,
            years=years,
            top_k_per_query=5
        )

        context = build_context(chunks)

        if not chunks:
            raise ValueError(f"No documents found for {company_name}. Cannot perform analysis.")

        db_service.update_analysis(analysis_id, {
            "progress": 20,
            "current_step": "Analyzing company overview..."
        })

        # Step 3: Company Analysis
        # Yield to event loop between heavy calls
        await asyncio.sleep(0.1)
        company_analysis = chains.run_company_analysis(company_name, context)

        db_service.update_analysis(analysis_id, {
            "company_analysis": company_analysis,
            "progress": 35,
            "current_step": "Analyzing financial performance..."
        })

        # Step 4: Financial Analysis
        await asyncio.sleep(0.1)
        financial_analysis = chains.run_financial_analysis(company_name, context)

        db_service.update_analysis(analysis_id, {
            "financial_analysis": financial_analysis.model_dump(),
            "progress": 50,
            "current_step": "Analyzing business risks..."
        })

        # Step 5: Risk Analysis
        await asyncio.sleep(0.1)
        risk_analysis = chains.run_risk_analysis(company_name, context)

        db_service.update_analysis(analysis_id, {
            "risk_analysis": risk_analysis.model_dump(),
            "progress": 65,
            "current_step": "Analyzing strategic priorities..."
        })

        # Step 6: Strategy Analysis
        await asyncio.sleep(0.1)
        strategy_analysis = chains.run_strategy_analysis(company_name, context)

        db_service.update_analysis(analysis_id, {
            "strategy_analysis": strategy_analysis.model_dump(),
            "progress": 75,
            "current_step": "Analyzing management outlook..."
        })

        # Step 7: Management Outlook
        await asyncio.sleep(0.1)
        management_outlook = chains.run_management_outlook(company_name, context)

        db_service.update_analysis(analysis_id, {
            "management_outlook": management_outlook.model_dump(),
            "progress": 85,
            "current_step": "Synthesizing final intelligence report..."
        })

        # Optional Step 8: Cross-Year Comparison
        comparison_analysis = None
        if years and len(years) > 1:
            await asyncio.sleep(0.1)
            periods = [str(y) for y in sorted(years)]
            comparison = chains.run_comparison(company_name, periods, context)
            comparison_analysis = comparison.model_dump()
            db_service.update_analysis(analysis_id, {
                "comparison_analysis": comparison_analysis
            })

        # Step 9: Report Synthesis
        await asyncio.sleep(0.1)
        report = chains.synthesize_report(
            company=company_name,
            company_analysis=company_analysis,
            financial_analysis=financial_analysis,
            trend_analysis=chains.TrendAnalysis(company=company_name), # Simple mock for MVP if no strict trend engine
            risk_analysis=risk_analysis,
            strategy_analysis=strategy_analysis,
            management_outlook=management_outlook
        )

        db_service.update_analysis(analysis_id, {
            "report": report,
            "status": AnalysisStatus.COMPLETED,
            "progress": 100,
            "current_step": "Analysis complete",
            "completed_at": datetime.utcnow()
        })

        logger.info(f"Successfully completed analysis {analysis_id}")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Analysis {analysis_id} failed: {error_msg}")
        logger.error(traceback.format_exc())

        db_service.update_analysis(analysis_id, {
            "status": AnalysisStatus.FAILED,
            "error_message": error_msg,
            "completed_at": datetime.utcnow()
        })
