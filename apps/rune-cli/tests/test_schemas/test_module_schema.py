import pytest
from rune.schemas.module_schema import ModuleSchema

def test_module_schema_properties():
    # Test specific_url parsing
    mod1 = ModuleSchema(name="test", url="https://github.com/a/b.git/tree/main/src", path=".")
    assert mod1.specific_url == "https://github.com/a/b.git/tree/main/src"
    
    mod2 = ModuleSchema(name="test", url="https://github.com/a/b.git main", path=".")
    assert mod2.specific_url == "https://github.com/a/b.git"
    
    # Test base_url parsing
    assert mod1.base_url == "https://github.com/a/b.git"
    assert mod2.base_url == "main"  # Space parsing behavior in schema
    
    # Test source_path parsing
    assert mod1.source_path == "src"

def test_module_schema_inferred_type():
    # Absolute paths
    assert ModuleSchema(name="x", url="y", path="/modules/foo").inferred_type == "modules"
    assert ModuleSchema(name="x", url="y", path="/rules/foo").inferred_type == "rules"
    assert ModuleSchema(name="x", url="y", path="/skills/foo").inferred_type == "skills"
    
    # Relative paths (new behavior)
    assert ModuleSchema(name="x", url="y", path="modules/python-logging").inferred_type == "modules"
    assert ModuleSchema(name="x", url="y", path="rules/test").inferred_type == "rules"
    assert ModuleSchema(name="x", url="y", path="skills/test").inferred_type == "skills"
    
    # Nested relative paths
    assert ModuleSchema(name="x", url="y", path=".agents/skills/python-logging").inferred_type == "skills"
    
    # Unknown
    assert ModuleSchema(name="x", url="y", path="foo/bar").inferred_type == "unknown"
