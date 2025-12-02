# SCIgen-py Architecture

## Overview

SCIgen-py is a complete redesign of the SCIgen paper generator using modern Python best practices. The architecture follows SOLID principles and emphasizes modularity, testability, and maintainability.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ CLI (click)  │  │ Python API   │  │ Future: Web  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            PaperGenerator (Orchestrator)              │  │
│  │  - Coordinates all generation components              │  │
│  │  - Manages generation lifecycle                       │  │
│  │  - Applies configuration                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Grammar    │  │   Figure     │  │     Text     │
│   Engine     │  │  Generators  │  │  Processors  │
│              │  │              │  │              │
│ - Rule parser│  │ - Graphs     │  │ - Formatting │
│ - Expander   │  │ - Diagrams   │  │ - LaTeX      │
│ - Counters   │  │ - Charts     │  │ - Casing     │
└──────────────┘  └──────────────┘  └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Domain Layer                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Paper    │  │   Rules    │  │   Config   │            │
│  │  Models    │  │  Models    │  │            │            │
│  │            │  │            │  │            │            │
│  │ - Paper    │  │ - Rule     │  │ - Settings │            │
│  │ - Author   │  │ - RuleSet  │  │ - Paths    │            │
│  │ - Section  │  │            │  │            │            │
│  │ - Figure   │  │            │  │            │            │
│  │ - Reference│  │            │  │            │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Logging   │  │    I/O     │  │  External  │            │
│  │            │  │            │  │  Libraries │            │
│  │ - Loguru   │  │ - File ops │  │            │            │
│  │ - Metrics  │  │ - Path mgmt│  │ - matplotlib│           │
│  │            │  │            │  │ - networkx │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Grammar Engine (`scigen.core.grammar`)

The heart of text generation. Implements context-free grammar expansion.

**Responsibilities:**
- Parse grammar rule files
- Expand rules recursively
- Handle weighted random selection
- Manage counters and references
- Support file includes
- Prevent duplicate expansions

**Key Classes:**
- `GrammarEngine`: Main engine for rule expansion
- `Rule`: Represents a single grammar rule
- `RuleSet`: Collection of rules with lookup

**Design Patterns:**
- **Strategy Pattern**: Different expansion strategies
- **Template Method**: Rule expansion algorithm
- **Singleton**: Pattern compilation cache

### 2. Paper Generator (`scigen.generators.paper`)

High-level orchestrator for paper generation.

**Responsibilities:**
- Coordinate grammar engine
- Generate paper structure (sections, references)
- Apply text processing
- Manage generation state

**Key Classes:**
- `PaperGenerator`: Full-featured paper generator
- `SimplePaperGenerator`: Minimal interface for basic use

**Design Patterns:**
- **Facade Pattern**: Simplifies complex generation
- **Builder Pattern**: Constructs paper incrementally
- **Factory Pattern**: Creates paper components

### 3. Domain Models (`scigen.models`)

Typed data structures representing paper components.

**Key Classes:**
- `Paper`: Complete paper with metadata
- `Author`: Author information
- `Section`: Paper section with subsections
- `Figure`: Figure with caption and label
- `Reference`: Bibliography entry

**Design Patterns:**
- **Data Transfer Object**: Pure data containers
- **Composite Pattern**: Nested sections

### 4. Text Processors (`scigen.processors`)

Format and prettify generated text.

**Responsibilities:**
- Fix article usage (a/an)
- Capitalize titles and sentences
- Format LaTeX commands
- Escape special characters
- Format BibTeX fields

**Key Classes:**
- `TextProcessor`: Main text formatting
- `LatexEscaper`: LaTeX special character handling

**Design Patterns:**
- **Strategy Pattern**: Different formatting strategies
- **Chain of Responsibility**: Multiple formatting passes

### 5. Figure Generators (`scigen.generators.graph`, `scigen.generators.diagram`)

Generate scientific figures and diagrams.

**Responsibilities:**
- Create matplotlib graphs (line, scatter, bar)
- Generate Graphviz diagrams
- Apply grammar-based labels
- Export multiple formats

**Key Classes:**
- `GraphGenerator`: Matplotlib-based graphs
- `DiagramGenerator`: Graphviz-based diagrams
- `GrammarBasedGraphGenerator`: Grammar + graphs

**Design Patterns:**
- **Factory Pattern**: Create different graph types
- **Builder Pattern**: Construct complex visualizations

### 6. CLI Interface (`scigen.cli`)

User-friendly command-line interface.

**Commands:**
- `generate-paper`: Full paper generation
- `generate-graph`: Graph creation
- `generate-diagram`: Diagram creation
- `expand`: Low-level grammar expansion

**Design Patterns:**
- **Command Pattern**: Each CLI command
- **Facade Pattern**: Simple interface to complex system

## Data Flow

### Paper Generation Flow

```
1. User Request
   └─> CLI or API call with configuration

2. Configuration
   └─> GeneratorConfig validates and sets up

3. Initialization
   ├─> Load grammar rules from files
   ├─> Initialize grammar engine
   └─> Prepare text processor

4. Generation
   ├─> Generate title
   ├─> Generate abstract
   ├─> Generate sections (intro, model, eval, etc.)
   ├─> Generate references
   └─> Generate figures (optional)

5. Post-Processing
   ├─> Apply pretty printing
   ├─> Format LaTeX
   └─> Fix articles and capitalization

6. Output
   ├─> Save LaTeX file
   ├─> Save BibTeX file
   └─> Optionally compile PDF
```

### Grammar Expansion Flow

```
1. Start Symbol
   └─> e.g., "SCI_TITLE"

2. Lookup Rule
   └─> Find rule in RuleSet

3. Select Expansion
   └─> Weighted random selection from options

4. Recursive Expansion
   ├─> Find embedded rule references
   ├─> Recursively expand each reference
   └─> Substitute results

5. Special Handling
   ├─> Counter (+): Increment and return
   ├─> Reference (#): Return random previous
   └─> Deduplication (!): Ensure uniqueness

6. Return Result
   └─> Fully expanded text
```

## Design Principles Applied

### SOLID Principles

1. **Single Responsibility Principle**
   - Each class has one clear purpose
   - `GrammarEngine`: Only grammar expansion
   - `TextProcessor`: Only text formatting
   - `PaperGenerator`: Only orchestration

2. **Open/Closed Principle**
   - Extensible through composition
   - New generators inherit interfaces
   - New processors can be added without modifying existing

3. **Liskov Substitution**
   - All generators follow consistent interface
   - Models are immutable and predictable

4. **Interface Segregation**
   - Small, focused interfaces
   - `SimplePaperGenerator` for basic use
   - `PaperGenerator` for full features

5. **Dependency Inversion**
   - Depend on abstractions (interfaces)
   - Configuration injected, not hardcoded
   - Grammar engine accepts RuleSet interface

### Other Principles

- **DRY (Don't Repeat Yourself)**: Shared utilities in base classes
- **YAGNI (You Aren't Gonna Need It)**: Only implement what's needed
- **Composition over Inheritance**: Prefer has-a over is-a
- **Fail Fast**: Validate early, raise clear errors
- **Explicit over Implicit**: Clear parameter names and types

## Testing Strategy

### Test Pyramid

```
        ┌─────────┐
        │   E2E   │  < 10% - Full system tests
        ├─────────┤
        │Integration│ < 20% - Component integration
        ├─────────┤
        │  Unit   │ > 70% - Individual functions
        └─────────┘
```

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test individual functions and classes
   - Mock external dependencies
   - Fast execution (<1s)
   - High coverage (>90%)

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - Use real files and data
   - Moderate execution (<10s)
   - Coverage of workflows

3. **Property-based Tests** (future)
   - Use Hypothesis for property testing
   - Test invariants and edge cases
   - Discover bugs automatically

## Configuration Management

### Hierarchy

1. **Defaults**: Sensible defaults in code
2. **Environment Variables**: System-level config
3. **Config Files**: Project-level settings
4. **CLI Arguments**: Runtime overrides
5. **API Parameters**: Programmatic control

### Configuration Sources

- `GeneratorConfig`: Main configuration dataclass
- `LogConfig`: Logging settings
- Environment variables (prefixed with `SCIGEN_`)
- Command-line flags

## Error Handling

### Strategy

1. **Fail Fast**: Validate inputs early
2. **Clear Messages**: User-friendly error messages
3. **Graceful Degradation**: Fallbacks when possible
4. **Logging**: All errors logged with context

### Exception Hierarchy

```
Exception
├── ValueError: Invalid inputs
├── FileNotFoundError: Missing files
├── RuntimeError: Runtime failures
└── Custom exceptions (future)
    ├── GrammarError
    ├── GenerationError
    └── ConfigurationError
```

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Load rules only when needed
2. **Caching**: Compile regex patterns once
3. **Efficient Data Structures**: Use sets for lookups
4. **Minimize I/O**: Batch file operations

### Benchmarks

Target performance (compared to Perl):
- Rule loading: ~100ms
- Paper generation: ~500ms
- Total end-to-end: <2s

## Future Enhancements

### Planned Features

1. **ML Integration**
   - Use GPT/BERT for more realistic text
   - Generate coherent paragraphs
   - Improve citation relevance

2. **Web Interface**
   - Flask/FastAPI REST API
   - React frontend
   - Real-time generation

3. **Enhanced Figures**
   - More graph types
   - Deep learning for figure generation
   - SVG support

4. **Multi-language**
   - Support non-English papers
   - Localized grammar rules

5. **Analysis Tools**
   - Paper quality metrics
   - Plagiarism detection
   - Citation graph analysis

## Comparison with Perl Version

| Aspect | Perl Version | Python Version |
|--------|-------------|----------------|
| Architecture | Procedural | Object-oriented |
| Type Safety | None | Full (mypy) |
| Testing | Minimal | Comprehensive |
| Documentation | Basic | Extensive |
| Modularity | Monolithic | Highly modular |
| Extensibility | Limited | Designed for extension |
| Performance | Fast | Comparable |
| Maintainability | Difficult | Easy |

## Conclusion

SCIgen-py represents a complete architectural overhaul while maintaining feature parity with the original. The design emphasizes:

- **Maintainability**: Clean code, clear structure
- **Testability**: High coverage, isolated components
- **Extensibility**: Easy to add features
- **Reliability**: Type safety, error handling
- **Performance**: Optimized critical paths

This architecture provides a solid foundation for future enhancements while serving current needs effectively.
