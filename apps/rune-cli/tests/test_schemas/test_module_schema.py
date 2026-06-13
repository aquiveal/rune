import pytest
from rune.schemas.module_schema import ModuleSchema

def test_module_schema_properties():
    schema = ModuleSchema(
        name=".agents/rules/language-python",
        path=".agents/rules/language-python",
        url="https://github.com/aquiveal/rune/tree/main/rules/language-python https://github.com/aquiveal/rune.git"
    )
    
    assert schema.specific_url == "https://github.com/aquiveal/rune/tree/main/rules/language-python"
    assert schema.base_url == "https://github.com/aquiveal/rune.git"
    assert schema.source_path == "rules/language-python"
    assert schema.inferred_type == "rules"

def test_module_schema_properties_single_url():
    schema = ModuleSchema(
        name=".agents/skills/my-skill",
        path=".agents/skills/my-skill",
        url="https://github.com/aquiveal/rune.git"
    )
    
    assert schema.specific_url == "https://github.com/aquiveal/rune.git"
    assert schema.base_url == "https://github.com/aquiveal/rune.git"
    assert schema.source_path == ""
    assert schema.inferred_type == "skills"

def test_module_schema_inferred_type_unknown():
    schema = ModuleSchema(
        name=".agents/other/my-module",
        path=".agents/other/my-module",
        url="https://github.com/aquiveal/rune.git"
    )
    
    assert schema.inferred_type == "unknown"
