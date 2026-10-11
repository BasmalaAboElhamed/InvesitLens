"""
InvestiLens — Reports API
"""

from fastapi import APIRouter, HTTPException
from typing import Any, Dict

from app.schemas.report import IntelligenceReport
from app.services import db_service

router = APIRouter()

# Report fields that must be plain text. The LLM sometimes returns a list or an
# object for these, which would make validation fail, so they are converted.
TEXT_FIELDS = [
    "executive_summary", "company_overview", "business_model",
    "products_and_services", "market_presence", "financial_performance",
    "overall_summary",
]


def _as_text(value: Any) -> Any:
    """Turn lists/objects returned by the LLM into readable text."""
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    return str(value)


def assemble_report(analysis) -> Dict[str, Any]:
    """
    Build the full report from a finished analysis.

    The LLM only writes the narrative parts (summary, business model...).
    Everything else (company name, metrics, risks, indicators...) comes from
    the structured results stored on the analysis itself, so the report page
    can show them and the response always passes validation.
    """
    report = dict(analysis.report or {})
    for field in TEXT_FIELDS:
        if field in report:
            report[field] = _as_text(report[field])

    financial = analysis.financial_analysis or {}
    risk = analysis.risk_analysis or {}
    strategy = analysis.strategy_analysis or {}
    outlook = analysis.management_outlook or {}
    trends = analysis.trend_analysis or {}

    # `setdefault`: never overwrite something the LLM report already contains
    report.setdefault("company", analysis.company_name)
    if analysis.completed_at:
        report.setdefault("generated_at", analysis.completed_at.isoformat())
    report.setdefault("financial_insights", financial.get("insights", []))
    report.setdefault("performance_trends", trends.get("trends", []))
    report.setdefault("positive_indicators", financial.get("positive_indicators", []))
    report.setdefault("warning_indicators", financial.get("warning_indicators", []))
    report.setdefault("key_risks", risk.get("risks", []))
    report.setdefault("strategic_outlook", strategy.get("strategies", []))
    if outlook.get("outlook_summary"):
        report.setdefault("management_outlook", _as_text(outlook["outlook_summary"]))
    if analysis.comparison_analysis:
        report.setdefault("cross_year_comparison", analysis.comparison_analysis)

    return report


@router.get("/{analysis_id}", response_model=IntelligenceReport)
def get_report(analysis_id: str):
    """
    Get the synthesized intelligence report for a completed analysis.
    """
    analysis = db_service.get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    if analysis.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Report not available. Analysis status is: {analysis.status}"
        )
        
    if not analysis.report:
        raise HTTPException(status_code=404, detail="Report generation failed or is missing")
        
    # We parse the dict back into the Pydantic model for validation
    try:
        report = IntelligenceReport.model_validate(assemble_report(analysis))
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate report: {e}")