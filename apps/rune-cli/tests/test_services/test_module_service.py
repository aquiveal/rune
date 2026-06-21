import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from rune.services import module_service
from rune.config.exceptions import ModuleError
from rune.schemas.module_schema import ModuleSchema

@pytest.fixture
def mock_git_repo():
    with patch("rune.services.module_service.git_repository") as mock:
        mock.is_git_repo.return_value = True
        yield mock

@pytest.fixture
def mock_module_repo():
    with patch("rune.services.module_service.module_repository") as mock:
        yield mock

@pytest.fixture
def mock_config_repo():
    with patch("rune.services.module_service.config_repository") as mock:
        mock.get_agent_names.return_value = [".roo"]
        yield mock

def test_add_module_local_clone(tmp_path, mock_git_repo, mock_module_repo):
    # Arrange
    root_dir = tmp_path
    url = "https://github.com/owner/repo.git"
    path = "rules/my-rule"
    name = "my-rule"
    type = "rules"
    agents = [".roo"]
    
    mock_git_repo.get_default_branch.return_value = "main"
    
    # Act
    original_exists = Path.exists
    def mock_exists(self):
        if "my-rule" in str(self):
            return True
        if "repo" in str(self) and "modules" in str(self):
            return False
        return original_exists(self)
        
    original_is_dir = Path.is_dir
    def mock_is_dir(self):
        # Only mock is_dir for the source_path
        if "repo" in str(self) and "rules" in str(self) and "my-rule" in str(self):
            return True
        return original_is_dir(self)
        
    with patch("pathlib.Path.exists", new=mock_exists):
        with patch("pathlib.Path.is_dir", new=mock_is_dir):
            with patch("rune.services.module_service.shutil.copytree") as mock_copytree:
                module_service.add_module(root_dir, root_dir, url, path, name, type, agents)
            
    # Assert
    mock_git_repo.clone.assert_called_once()
    mock_git_repo.sparse_checkout_init.assert_called_once()
    mock_git_repo.sparse_checkout_set.assert_called_once()
    mock_module_repo.add_module.assert_called_once()
    mock_copytree.assert_called_once()
    assert mock_copytree.call_args.kwargs.get("ignore_dangling_symlinks") is True

def test_add_module_global_clone(tmp_path, mock_git_repo, mock_module_repo):
    # Arrange
    root_dir = tmp_path
    url = "https://github.com/owner/repo.git"
    path = "rules/my-rule"
    name = "my-rule"
    type = "rules"
    agents = [".roo"]
    
    mock_git_repo.get_default_branch.return_value = "main"
    
    # Act
    original_exists = Path.exists
    def mock_exists(self):
        if "my-rule" in str(self):
            return True
        if "repo" in str(self) and "modules" in str(self):
            return False
        return original_exists(self)
        
    original_is_dir = Path.is_dir
    def mock_is_dir(self):
        # Only mock is_dir for the source_path
        if "repo" in str(self) and "rules" in str(self) and "my-rule" in str(self):
            return True
        return original_is_dir(self)
        
    with patch("pathlib.Path.exists", new=mock_exists):
        with patch("pathlib.Path.is_dir", new=mock_is_dir):
            with patch("rune.services.module_service.shutil.copytree") as mock_copytree:
                module_service.add_module(root_dir, root_dir, url, path, name, type, agents, global_scope=True)
            
    # Assert
    mock_git_repo.clone.assert_called_once()
    mock_git_repo.sparse_checkout_init.assert_called_once()
    mock_git_repo.sparse_checkout_set.assert_called_once()
    mock_copytree.assert_called_once()
    assert mock_copytree.call_args.kwargs.get("ignore_dangling_symlinks") is True

def test_update_modules_local(tmp_path, mock_git_repo, mock_module_repo, mock_config_repo):
    # Arrange
    mock_module_repo.list_modules.return_value = [
        ModuleSchema(name=".roo/rules/my-rule", url="https://github.com/owner/repo/tree/main/rules/my-rule https://github.com/owner/repo.git", path=".roo/rules/my-rule")
    ]
    mock_git_repo.is_git_repo.return_value = True
    
    # Act
    original_is_dir = Path.is_dir
    def mock_is_dir(self):
        if "repo" in str(self) and "rules" in str(self) and "my-rule" in str(self):
            return True
        return original_is_dir(self)

    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.is_dir", new=mock_is_dir):
            with patch("rune.services.module_service.shutil.copytree") as mock_copytree:
                # Also mock is_symlink to prevent unlink
                with patch("pathlib.Path.is_symlink", return_value=False):
                    module_service.update_modules(tmp_path, type="rules")
            
    # Assert
    assert mock_git_repo.run_git.call_count == 1
    args = mock_git_repo.run_git.call_args[0][0]
    assert args[0] == "pull"
    mock_copytree.assert_called_once()
    assert mock_copytree.call_args.kwargs.get("ignore_dangling_symlinks") is True