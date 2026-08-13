import pytest
import yaml
from rune.config.exceptions import RuneError
from rune.services.mutagen_service import parse_gitignore, update_mutagen_ignore


def test_parse_gitignore_success(tmp_path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text(
        "# Comment\n"
        "__pycache__/\n"
        "\n"
        "*.py[codz]\n"
        "  \n"
        "__pycache__/\n"  # Duplicate check
        "*.so\n",
        encoding="utf-8",
    )

    patterns = parse_gitignore(gitignore)
    assert patterns == ["__pycache__/", "*.py[codz]", "*.so"]


def test_parse_gitignore_not_found(tmp_path):
    gitignore = tmp_path / ".gitignore"
    with pytest.raises(RuneError, match="file not found"):
        parse_gitignore(gitignore)


def test_update_mutagen_ignore_merges_paths_strictly_in_defaults(tmp_path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("__pycache__/\n*.so\n.env\n", encoding="utf-8")

    mutagen = tmp_path / "mutagen.yml"
    mutagen.write_text(
        yaml.dump(
            {
                "sync": {
                    "defaults": {
                        "ignore": {
                            "paths": ["__pycache__/"],
                        }
                    },
                    "session1": {
                        "ignore": {
                            "paths": ["!custom/*"],
                        }
                    },
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    updated_file, added = update_mutagen_ignore(git_root=tmp_path)
    assert updated_file == mutagen
    assert added == 2

    data = yaml.safe_load(mutagen.read_text(encoding="utf-8"))
    assert data["sync"]["defaults"]["ignore"]["paths"] == [
        "__pycache__/",
        "*.so",
        ".env",
    ]
    # Verify session1 was untouched
    assert data["sync"]["session1"]["ignore"]["paths"] == ["!custom/*"]


def test_update_mutagen_ignore_creates_defaults_when_missing(tmp_path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("build/\ndist/\n", encoding="utf-8")

    mutagen = tmp_path / "mutagen.yml"
    mutagen.write_text(yaml.dump({"sync": {}}, sort_keys=False), encoding="utf-8")

    updated_file, added = update_mutagen_ignore(git_root=tmp_path)
    assert updated_file == mutagen
    assert added == 2

    data = yaml.safe_load(mutagen.read_text(encoding="utf-8"))
    assert data["sync"]["defaults"]["ignore"]["paths"] == ["build/", "dist/"]


def test_update_mutagen_ignore_missing_mutagen_yml(tmp_path):
    gitignore = tmp_path / ".gitignore"
    gitignore.write_text("build/\n", encoding="utf-8")

    with pytest.raises(RuneError, match="mutagen.yml file not found"):
        update_mutagen_ignore(git_root=tmp_path)
