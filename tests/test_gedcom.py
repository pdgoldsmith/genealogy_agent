from genealogy_agent.tools import parse_gedcom


def test_parse_gedcom_basic_tree() -> None:
    text = """0 @I1@ INDI
1 NAME Ada /Lovelace/
1 SEX F
0 @F1@ FAM
1 HUSB @I2@
1 WIFE @I1@
"""
    roots = parse_gedcom(text)
    assert len(roots) == 2
    assert roots[0].tag == "INDI"
    assert roots[0].children[0].tag == "NAME"
