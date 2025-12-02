# SCIgen-py: Modern Python Implementation

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

A complete reimplementation of [SCIgen](https://pdos.csail.mit.edu/archive/scigen/) in modern Python with **architectural improvements** over the original Perl implementation.

## What is SCIgen?

SCIgen is an automatic paper generator that produces random Computer Science research papers, including graphs, figures, and citations. It uses a hand-written context-free grammar to form all elements of the papers.

## 🎯 Key Improvements Over Perl

This Python implementation achieves **full Perl compatibility** while introducing architectural innovations:

### **Context Injection Pattern** 
Superior to Perl's manual rule manipulation. Cleanly separates static grammar from runtime variables:
```python
engine.set_context(SYSNAME="MySystem", AUTHOR_NAME=["Alice", "Bob"])
```
- Type-safe and testable
- No grammar namespace pollution
- Automatic cleanup
- Thread-safe potential
- See [PYTHONIC_IMPROVEMENTS.md](PYTHONIC_IMPROVEMENTS.md) for details

### **Modern Software Engineering**
- 🏗️ **SOLID principles** with clean separation of concerns
- 🔍 **Type safety** with comprehensive type hints
- � **Modular design** with 33 well-organized modules
- 🧪 **Better testability** through dependency injection
- � **Clear documentation** and API structure

## Features

- **Paper Generation**: Complete LaTeX papers with abstract, introduction, methodology, evaluation, related work, and conclusions
- **Figure Generation**: Automatic creation of graphs, diagrams, and charts
- **Citation Management**: Automatic BibTeX generation
- **Customization**: Configurable authors, system names, and paper structure
- **Reproducibility**: Seed-based generation for consistent results

## Quick Start

### Installation

```bash
cd python_based
pip install -e .
```

### Generate a Paper

```bash
# Simple generation
python -m scigen.cli generate-paper --author "Alice Smith" --output paper.tex

# With multiple authors and custom seed
python -m scigen.cli generate-paper \
  --author "Alice" --author "Bob" \
  --seed 12345 \
  --output paper.tex

# Generates: paper.tex and paper.bib
```

### Python API

```python
from pathlib import Path
from scigen.core.grammar import GrammarEngine
from scigen.models.rules import RuleSet
from scigen.generators.paper import PaperGenerator
from scigen.config import GeneratorConfig

# Configure and generate
config = GeneratorConfig(seed=12345, authors=["Alice", "Bob"])
generator = PaperGenerator(config)
paper = generator.generate()

# Access components
print(paper.title)
print(paper.abstract)
for section in paper.sections:
    print(f"{section.title}: {section.content[:100]}")
```

### Using Context Injection

```python
# Set dynamic variables at runtime
engine.set_context(
    SYSNAME="FuzzyNet",          # Your system name
    AUTHOR_NAME=["Alice", "Bob"], # Author names
    CUSTOM_VAR="anything"         # Extensible!
)

# Context overrides grammar rules
title = engine.expand("SCI_TITLE")  # Uses "FuzzyNet" instead of "SYSNAME"
```

## Project Structure

```
python_based/
├── src/scigen/
│   ├── core/              # Grammar engine with context injection
│   ├── generators/        # Paper, figure, diagram generators  
│   ├── models/            # Data models (Paper, Section, Reference, etc.)
│   ├── processors/        # Text processing and LaTeX utilities
│   ├── data/              # Grammar files (scirules.txt, system_names.txt, etc.)
│   ├── config.py          # Configuration management
│   └── cli.py             # Command-line interface
├── tests/                 # Test suite
├── README.md              # This file
├── PYTHONIC_IMPROVEMENTS.md  # Context injection documentation
└── setup.py               # Package configuration
```

### Key Components

- **GrammarEngine** (`core/grammar.py`): 
  - Perl-compatible recursive expansion
  - **Context injection pattern** for runtime variables
  - Pattern matching: `^(.*?)(RULE1|RULE2|...)` (no word boundaries)
  
- **PaperGenerator** (`generators/paper.py`):
  - Orchestrates paper generation
  - Injects system names and author names via context
  - Per-reference unique system names

- **TextProcessor** (`processors/text.py`):
  - Sentence capitalization (fixes lowercase paragraph starts)
  - Article correction (a/an)
  - LaTeX formatting


## Testing

Generate and verify output quality:

```bash
# Generate test paper
python -m scigen.cli generate-paper \
  --seed 42 \
  --author "Test Author" \
  --output test_output.tex

# Check for quality issues
grep -i "sysname" test_output.tex  # Should find nothing
grep "^ [a-z]" test_output.tex     # Should find nothing (all capitalized)
```

```bash
./scigen/python_based && rm -rf output && export PATH="/Library/TeX/texbin:$PATH" && PYTHONPATH=src python3 -m scigen.cli generate-paper \
  --seed 2025 \
  --author "Alice Johnson" \
  --author "Bob Smith" \
  --output output/paper.tex \
  --pdf
```

## License

GPL v2 - Same as original SCIgen

## Credits

- Original SCIgen by Jeremy Stribling, Max Krohn, and Dan Aguayo
- Python reimplementation with architectural improvements (2024-2025)
- Context injection pattern inspired by modern dependency injection frameworks

## Documentation

- **README.md** - This file (overview and quick start)
- **PYTHONIC_IMPROVEMENTS.md** - Detailed explanation of context injection pattern
- Code documentation - Comprehensive docstrings in all modules

