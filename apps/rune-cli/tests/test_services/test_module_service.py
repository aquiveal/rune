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

def test_add_module_local_submodule(tmp_path, mock_git_repo, mock_module_repo):
    # Arrange
    root_dir = tmp_path
    url = "https://github.com/owner/repo.git"
    path = "rules/my-rule"
    name = "my-rule"
    type = "rules"
    agents = [".roo"]
    
    # Act
    original_exists = Path.exists
    def mock_exists(self):
        if "my-rule" in str(self):
            return True
        if "repo" in str(self) and "modules" in str(self):
            return False
        return original_exists(self)
        
    with patch("pathlib.Path.exists", new=mock_exists):
        with patch("rune.services.module_service.shutil.copytree") as mock_copytree:
            with patch("rune.services.module_service.shutil.copy2") as mock_copy2:
                module_service.add_module(root_dir, root_dir, url, path, name, type, agents)
            
    # Assert
    mock_git_repo.is_git_repo.assert_called_once_with(root_dir)
    mock_git_repo.add_submodule.assert_called_once()
    mock_git_repo.sparse_checkout_init.assert_called_once()
    mock_git_repo.sparse_checkout_set.assert_called_once()
    mock_module_repo.add_module.assert_called_once()
    assert mock_copytree.called or mock_copy2.called

def test_add_module_not_git_repo(tmp_path, mock_git_repo):
    # Arrange
    mock_git_repo.is_git_repo.return_value = False
    
    # Act & Assert
    with pytest.raises(ModuleError, match="Must be run inside a git repository"):
        module_service.add_module(tmp_path, tmp_path, "url", "path", "name", "rules", [".roo"])

def test_add_module_global_clone(tmp_path, mock_git_repo, mock_module_repo):
    # Arrange
    root_dir = tmp_path
    url = "https://github.com/owner/repo.git"
    path = "rules/my-rule"
    name = "my-rule"
    type = "rules"
    agents = [".roo"]
    
    # Act
    original_exists = Path.exists
    def mock_exists(self):
        if "my-rule" in str(self):
            return True
        if "repo" in str(self) and "modules" in str(self):
            return False
        return original_exists(self)
        
    with patch("pathlib.Path.exists", new=mock_exists):
        with patch("rune.services.module_service.shutil.copytree") as mock_copytree:
            with patch("rune.services.module_service.shutil.copy2") as mock_copy2:
                module_service.add_module(root_dir, root_dir, url, path, name, type, agents, global_scope=True)
            
    # Assert
    mock_git_repo.clone.assert_called_once()
    mock_git_repo.add_submodule.assert_not_called()
    mock_git_repo.sparse_checkout_init.assert_called_once()
    mock_git_repo.sparse_checkout_set.assert_called_once()
    assert mock_copytree.called or mock_copy2.called

def test_update_modules_local(tmp_path, mock_git_repo, mock_module_repo, mock_config_repo):
    # Arrange
    mock_module_repo.list_modules.return_value = [
        ModuleSchema(name="my-rule", url="https://github.com/owner/repo.git", path="rules/my-rule", type="rules")
    ]
    
    # Act
    with patch("pathlib.Path.exists", return_value=True):
        with patch("rune.services.module_service.os.symlink"):
            module_service.update_modules(tmp_path, type="rules")
            
    # Assert
    mock_git_repo.run_git.assert_called_once()
    args = mock_git_repo.run_git.call_args[0][0]
    assert args[0] == "submodule"
    assert args[1] == "update"
    assert args[2] == "--remote"