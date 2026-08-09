from rune.repositories import index_repository
from rune.schemas.index_schema import IndexItemSchema


def test_index_repository(tmp_path):
    # Load from empty directory
    manifest = index_repository.load_index(tmp_path)
    assert len(manifest.items) == 0

    # Record item
    item = IndexItemSchema(
        name="test-skill",
        path=".agents/skills/test-skill",
        item_type="skill",
        origin_scope="submodule:submodules/frontend",
    )
    index_repository.record_item(tmp_path, item)

    # Re-load index
    reloaded = index_repository.load_index(tmp_path)
    assert len(reloaded.items) == 1
    assert "skill:test-skill" in reloaded.items

    sub_items = index_repository.get_items_by_scope(
        tmp_path, "submodule:submodules/frontend"
    )
    assert len(sub_items) == 1
    assert sub_items[0].name == "test-skill"
