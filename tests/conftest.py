"""Test configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_rules_file(tmp_path):
    """Create a sample rules file for testing."""
    rules = tmp_path / "test_rules.txt"
    rules.write_text("""
# Sample rules for testing
START Hello WORLD
WORLD world
GREETING Hello WORLD
FAREWELL Goodbye WORLD

# Weighted rule
WEIGHTED+2 common
WEIGHTED rare

# Multiline rule
MULTI {
This is a
multiline expansion
with multiple lines
}
""")
    return rules


@pytest.fixture
def minimal_paper_config(tmp_path):
    """Create minimal configuration for paper generation."""
    from scigen.config import GeneratorConfig
    
    return GeneratorConfig(
        seed=12345,
        authors=["Test Author"],
        output_dir=tmp_path,
        debug_level=0
    )
