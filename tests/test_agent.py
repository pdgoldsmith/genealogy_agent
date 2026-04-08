from genealogy_agent import AgentConfig, GenealogyAgent
from genealogy_agent.models import Discovery
from genealogy_agent.providers import OpenAIBackend
from genealogy_agent.tools import ConfigurablePdfReader, DictMCPClient, HistoricalContext, WebBrowserTool


class DummyWeb(WebBrowserTool):
    def fetch(self, url: str, max_chars: int = 4000):  # type: ignore[override]
        return super().fetch("data:text/html,<html><body>ignored</body></html>")


def fake_extractor(pdf_bytes: bytes, language_hint: str | None):
    del pdf_bytes
    return ("Johann Schmidt born 1820", language_hint or "de", 0.82)


def test_pdf_and_context_flows() -> None:
    agent = GenealogyAgent(
        backend=OpenAIBackend(),
        config=AgentConfig(human_review_threshold=0.9),
        pdf_reader=ConfigurablePdfReader(fake_extractor),
        mcp_client=DictMCPClient(
            {
                ("migration", "Hamburg", "1820-1850"): HistoricalContext(
                    topic="migration",
                    place="Hamburg",
                    period="1820-1850",
                    summary="Economic migration increased.",
                    sources=["archive:hamburg:001"],
                )
            }
        ),
    )

    result = agent.analyze_handwritten_pdf(b"%PDF", "de")
    assert result["discoveries"][0]["requires_human_review"] is True
    assert result["resources_examined"][0]["resource_type"] == "pdf"

    context = agent.historical_context("migration", "Hamburg", "1820-1850")
    assert context["summary"] == "Economic migration increased."

    d = Discovery(summary="link", confidence=0.3)
    approved = agent.approve_discovery(d, approved=True)
    assert approved.status == "verified"
