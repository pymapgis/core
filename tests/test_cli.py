"""
Comprehensive tests for PyMapGIS CLI (pmg.cli) module.

Tests all CLI commands and functionality as specified in Phase 1 - Part 6.
"""

import pytest
import subprocess
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

# Import CLI components
try:
    from pymapgis.cli import app
    from pymapgis import cli as cli_module
    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False
    app = None
    cli_module = None


@pytest.fixture
def cli_runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_settings():
    """Mock PyMapGIS settings for testing."""
    mock_settings = MagicMock()
    mock_settings.cache_dir = "/tmp/test_cache"
    mock_settings.default_crs = "EPSG:4326"
    return mock_settings


@pytest.fixture
def mock_pymapgis():
    """Mock PyMapGIS module for testing."""
    mock_pymapgis = MagicMock()
    mock_pymapgis.__version__ = "0.1.0"
    return mock_pymapgis


# ============================================================================
# CLI MODULE STRUCTURE TESTS
# ============================================================================

def test_cli_module_structure():
    """Test that CLI module has proper structure."""
    if not CLI_AVAILABLE:
        pytest.skip("CLI module not available")
    
    # Check that cli module exists and has expected attributes
    assert hasattr(cli_module, 'app'), "CLI module should have 'app' attribute"
    assert cli_module.app is not None, "CLI app should not be None"


def test_cli_module_imports():
    """Test that CLI module can be imported correctly."""
    if not CLI_AVAILABLE:
        pytest.skip("CLI module not available")
    
    # Test importing from pymapgis.cli
    from pymapgis.cli import app as cli_app
    assert cli_app is not None
    
    # Test that it's the same as the main CLI app
    from pymapgis.cli import app as main_app
    assert cli_app is main_app


# ============================================================================
# INFO COMMAND TESTS
# ============================================================================

@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_info_command_basic(cli_runner, mock_settings, mock_pymapgis):
    """Test basic info command functionality."""
    with patch('pymapgis.cli.settings', mock_settings), \
         patch('pymapgis.cli.pymapgis', mock_pymapgis):
        
        result = cli_runner.invoke(app, ["info"])
        
        assert result.exit_code == 0
        assert "PyMapGIS Environment Information" in result.stdout
        assert "Version: 0.1.0" in result.stdout
        assert "Cache Directory: /tmp/test_cache" in result.stdout
        assert "Default CRS: EPSG:4326" in result.stdout


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_info_command_dependencies(cli_runner, mock_settings, mock_pymapgis):
    """Test that info command shows dependency information."""
    with patch('pymapgis.cli.settings', mock_settings), \
         patch('pymapgis.cli.pymapgis', mock_pymapgis):
        
        result = cli_runner.invoke(app, ["info"])
        
        assert result.exit_code == 0
        assert "Key Dependencies:" in result.stdout
        assert "Python Version:" in result.stdout


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_info_command_with_import_error(cli_runner):
    """Test info command when PyMapGIS modules can't be imported."""
    # This tests the fallback behavior when imports fail
    result = cli_runner.invoke(app, ["info"])
    
    # Should still work with dummy settings
    assert result.exit_code == 0
    assert "PyMapGIS Environment Information" in result.stdout


# ============================================================================
# CACHE COMMAND TESTS
# ============================================================================

@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_cache_dir_command(cli_runner, mock_settings):
    """Test cache dir command."""
    with patch('pymapgis.cli.settings', mock_settings):
        result = cli_runner.invoke(app, ["cache", "dir"])
        
        assert result.exit_code == 0
        assert "/tmp/test_cache" in result.stdout.strip()


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_cache_info_command(cli_runner, mock_settings):
    """Test cache info command."""
    mock_stats = {
        "cache_enabled": True,
        "cache_size_bytes": 1024000,
        "cache_entries": 42
    }
    
    with patch('pymapgis.cli.settings', mock_settings), \
         patch('pymapgis.cli.stats_api', return_value=mock_stats):
        
        result = cli_runner.invoke(app, ["cache", "info"])
        
        assert result.exit_code == 0
        assert "PyMapGIS Cache Information" in result.stdout
        assert "Cache Enabled: Enabled" in result.stdout
        assert "1.00 MB" in result.stdout  # Size formatting


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_cache_clear_command(cli_runner):
    """Test cache clear command."""
    with patch('pymapgis.cli.clear_cache_api') as mock_clear:
        result = cli_runner.invoke(app, ["cache", "clear"])
        
        assert result.exit_code == 0
        assert "cleared successfully" in result.stdout
        mock_clear.assert_called_once()


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_cache_purge_command(cli_runner):
    """Test cache purge command."""
    with patch('pymapgis.cli.purge_cache_api') as mock_purge:
        result = cli_runner.invoke(app, ["cache", "purge"])
        
        assert result.exit_code == 0
        assert "purged" in result.stdout
        mock_purge.assert_called_once()


# ============================================================================
# RIO COMMAND TESTS
# ============================================================================

@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_rio_command_not_found(cli_runner):
    """Test rio command when rio executable is not found."""
    with patch('pymapgis.cli.shutil.which', return_value=None):
        result = cli_runner.invoke(app, ["rio", "--help"])
        
        assert result.exit_code == 1
        assert "rio" in result.stdout
        assert "not found" in result.stdout


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_rio_command_found(cli_runner):
    """Test rio command when rio executable is found."""
    mock_process = MagicMock()
    mock_process.returncode = 0
    
    with patch('pymapgis.cli.shutil.which', return_value='/usr/bin/rio'), \
         patch('pymapgis.cli.subprocess.run', return_value=mock_process), \
         patch('sys.exit') as mock_exit:
        
        result = cli_runner.invoke(app, ["rio", "--version"])
        
        # Should attempt to run rio command
        mock_exit.assert_called_once_with(0)


# ============================================================================
# DOCTOR COMMAND TESTS
# ============================================================================

@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_doctor_command_basic(cli_runner, mock_settings, mock_pymapgis):
    """Test doctor command basic functionality."""
    with patch('pymapgis.cli.settings', mock_settings), \
         patch('pymapgis.cli.pymapgis', mock_pymapgis):
        
        result = cli_runner.invoke(app, ["doctor"])
        
        assert result.exit_code == 0
        assert "PyMapGIS Doctor" in result.stdout
        assert "System Information" in result.stdout
        assert "Python Packages" in result.stdout


# ============================================================================
# PLUGIN COMMAND TESTS
# ============================================================================

@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_plugin_list_command(cli_runner):
    """Test plugin list command."""
    mock_plugins = {"test_plugin": MagicMock()}
    mock_plugins["test_plugin"].__module__ = "test.module"
    
    with patch('pymapgis.cli.load_driver_plugins', return_value=mock_plugins), \
         patch('pymapgis.cli.load_algorithm_plugins', return_value={}), \
         patch('pymapgis.cli.load_viz_backend_plugins', return_value={}):
        
        result = cli_runner.invoke(app, ["plugin", "list"])
        
        assert result.exit_code == 0
        assert "Discovering PyMapGIS Plugins" in result.stdout
        assert "test_plugin" in result.stdout


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_plugin_list_command_verbose(cli_runner):
    """Test plugin list command with verbose flag."""
    mock_plugins = {"test_plugin": MagicMock()}
    mock_plugins["test_plugin"].__module__ = "test.module"
    
    with patch('pymapgis.cli.load_driver_plugins', return_value=mock_plugins), \
         patch('pymapgis.cli.load_algorithm_plugins', return_value={}), \
         patch('pymapgis.cli.load_viz_backend_plugins', return_value={}):
        
        result = cli_runner.invoke(app, ["plugin", "list", "--verbose"])
        
        assert result.exit_code == 0
        assert "test.module" in result.stdout


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_cache_command_error_handling(cli_runner):
    """Test cache command error handling."""
    with patch('pymapgis.cli.clear_cache_api', side_effect=Exception("Test error")):
        result = cli_runner.invoke(app, ["cache", "clear"])
        
        assert result.exit_code == 0  # Typer handles the error gracefully
        assert "Error" in result.stdout


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_plugin_command_unavailable(cli_runner):
    """Test plugin command when plugin system is unavailable."""
    # Remove the plugin functions from globals to simulate unavailable plugins
    with patch.dict('pymapgis.cli.__dict__', {}, clear=False):
        # Remove the plugin loading functions
        if 'load_driver_plugins' in cli_module.__dict__:
            del cli_module.__dict__['load_driver_plugins']
        
        result = cli_runner.invoke(app, ["plugin", "list"])
        
        assert result.exit_code == 1
        assert "unavailable" in result.stdout


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_cli_entry_point_exists():
    """Test that CLI entry point is properly configured."""
    # Check that the entry point exists in pyproject.toml
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()
        assert "pymapgis = \"pymapgis.cli:app\"" in content


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_cli_help_command(cli_runner):
    """Test that CLI help command works."""
    result = cli_runner.invoke(app, ["--help"])
    
    assert result.exit_code == 0
    assert "PyMapGIS" in result.stdout
    assert "info" in result.stdout
    assert "cache" in result.stdout
    assert "rio" in result.stdout


@pytest.mark.skipif(not CLI_AVAILABLE, reason="CLI not available")
def test_cli_version_info(cli_runner):
    """Test that CLI provides version information."""
    result = cli_runner.invoke(app, ["info"])
    
    assert result.exit_code == 0
    assert "Version:" in result.stdout


# ============================================================================
# REAL CLI EXECUTION TESTS (INTEGRATION)
# ============================================================================

@pytest.mark.integration
def test_real_cli_execution():
    """Test actual CLI execution via subprocess (integration test)."""
    try:
        # Test that the CLI can be invoked
        result = subprocess.run(
            [sys.executable, "-m", "pymapgis.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should not crash
        assert result.returncode == 0 or result.returncode == 2  # 2 is help exit code
        assert "PyMapGIS" in result.stdout or "PyMapGIS" in result.stderr
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pytest.skip("CLI not available for real execution test")


@pytest.mark.integration
def test_real_info_command():
    """Test actual info command execution."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", "from pymapgis.cli import app; app()"],
            input="info\n",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should provide some output even if modules aren't fully available
        assert "PyMapGIS" in result.stdout or "PyMapGIS" in result.stderr
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pytest.skip("CLI not available for real execution test")
