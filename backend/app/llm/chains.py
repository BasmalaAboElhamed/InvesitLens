"""
InvestiLens — Analysis Chains

LangChain orchestration for all specialized analysis tasks.
Connects prompts, LLM, and output parsers.

Every task follows the same flow:
    prompt template  ->  LLM  ->  raw text  ->  parse JSON  ->  result
"""

from typing import Dict, Any, List, Callable
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

# Intent categories the classifier may return. The order matters: the first
# category found inside the LLM's answer is the one that is used.
VALID_INTENTS = [
    "company_overview",
    "financial_analysis",
    "trend_analysis",
    "risk_analysis",
    "strategy_analysis",
    "management_outlook",
    "comparison",
    "general_document_question",
]
DEFAULT_INTENT = "general_document_question"


def _invoke_chain(
    prompt,
    variables: Dict[str, Any],
    log_message: str,
    log: Callable[[str], None] = logger.info,
) -> str:
    """
    Run `prompt -> LLM -> text` once and return the model's raw text answer.

    Args:
        prompt: The PromptTemplate to fill in
        variables: Values for the prompt's placeholders
        log_message: Message logged just before the LLM is called
        log: Logger method used for `log_message` (info by default)
    """
    llm = get_llm()
    chain = prompt | llm | StrOutputParser()

    log(log_message)
    return chain.invoke(variables)


# ─────────────────────────────────────────────────────────
# Specialized analyses
# ─────────────────────────────────────────────────────────

def run_company_analysis(company: str, context: str) -> Dict[str, Any]:
    """Execute company analysis chain. Returns a plain dict (not a schema model)."""
    response = _invoke_chain(
        prompts.COMPANY_ANALYSIS_PROMPT,
        {"company": company, "context": context},
        f"Running company analysis for {company}",
    )

    parsed = parsers.extract_json_from_response(response)
    if not parsed:
        logger.warning(f"Failed to parse company analysis for {company}")
        return {"company_name": company, "summary": "Analysis failed to parse."}
    return parsed


def run_financial_analysis(company: str, context: str) -> FinancialAnalysis:
    """Execute financial analysis chain."""
    response = _invoke_chain(
        prompts.FINANCIAL_ANALYSIS_PROMPT,
        {"company": company, "context": context},
        f"Running financial analysis for {company}",
    )

    return parsers.parse_response_or_default(response, FinancialAnalysis, company=company)


def run_trend_analysis(company: str, context: str) -> TrendAnalysis:
    """Execute trend analysis chain."""
    response = _invoke_chain(
        prompts.TREND_ANALYSIS_PROMPT,
        {"company": company, "context": context},
        f"Running trend analysis for {company}",
    )

    return parsers.parse_response_or_default(response, TrendAnalysis, company=company)


def run_risk_analysis(company: str, context: str) -> RiskAnalysis:
    """Execute risk analysis chain."""
    response = _invoke_chain(
        prompts.RISK_ANALYSIS_PROMPT,
        {"company": company, "context": context},
        f"Running risk analysis for {company}",
    )

    analysis = parsers.parse_response_or_default(response, RiskAnalysis, company=company)
    # Compute counts based on the parsed list of risks
    return analysis.compute_counts()


def run_strategy_analysis(company: str, context: str) -> StrategyAnalysis:
    """Execute strategy analysis chain."""
    response = _invoke_chain(
        prompts.STRATEGY_ANALYSIS_PROMPT,
        {"company": company, "context": context},
        f"Running strategy analysis for {company}",
    )

    return parsers.parse_response_or_default(response, StrategyAnalysis, company=company)


def run_management_outlook(company: str, context: str) -> ManagementOutlook:
    """Execute management outlook chain."""
    response = _invoke_chain(
        prompts.MANAGEMENT_OUTLOOK_PROMPT,
        {"company": company, "context": context},
        f"Running management outlook for {company}",
    )

    return parsers.parse_response_or_default(response, ManagementOutlook, company=company)


def run_comparison(company: str, periods: List[str], context: str) -> CrossYearComparison:
    """Execute cross-year comparison chain."""
    periods_str = ", ".join(periods)

    response = _invoke_chain(
        prompts.COMPARISON_PROMPT,
        {"company": company, "periods": periods_str, "context": context},
        f"Running comparison for {company} across {periods_str}",
    )

    return parsers.parse_response_or_default(
        response,
        CrossYearComparison,
        company=company,
        periods_compared=periods,
    )


# ─────────────────────────────────────────────────────────
# Chat
# ─────────────────────────────────────────────────────────

def run_chat(question: str, company: str, context: str, history: str = "") -> ChatResponse:
    """Execute interactive chat chain."""
    response = _invoke_chain(
        prompts.CHAT_PROMPT,
        {"company": company, "question": question, "context": context, "history": history},
        f"Running chat for {company}: '{question[:50]}...'",
    )

    return parsers.parse_response_or_default(
        response,
        ChatResponse,
        answer="I'm sorry, I couldn't generate a structured response to that question.",
    )


def classify_intent(question: str) -> str:
    """Classify the user intent of a chat question (always returns one of VALID_INTENTS)."""
    response = _invoke_chain(
        prompts.INTENT_PROMPT,
        {"question": question},
        f"Classifying intent for: '{question[:50]}...'",
        log=logger.debug,
    )

    # Clean up response to match our expected categories
    answer = response.strip().lower()

    for intent in VALID_INTENTS:
        if intent in answer:
            return intent

    return DEFAULT_INTENT


# ─────────────────────────────────────────────────────────
# Final report
# ─────────────────────────────────────────────────────────

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
    # The analysis models are passed to the prompt as JSON (without the repeated company field)
    response = _invoke_chain(
        prompts.REPORT_SYNTHESIS_PROMPT,
        {
            "company": company,
            "company_analysis": company_analysis,
            "financial_analysis": financial_analysis.model_dump_json(exclude={"company"}),
            "trend_analysis": trend_analysis.model_dump_json(exclude={"company"}),
            "risk_analysis": risk_analysis.model_dump_json(exclude={"company"}),
            "strategy_analysis": strategy_analysis.model_dump_json(exclude={"company"}),
            "management_outlook": management_outlook.model_dump_json(exclude={"company"}),
        },
        f"Synthesizing final intelligence report for {company}",
    )

    parsed = parsers.extract_json_from_response(response)
    if not parsed:
        logger.warning(f"Failed to parse report synthesis for {company}")
        return {
            "overall_summary": "Report synthesis failed to parse correctly.",
            "executive_summary": "Error generating executive summary."
        }

    return parsed
