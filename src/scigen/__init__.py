"""
SCIgen-py: Modern Python implementation of SCIgen automatic paper generator.

This package provides a comprehensive, well-architected system for generating
fake computer science research papers using context-free grammars.
"""

__version__ = "2.0.0"
__author__ = "SCIgen Team"
__license__ = "GPL-2.0-or-later"

from scigen.core.grammar import GrammarEngine
from scigen.generators.paper import PaperGenerator
from scigen.models.paper import Paper
from scigen.config import GeneratorConfig

__all__ = [
    "GrammarEngine",
    "PaperGenerator",
    "Paper",
    "GeneratorConfig",
]
