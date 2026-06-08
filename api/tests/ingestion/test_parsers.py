"""
Pure unit tests for EU and UN XML parsers.

No database, no network — only inline XML strings.
"""

from src.ingestion.service import _parse_eu_xml, _parse_un_xml

# ---------------------------------------------------------------------------
# Minimal EU XML fixtures
# ---------------------------------------------------------------------------

EU_PERSON_WHOLENAME = """<?xml version="1.0" encoding="UTF-8"?>
<export>
  <sanctionEntity logicalId="EU-001">
    <entity>
      <subjectType code="P"/>
    </entity>
    <nameAlias wholeName="John DOE" strong="true"/>
    <nameAlias wholeName="Johnny DOE" strong="false"/>
  </sanctionEntity>
</export>"""

EU_PERSON_FIRSTNAME_LASTNAME = """<?xml version="1.0" encoding="UTF-8"?>
<export>
  <sanctionEntity logicalId="EU-002">
    <entity>
      <subjectType code="P"/>
    </entity>
    <nameAlias firstName="Jane" lastName="SMITH" strong="true"/>
  </sanctionEntity>
</export>"""

EU_NO_NAME = """<?xml version="1.0" encoding="UTF-8"?>
<export>
  <sanctionEntity logicalId="EU-003">
    <entity>
      <subjectType code="P"/>
    </entity>
  </sanctionEntity>
</export>"""

EU_WITH_ALIASES = """<?xml version="1.0" encoding="UTF-8"?>
<export>
  <sanctionEntity logicalId="EU-004">
    <entity>
      <subjectType code="E"/>
    </entity>
    <nameAlias wholeName="ACME Corp" strong="true"/>
    <nameAlias wholeName="ACME Ltd" strong="false"/>
    <nameAlias wholeName="ACME LLC" strong="false"/>
  </sanctionEntity>
</export>"""


# ---------------------------------------------------------------------------
# Minimal UN XML fixtures
# ---------------------------------------------------------------------------

UN_INDIVIDUAL = """<?xml version="1.0" encoding="UTF-8"?>
<CONSOLIDATED_LIST>
  <INDIVIDUALS>
    <INDIVIDUAL>
      <DATAID>123</DATAID>
      <FIRST_NAME>ALI</FIRST_NAME>
      <SECOND_NAME>HASSAN</SECOND_NAME>
      <THIRD_NAME>OMAR</THIRD_NAME>
      <FOURTH_NAME></FOURTH_NAME>
      <INDIVIDUAL_ALIAS>
        <QUALITY>Good quality</QUALITY>
        <ALIAS_NAME>A H OMAR</ALIAS_NAME>
      </INDIVIDUAL_ALIAS>
      <INDIVIDUAL_ALIAS>
        <QUALITY>Low quality</QUALITY>
        <ALIAS_NAME>Unknown alias</ALIAS_NAME>
      </INDIVIDUAL_ALIAS>
    </INDIVIDUAL>
  </INDIVIDUALS>
  <ENTITIES/>
</CONSOLIDATED_LIST>"""

UN_ENTITY = """<?xml version="1.0" encoding="UTF-8"?>
<CONSOLIDATED_LIST>
  <INDIVIDUALS/>
  <ENTITIES>
    <ENTITY>
      <DATAID>456</DATAID>
      <FIRST_NAME>TERROR FINANCE INC</FIRST_NAME>
      <ENTITY_ALIAS>
        <QUALITY>Good quality</QUALITY>
        <ALIAS_NAME>TFI</ALIAS_NAME>
      </ENTITY_ALIAS>
    </ENTITY>
  </ENTITIES>
</CONSOLIDATED_LIST>"""


# ---------------------------------------------------------------------------
# EU parser tests
# ---------------------------------------------------------------------------


def test_eu_parser_extracts_person_with_wholename() -> None:
    entries = _parse_eu_xml(EU_PERSON_WHOLENAME)
    assert len(entries) == 1
    e = entries[0]
    assert e.external_id == "EU-001"
    assert e.entity_type == "PERSON"
    assert e.primary_name == "John DOE"
    assert e.source_list == "EU"


def test_eu_parser_falls_back_to_firstname_lastname() -> None:
    entries = _parse_eu_xml(EU_PERSON_FIRSTNAME_LASTNAME)
    assert len(entries) == 1
    assert entries[0].primary_name == "Jane SMITH"


def test_eu_parser_skips_entry_with_no_name() -> None:
    entries = _parse_eu_xml(EU_NO_NAME)
    assert len(entries) == 0


def test_eu_parser_collects_aliases() -> None:
    entries = _parse_eu_xml(EU_WITH_ALIASES)
    assert len(entries) == 1
    e = entries[0]
    assert e.primary_name == "ACME Corp"
    assert e.entity_type == "ENTITY"
    assert "ACME Ltd" in e.aliases
    assert "ACME LLC" in e.aliases
    assert len(e.aliases) == 2


# ---------------------------------------------------------------------------
# UN parser tests
# ---------------------------------------------------------------------------


def test_un_parser_joins_name_parts() -> None:
    entries = _parse_un_xml(UN_INDIVIDUAL)
    persons = [e for e in entries if e.entity_type == "PERSON"]
    assert len(persons) == 1
    assert persons[0].primary_name == "ALI HASSAN OMAR"
    assert persons[0].external_id == "123"
    assert persons[0].source_list == "UN"


def test_un_parser_excludes_low_quality_aliases() -> None:
    entries = _parse_un_xml(UN_INDIVIDUAL)
    assert len(entries) == 1
    e = entries[0]
    assert "A H OMAR" in e.aliases
    assert "Unknown alias" not in e.aliases


def test_un_parser_handles_entities() -> None:
    entries = _parse_un_xml(UN_ENTITY)
    entities = [e for e in entries if e.entity_type == "ENTITY"]
    assert len(entities) == 1
    e = entities[0]
    assert e.primary_name == "TERROR FINANCE INC"
    assert e.external_id == "456"
    assert "TFI" in e.aliases
