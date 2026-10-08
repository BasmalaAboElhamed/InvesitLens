"""
InvestiLens — Analysis Chains

LangChain orchestration for all specialized analysis tasks.
Connects prompts, LLM, and output parsers.
"""

from typing import Dict, Any, List, Optional
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from app.core.logging import logger
from app.llm.model import get_llm
from app.llm import prompts
from app.llm import parsers
from app.schemas.financial import FinancialAnalysis, TrendAnalysis
from app.schemas.risk import RiskAnalysis
from app.schemas.strategy import StrategyAnalysis, ManagementOutlook
from app.schemas.comparison import CrossYearComparison
from app.schemas.chat import ChatResponse


def run_company_analysis(company: str, context: str) -> Dict[str, Any]:
    """Execute company analysis chain."""
    llm = get_llm()
    chain = prompts.COMPANY_ANALYSIS_PROMPT | llm | StrOutputParser()
    
    logger.info(f"Running company analysis for {company}")
    response = chain.invoke({"company": company, "context": context})
    
    parsed = parsers.extract_json_from_response(response)
    if not parsed:
        logger.warning(f"Failed to parse company analysis for {company}")
        return {"company_name": company, "summary": "Analysis failed to parse."}
    return parsed


def run_financial_analysis(company: str, context: str) -> FinancialAnalysis:
    """Execute financial analysis chain."""
    llm = get_llm()
    chain = prompts.FINANCIAL_ANALYSIS_PROMPT | llm | StrOutputParser()
    
    logger.info(f"Running financial analysis for {company}")
    response = chain.invoke({"company": company, "context": context})
    
    return parsers.parse_response_or_default(response, FinancialAnalysis, company=company)


def run_trend_analysis(company: str, context: str) -> TrendAnalysis:
    """Execute trend analysis chain."""
    llm = get_llm()
    chain = prompts.TREND_ANALYSIS_PROMPT | llm | StrOutputParser()
    
    logger.info(f"Running trend analysis for {company}")
    response = chain.invoke({"company": company, "context": context})
    
    return parsers.parse_response_or_default(response, TrendAnalysis, company=company)


def run_risk_analysis(company: str, context: str) -> RiskAnalysis:
    """Execute risk analysis chain."""
    llm = get_llm()
    chain = prompts.RISK_ANALYSIS_PROMPT | llm | StrOutputParser()
    
    logger.info(f"Running risk analysis for {company}")
    response = chain.invoke({"company": company, "context": context})
    
    analysis = parsers.parse_response_or_default(response, RiskAnalysis, company=company)
    # Compute counts based on the parsed list of risks
    return analysis.compute_counts()


def run_strategy_analysis(company: str, context: str) -> StrategyAnalysis:
    """Execute strategy analysis chain."""
    llm = get_llm()
    chain = prompts.STRATEGY_ANALYSIS_PROMPT | llm | StrOutputParser()
    
    logger.info(f"Running strategy analysis for {company}")
    response = chain.invoke({"company": company, "context": context})
    
    return parsers.parse_response_or_default(response, StrategyAnalysis, company=company)


def run_management_outlook(company: str, context: str) -> ManagementOutlook:
    """Execute management outlook chain."""
    llm = get_llm()
    chain = prompts.MANAGEMENT_OUTLOOK_PROMPT | llm | StrOutputParser()
    
    logger.info(f"Running management outlook for {company}")
    response = chain.invoke({"company": company, "context": context})
    
    return parsers.parse_response_or_default(response, ManagementOutlook, company=company)


def run_comparison(company: str, periods: List[str], context: str) -> CrossYearComparison:
    """Execute cross-year comparison chain."""
    llm = get_llm()
    chain = prompts.COMPARISON_PROMPT | llm | StrOutputParser()
    
    periods_str = ", ".join(periods)
    logger.info(f"Running comparison for {company} across {periods_str}")
    response = chain.invoke({"company": company, "periods": periods_str, "context": context})
    
    return parsers.parse_response_or_default(
        response, 
        CrossYearComparison, 
        company=company, 
        periods_compared=periods
    )


def run_chat(question: str, company: str, context: str, history: str = "") -> ChatResponse:
    """Execute interactive chat chain."""
    llm = get_llm()
    chain = prompts.CHAT_PROMPT | llm | StrOutputParser()
    
    logger.info(f"Running chat for {company}: '{question[:50]}...'")
    response = chain.invoke({"company": company, "question": question, "context": context, "history": history})
    
    return parsers.parse_response_or_default(
        response, 
        ChatResponse, 
        answer="I'm sorry, I couldn't generate a structured response to that question."
    )


def classify_intent(question: str) -> str:
    """Classify the user intent of a chat question."""
    llm = get_llm()
    chain = prompts.INTENT_PROMPT | llm | StrOutputParser()
    
    logger.debug(f"Classifying intent for: '{question[:50]}...'")
    response = chain.invoke({"question": question})
    
    # Clean up response to match our expected categories
    intent = response.strip().lower()
    valid_intents = [
        "company_overview", "financial_analysis", "trend_analysis", 
        "risk_analysis", "strategy_analysis", "management_outlook", 
        "comparison", "general_document_question"
    ]
    
    for valid in valid_intents:
        if valid in intent:
            return valid
            
    return "general_document_question"


def synthesize_report(
    company: str,
    company_analysis: Dict,
    financial_analysis: FinancialAnalysis,
    trend_analysis: TrendAnalysis,
    risk_analysis: RiskAnalysis,
    strategy_analysis: StrategyAnalysis,
    management_outlook: ManagementOutlook
) -> Dict[str, Any]:
    """Synthesize the final intelligence report from all specialized analyses."""
    llm = get_llm()
    chain = prompts.REPORT_SYNTHESIS_PROMPT | llm | StrOutputParser()
    
    logger.info(f"Synthesizing final intelligence report for {company}")
    
    # We pass the JSON representations of the models to the prompt
    response = chain.invoke({
        "company": company,
        "company_analysis": company_analysis,
        "financial_analysis": financial_analysis.model_dump_json(exclude={"company"}),
        "trend_analysis": trend_analysis.model_dump_json(exclude={"company"}),
        "risk_analysis": risk_analysis.model_dump_json(exclude={"company"}),
        "strategy_analysis": strategy_analysis.model_dump_json(exclude={"company"}),
        "management_outlook": management_outlook.model_dump_json(exclude={"company"}),
    })
    
    parsed = parsers.extract_json_from_response(response)
    if not parsed:
        logger.warning(f"Failed to parse report synthesis for {company}")
        return {
            "overall_summary": "Report synthesis failed to parse correctly.",
            "executive_summary": "Error generating executive summary."
        }
        
    return parsed
