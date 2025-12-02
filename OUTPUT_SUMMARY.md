# SCIgen Python - Output Summary


## Generated Files

```
output/
├── final_paper.tex    (14K)  - LaTeX source with proper formatting
├── final_paper.bib    (2.7K) - BibTeX with quality references
├── figure0.eps        (22K)  - Scientific graph (matplotlib)
├── figure1.eps        (25K)  - Scientific graph (matplotlib)
├── dia0.dot           (880B) - System diagram (Graphviz DOT)
└── dia1.dot           (571B) - System diagram (Graphviz DOT)
```

## PDF Generation

#### Option 1: Install LaTeX (Recommended)
```bash
# Full distribution (~4GB)
brew install --cask mactex

# Or minimal distribution (~100MB)
brew install --cask basictex

# Then generate PDF
cd python_based
PYTHONPATH=src python3 -m scigen.cli generate-paper \
  --seed 2025 \
  --author "Alice Johnson" \
  --author "Bob Smith" \
  --output output/paper.tex \
  --pdf
```

#### Option 2: Use Online Compiler
1. Upload `output/final_paper.tex` and `output/final_paper.bib` to:
   - **Overleaf**: https://www.overleaf.com/
   - **Papeeria**: https://papeeria.com/
2. Upload the `.eps` files to the same project
3. Compile online to get PDF

#### Option 3: Manual Compilation
```bash
cd output
pdflatex final_paper.tex
bibtex final_paper
pdflatex final_paper.tex
pdflatex final_paper.tex
```

## Diagram Files (.dot)

The `.dot` files can be converted to `.eps` using Graphviz:

```bash
# Install Graphviz
brew install graphviz

# Convert diagrams
cd output
dot -Teps dia0.dot -o dia0.eps
dot -Teps dia1.dot -o dia1.eps

# Then recompile PDF
pdflatex final_paper.tex
```

## Architecture Highlights

### Pythonic Improvements Over Perl

1. **Context Injection Pattern**
   ```python
   engine.set_context(SYSNAME="MySystem", AUTHOR_NAME=["Alice", "Bob"])
   ```
   - Cleaner than Perl's manual hash manipulation
   - Type-safe and testable
   - No grammar pollution
   - Thread-safe potential

2. **Modern Software Engineering**
   - SOLID principles
   - Full type hints
   - 33 well-organized modules
   - Clean separation of concerns

3. **Better Text Processing**
   - Fixed sentence capitalization
   - Proper article handling (a/an)
   - LaTeX-aware formatting

4. **Perl-Compatible Expansion**
   - Pattern: `^(.*?)(RULE1|RULE2|...)` (no word boundaries)
   - Recursive pattern support (NONZDIGIT, etc.)
   - Identical output to Perl for same seed

## Commands Reference

```bash
# Generate paper with all features
python -m scigen.cli generate-paper \
  --seed 2025 \
  --author "Alice" --author "Bob" \
  --output paper.tex \
  --pdf \
  --figures

# Generate without PDF (if LaTeX not installed)
python -m scigen.cli generate-paper \
  --seed 2025 \
  --author "Alice" \
  --output paper.tex

# Generate graph only
python -m scigen.cli generate-graph \
  --seed 42 \
  --output graph.eps

# Generate diagram only
python -m scigen.cli generate-diagram \
  --sysname "MySystem" \
  --seed 100 \
  --output diagram.dot
```

## Documentation

- `README.md` - Project overview and quick start
- `PYTHONIC_IMPROVEMENTS.md` - Context injection pattern details
- Code docstrings - Comprehensive API documentation


