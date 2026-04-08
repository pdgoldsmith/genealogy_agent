from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .models import Citation, Discovery, ResearchLogEntry, ResourceExamined
from .providers import LLMBackend
from .tools import MCPClient, HandwrittenPdfReader, WebBrowserTool, parse_gedcom


DEFAULT_SYSTEM_RULES = """You are an expert genealogy research agent.
Rules:
1) Be evidence-driven and professionally skeptical.
2) Track every source examined and provide citations.
3) Keep hypotheses distinct from verified facts.
4) Require human review for ambiguous person or relationship matches.
5) Include uncertainty and alternative explanations explicitly.
"""


@dataclass(slots=True)
class AgentConfig:
    human_review_threshold: float = 0.80
    system_rules: str = DEFAULT_SYSTEM_RULES


@dataclass(slots=True)
class GenealogyAgent:
    backend: LLMBackend
    config: AgentConfig = field(default_factory=AgentConfig)
    web_tool: WebBrowserTool | None = None
    pdf_reader: HandwrittenPdfReader | None = None
    mcp_client: MCPClient | None = None
    logs: list[ResearchLogEntry] = field(default_factory=list)
    resources_examined: list[ResourceExamined] = field(default_factory=list)

    def analyze_gedcom_text(self, gedcom_text: str) -> dict:
        records = parse_gedcom(gedcom_text)
        citation = Citation(source_id="gedcom:input", locator="in-memory")
        self._track_resource("gedcom:input", "gedcom", "GEDCOM analyzed")
        self._log("parse_gedcom", f"Parsed {len(records)} root GEDCOM records", [citation])

        user_prompt = (
            "Analyze GEDCOM records for candidate family links, uncertainty, and missing corroboration. "
            "Return conservative conclusions and highlight low-confidence joins."
        )
        model_summary = self.backend.generate(self.config.system_rules, user_prompt)

        tentative = Discovery(
            summary="Potential relationship found from GEDCOM structure.",
            confidence=0.70,
            citations=[citation],
            requires_human_review=True,
            status="hypothesis",
        )
        return self._response(len(records), model_summary, [tentative])

    def analyze_handwritten_pdf(self, pdf_bytes: bytes, language_hint: str | None = None) -> dict:
        if not self.pdf_reader:
            raise RuntimeError("No PDF reader configured")
        extracted = self.pdf_reader.extract_text(pdf_bytes, language_hint)
        citation = Citation(source_id=extracted.document_id, locator="ocr:text", note=extracted.language)
        self._track_resource(extracted.document_id, "pdf", "Handwritten PDF extracted")
        self._log("extract_pdf", f"Extracted text confidence={extracted.confidence:.2f}", [citation])

        model_summary = self.backend.generate(
            self.config.system_rules,
            "Summarize genealogy-relevant facts, persons, dates, and places from extracted handwriting.",
        )
        discovery = Discovery(
            summary="Extracted candidate entities from handwritten PDF.",
            confidence=extracted.confidence,
            citations=[citation],
            requires_human_review=extracted.confidence < self.config.human_review_threshold,
            status="hypothesis",
        )
        return self._response(1, model_summary, [discovery])

    def browse_source(self, url: str) -> dict:
        if not self.web_tool:
            raise RuntimeError("No web tool configured")
        page = self.web_tool.fetch(url)
        citation = Citation(source_id=url, locator="web:excerpt", note=page.title)
        self._track_resource(url, "webpage", f"Fetched page titled '{page.title}'")
        self._log("browse", f"Collected {len(page.text_excerpt)} chars", [citation])
        return {"url": page.url, "title": page.title, "excerpt": page.text_excerpt}

    def historical_context(self, topic: str, place: str, period: str) -> dict:
        if not self.mcp_client:
            raise RuntimeError("No MCP client configured")
        context = self.mcp_client.get_context(topic=topic, place=place, period=period)
        citations = [Citation(source_id=s, locator="mcp:source") for s in context.sources]
        self._track_resource(f"mcp:{topic}:{place}:{period}", "mcp_context", "Historical context lookup")
        self._log("historical_context", context.summary, citations)
        return {
            "topic": context.topic,
            "place": context.place,
            "period": context.period,
            "summary": context.summary,
            "sources": context.sources,
        }

    def approve_discovery(self, discovery: Discovery, approved: bool) -> Discovery:
        if discovery.confidence < self.config.human_review_threshold:
            discovery.requires_human_review = True
        if approved:
            discovery.requires_human_review = False
            discovery.status = "verified"
            self._log("human_review", f"Approved: {discovery.summary}", discovery.citations)
        else:
            discovery.status = "rejected"
            self._log("human_review", f"Rejected: {discovery.summary}", discovery.citations)
        return discovery

    def _response(self, record_count: int, model_summary: str, discoveries: list[Discovery]) -> dict:
        return {
            "record_count": record_count,
            "model_summary": model_summary,
            "discoveries": [
                {
                    "summary": d.summary,
                    "confidence": d.confidence,
                    "requires_human_review": d.requires_human_review,
                    "status": d.status,
                }
                for d in discoveries
            ],
            "resources_examined": [
                {
                    "resource_id": r.resource_id,
                    "resource_type": r.resource_type,
                    "accessed_at": r.accessed_at.isoformat(),
                    "notes": r.notes,
                }
                for r in self.resources_examined
            ],
            "logs": [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "action": entry.action,
                    "detail": entry.detail,
                }
                for entry in self.logs
            ],
        }

    def _track_resource(self, resource_id: str, resource_type: str, notes: str = "") -> None:
        self.resources_examined.append(
            ResourceExamined(
                resource_id=resource_id,
                resource_type=resource_type,
                accessed_at=datetime.utcnow(),
                notes=notes,
            )
        )

    def _log(self, action: str, detail: str, citations: list[Citation] | None = None) -> None:
        self.logs.append(
            ResearchLogEntry(
                timestamp=datetime.utcnow(),
                action=action,
                detail=detail,
                citations=citations or [],
            )
        )
