from genealogy_agent.tools.documents import ConfigurablePdfReader


def test_configurable_pdf_reader() -> None:
    def extractor(pdf_bytes: bytes, language_hint: str | None):
        del pdf_bytes
        return ("hola", language_hint or "es", 0.8)

    reader = ConfigurablePdfReader(extractor)
    result = reader.extract_text(b"%PDF", "es")

    assert result.text == "hola"
    assert result.language == "es"
    assert result.confidence == 0.8
