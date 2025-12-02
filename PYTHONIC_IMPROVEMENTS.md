# Pythonic Improvements to SCIgen - Context Injection System

## Problem: Perl's Manual Rule Injection
The Perl version manually injects dynamic values by modifying the rules hash:
```perl
my @a = ($sysname);
$tex_dat->{"SYSNAME"} = \@a;  # Manually inject into rules
```

## Solution: Pythonic Context Injection

### Design Pattern: Separation of Concerns
```python
# Clean separation: Grammar rules (static) vs Runtime context (dynamic)
engine.set_context(
    SYSNAME="FuzzyNet",           # System name
    AUTHOR_NAME=["Alice", "Bob"],  # Author list
    INSTITUTION="MIT"              # Custom variables
)
```

### Implementation

#### 1. Grammar Engine Enhancement
```python
class GrammarEngine:
    def __init__(self, ...):
        self.context: Dict[str, List[str]] = {}  # Runtime context
    
    def set_context(self, **variables) -> None:
        """Inject runtime variables (Pythonic improvement)."""
        for name, value in variables.items():
            self.context[name] = [value] if isinstance(value, str) else value
    
    def _expand_internal(self, start_symbol: str, ...) -> str:
        # Check context FIRST - overrides static rules
        if start_symbol in self.context:
            return random.choice(self.context[start_symbol])
        # Then check static grammar rules
        ...
```

#### 2. Paper Generator Usage
```python
def generate(self) -> Paper:
    # Generate dynamic values
    system_name = self._generate_system_name()  # e.g., "FuzzyNet"
    
    # Inject as context (clean, temporary)
    self.engine.set_context(
        SYSNAME=system_name,
        AUTHOR_NAME=self.config.authors
    )
    
    # Generate paper (automatically uses context)
    title = self._generate_title()
    sections = self._generate_sections()
    references = self._generate_references()  # Each gets unique SYSNAME
    
    return Paper(...)
```

#### 3. Per-Reference System Names
```python
def _generate_references(self) -> List[Reference]:
    for i in range(num_refs):
        # Generate unique system name for THIS reference
        ref_sysname = self._generate_system_name()
        
        # Temporarily override context for this reference
        self.engine.set_context(SYSNAME=ref_sysname)
        
        # Expand using the new context
        bibtex_entry = self.engine.expand("BIBTEX_ENTRY")
```

## Benefits of Pythonic Approach

### ✅ Clean Architecture
- **Separation**: Grammar (static) vs Data (runtime)
- **Scoped**: Context is temporary, doesn't pollute rules
- **Reusable**: Same engine, different contexts

### ✅ Better Design Patterns
- **Strategy Pattern**: Different contexts = different behaviors
- **Dependency Injection**: Values injected at runtime
- **Immutability**: Original grammar rules never modified

### ✅ Enhanced Capabilities
```python
# Dynamic per-item customization
for paper in papers:
    engine.set_context(
        SYSNAME=paper.system_name,
        AUTHOR_NAME=paper.authors,
        YEAR=paper.year
    )
    content = engine.expand("PAPER_TEMPLATE")
    engine.clear_context()  # Clean slate for next paper
```

### ✅ Type Safety & IDE Support
```python
# Modern Python with type hints
def set_context(self, **variables: str | List[str]) -> None:
    """Full type checking and autocomplete support"""
```

### ✅ Testability
```python
def test_context_override():
    engine = GrammarEngine(ruleset)
    engine.set_context(DIGIT="X")
    assert engine.expand("DIGIT") == "X"
    
    engine.clear_context()
    assert engine.expand("DIGIT") in "0123456789"
```

## Comparison

| Aspect | Perl Approach | Python Approach |
|--------|---------------|-----------------|
| **Method** | Manual rule injection | Context injection pattern |
| **Cleanup** | Manual deletion | Automatic with `clear_context()` |
| **Scope** | Global rules hash | Scoped context dictionary |
| **Type Safety** | None | Full type hints |
| **Testability** | Hard to isolate | Easy to test |
| **Reusability** | Must reset manually | Context per-use |
| **Thread Safety** | Not thread-safe | Thread-local possible |
| **Extensibility** | Limited | Infinite variables |


## Conclusion

The Pythonic context injection approach is:
- **More elegant**: Clean separation of concerns
- **More powerful**: Infinite extensibility  
- **More maintainable**: Clear, testable code
- **More Pythonic**: Leverages modern Python features

This demonstrates how migrating from Perl to Python isn't just about translation - it's about **reimagining the architecture** using modern best practices.
