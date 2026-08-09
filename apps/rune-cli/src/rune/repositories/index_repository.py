import json
from pathlib import Path

from rune.config.exceptions import ConfigError
from rune.schemas.index_schema import IndexItemSchema, IndexManifestSchema

__all__ = [
    "get_items_by_scope",
    "get_items_by_type",
    "load_index",
    "record_item",
    "save_index",
]


def _get_index_path(root_dir: Path) -> Path:
    return root_dir / ".rune" / "index"


def load_index(root_dir: Path) -> IndexManifestSchema:
    index_path = _get_index_path(root_dir)
    if not index_path.exists():
        return IndexManifestSchema()

    try:
        content = index_path.read_text(encoding="utf-8").strip()
        if not content:
            return IndexManifestSchema()
        data = json.loads(content)
        return IndexManifestSchema.model_validate(data)
    except Exception:  # noqa: BLE001
        # Fallback to empty manifest if unparseable
        return IndexManifestSchema()


def save_index(root_dir: Path, manifest: IndexManifestSchema) -> None:
    index_path = _get_index_path(root_dir)
    try:
        index_path.parent.mkdir(parents=True, exist_ok=True)
        data = manifest.model_dump(exclude_none=True, mode="json")
        index_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        raise ConfigError(f"Failed to save index file '{index_path}': {e}")


def record_item(root_dir: Path, item: IndexItemSchema) -> None:
    manifest = load_index(root_dir)
    key = f"{item.item_type}:{item.name}"
    manifest.items[key] = item
    save_index(root_dir, manifest)


def get_items_by_scope(root_dir: Path, scope: str) -> list[IndexItemSchema]:
    manifest = load_index(root_dir)
    return [item for item in manifest.items.values() if item.origin_scope == scope]


def get_items_by_type(root_dir: Path, item_type: str) -> list[IndexItemSchema]:
    manifest = load_index(root_dir)
    return [item for item in manifest.items.values() if item.item_type == item_type]
