# Quick Start Guide

## Installation

### From Source

```bash
# Clone repository
git clone <repository-url>
cd python_based

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Using Docker

```bash
# Build image
docker build -t scigen-py .

# Run
docker run -v $(pwd)/output:/output scigen-py scigen-paper --output /output/paper.tex
```

## Basic Usage

### Generate a Paper

```bash
# Simple paper with default authors
scigen-paper --output paper.tex

# With custom authors
scigen-paper --author "Neyaz" --author "Bob" --output paper.tex

# With specific seed for reproducibility
scigen-paper --seed 12345 --author "Charlie" --output paper.tex

# Generate PDF (requires pdflatex)
scigen-paper --author "Dave" --output paper.tex --pdf
```

### Generate a Graph

```bash
# Line plot
scigen-graph --output graph.eps

# Scatter plot
scigen-graph --type scatter --output scatter.png

# Bar chart in color
scigen-graph --type bar --color --output bars.pdf
```

### Generate a Diagram

```bash
# System diagram
scigen-diagram --sysname "MySystem" --output diagram.dot

# With specific number of nodes
scigen-diagram --sysname "Network" --nodes 10 --output net.dot

# Undirected graph
scigen-diagram --sysname "Cluster" --undirected --output cluster.dot

# Render to image (requires graphviz)
dot -Teps diagram.dot -o diagram.eps
```

## Python API

### Simple Example

```python
from scigen import PaperGenerator, GeneratorConfig

# Configure
config = GeneratorConfig(
    seed=42,
    authors=["Alice", "Bob"],
    pretty_print=True
)

# Generate
generator = PaperGenerator(config)
paper = generator.generate()

# Save
paper.save_latex("output/paper.tex")
paper.save_bibtex("output/paper.bib")
```

### Advanced Example

```python
from pathlib import Path
from scigen.core.grammar import GrammarEngine
from scigen.models.rules import RuleSet

# Load custom rules
ruleset = RuleSet()
engine = GrammarEngine(ruleset)
engine.load_rules(Path("my_rules.txt"))

# Generate with custom rules
title = engine.expand("CUSTOM_TITLE")
abstract = engine.expand("CUSTOM_ABSTRACT")

print(f"Title: {title}")
print(f"Abstract: {abstract}")
```

## Common Tasks

### Create Custom Grammar Rules

Create a file `custom_rules.txt`:

```
# Define your rules
GREETING Hello SUBJECT
SUBJECT world
SUBJECT universe
FAREWELL Goodbye SUBJECT
```

Use with CLI:

```bash
scigen expand --file custom_rules.txt --start GREETING
```

### Customize Output

```python
from scigen.config import GeneratorConfig

config = GeneratorConfig(
    seed=12345,
    authors=["Dr. Smith", "Prof. Jones"],
    institution="Fictional University",
    pretty_print=True,      # Enable pretty printing
    debug_level=1,          # Show debug info
    output_dir=Path("my_output")
)
```

### Generate Multiple Papers

```python
from scigen import PaperGenerator, GeneratorConfig

# Generate 10 papers with different seeds
for i in range(10):
    config = GeneratorConfig(
        seed=i,
        authors=["Author"],
        output_dir=Path(f"output/paper_{i}")
    )
    
    generator = PaperGenerator(config)
    paper = generator.generate()
    
    paper.save_latex(Path(f"output/paper_{i}/paper.tex"))
```

## Troubleshooting

### Import Errors

If you get import errors:

```bash
# Make sure package is installed
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/python_based/src"
```

### Missing Dependencies

```bash
# Install all dependencies
pip install -e ".[dev]"

# Or individually
pip install matplotlib networkx click pyyaml
```

### Rules File Not Found

Make sure the data directory exists:

```bash
ls src/scigen/data/scirules.txt
```

If missing, copy from perl_based:

```bash
cp ../perl_based/scirules.in src/scigen/data/scirules.txt
```

### PDF Generation Fails

Install LaTeX:

```bash
# Ubuntu/Debian
sudo apt-get install texlive-latex-base texlive-latex-extra

# macOS
brew install mactex

# Or use Docker
docker run -v $(pwd):/data thomasweise/docker-texlive pdflatex paper.tex
```

## Getting Help

- Open an issue on GitHub
- Check existing issues for solutions
- Read the source code (it's well-documented!)

## Tips

1. **Use seeds for reproducibility** - Same seed = same output
2. **Pretty printing** - Enabled by default for better formatting
3. **Debug mode** - Use `-d` flag for verbose output
4. **Batch generation** - Use Python API for multiple papers
5. **Custom rules** - Extend grammar for specialized content
