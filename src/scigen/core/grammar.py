"""Core context-free grammar engine for SCIgen.

This module implements a robust, well-designed grammar expansion system that
serves as the heart of SCIgen's text generation.
"""

import re
import random
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path

from scigen.models.rules import Rule, RuleSet


class GrammarEngine:
    """Context-free grammar parser and expander.
    
    This engine reads grammar rules and expands them recursively to generate
    text. It supports:
    - Weighted random selection
    - Deduplication of expansions
    - File includes
    - Special counters and references
    - **Context injection for dynamic variables (Pythonic improvement)**
    - Configurable debug output
    
    Modern Pythonic Features:
    - Context variables: Inject dynamic values like system names, authors
    - Lazy rule creation: Automatically creates temporary rules from context
    - Clean separation: Grammar rules vs runtime context
    
    Attributes:
        ruleset: The loaded grammar rules.
        debug_level: Verbosity of debug output.
        counters: Dictionary of counter values for numbered expansions.
        expansion_cache: Cache of previously generated expansions (for dedup).
        context: Runtime context for dynamic variable substitution.
    """
    
    MAX_RECURSION_DEPTH = 500  # Prevent infinite recursion loops (increased for complex citations)
    
    def __init__(self, ruleset: Optional[RuleSet] = None, debug_level: int = 0):
        """Initialize the grammar engine.
        
        Args:
            ruleset: Pre-loaded ruleset. If None, must call load_rules().
            debug_level: Debug verbosity (0=none, 1=info, 2+=verbose).
        """
        self.ruleset = ruleset or RuleSet()
        self.debug_level = debug_level
        self.counters: Dict[str, int] = {}
        self.expansion_cache: Dict[str, Set[str]] = {}
        self.context: Dict[str, List[str]] = {}  # NEW: Runtime context variables
        self._recursion_depth = 0
        self._compile_pattern()
    
    def _compile_pattern(self) -> None:
        """Compile regex pattern for finding rule references.
        
        Matches the Perl implementation exactly:
        - Regex: ^(.*?)(RULE1|RULE2|...|RULEN)
        - Rules sorted by length (longest first) for greedy matching
        - No word boundaries - allows concatenated patterns like "NONZDIGIT"
        - Recursive expansion handles all nested rules automatically
        
        Counter references (RULE+ and RULE#) are handled separately in expand().
        """
        if not self.ruleset.rules:
            self._pattern = None
            return
        
        # Sort by length (longest first) to match greedily and avoid
        # partial matches (e.g., match "CITATION_SINGLE" before "CITATION")
        # This is critical - matches Perl's: sort { length ($b) <=> length ($a) }
        rule_names = sorted(self.ruleset.rules.keys(), key=len, reverse=True)
        
        # Escape special regex characters in rule names
        rules_re = "|".join(re.escape(name) for name in rule_names)
        
        # Pattern matches Perl's: qr/^(.*?)(${in})/s
        # Group 1: preamble (everything before the rule)
        # Group 2: the matched rule name
        # DOTALL flag matches Perl's /s modifier
        self._pattern = re.compile(
            rf"^(.*?)({rules_re})",
            re.DOTALL
        )
    
    def set_context(self, **variables: str | List[str]) -> None:
        """Set context variables for dynamic substitution (Pythonic improvement).
        
        Context variables are injected as temporary rules that override
        static grammar rules. This is cleaner than Perl's approach of
        manually modifying the rules hash.
        
        Args:
            **variables: Variable name to value(s) mapping.
                        Single strings are converted to single-item lists.
        
        Example:
            engine.set_context(
                SYSNAME="FuzzyNet",
                AUTHOR_NAME=["Alice", "Bob"],
                INSTITUTION="MIT"
            )
        """
        for name, value in variables.items():
            # Convert single values to lists for consistency
            if isinstance(value, str):
                value = [value]
            self.context[name] = value
    
    def clear_context(self) -> None:
        """Clear all context variables."""
        self.context.clear()
    
    def load_rules(self, file_path: Path) -> None:
        """Load grammar rules from a file.
        
        Args:
            file_path: Path to rules file.
            
        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If rules are malformed.
        """
        self._load_rules_recursive(file_path, self.ruleset)
        self._compile_pattern()
    
    def _load_rules_recursive(
        self, file_path: Path, ruleset: RuleSet, base_dir: Optional[Path] = None
    ) -> None:
        """Recursively load rules, handling includes.
        
        Args:
            file_path: Path to rules file.
            ruleset: RuleSet to populate.
            base_dir: Base directory for resolving includes.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Rules file not found: {file_path}")
        
        # Track included files to prevent duplicates
        if file_path in ruleset.included_files:
            if self.debug_level > 0:
                print(f"Skipping duplicate included file: {file_path}")
            return
        
        ruleset.included_files.add(file_path)
        
        if base_dir is None:
            base_dir = file_path.parent
        
        if self.debug_level > 0:
            print(f"Loading rules from: {file_path}")
        
        content = file_path.read_text()
        self._parse_rules(content, ruleset, base_dir)
    
    def _parse_rules(self, content: str, ruleset: RuleSet, base_dir: Path) -> None:
        """Parse rule definitions from text content.
        
        Args:
            content: Text content containing rules.
            ruleset: RuleSet to populate.
            base_dir: Base directory for resolving includes.
        """
        lines = content.split("\n")
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            tokens = line.split()
            if not tokens:
                continue
            
            original_name = tokens[0]
            name = original_name
            
            # Handle .include directive
            if name == ".include" or name.endswith(".include"):
                if len(tokens) < 2:
                    raise ValueError(f"Invalid .include directive: {line}")
                include_file = base_dir / tokens[1]
                self._load_rules_recursive(include_file, ruleset, base_dir)
                continue
            
            # Parse weight and deduplication markers
            weight = 1
            no_duplicates = False
            
            # Check for ! suffix (no duplicates) - but not if escaped with backslash
            if name.endswith("!") and not name.endswith("\\!"):
                no_duplicates = True
                name = name[:-1]
                # Initialize deduplication cache
                if name not in self.expansion_cache:
                    self.expansion_cache[name] = set()
                continue  # This line just marks the rule, no expansion
            
            # Check for +N suffix (weight) - but not if escaped with backslash  
            if "+" in name and not "\\" in name:
                parts = name.rsplit("+", 1)  # Split from right to handle names like FOO_BAR+5
                if len(parts) == 2 and parts[1].isdigit():
                    name = parts[0]
                    weight = int(parts[1])
            
            # Now handle escaped characters in the rule name  
            # CITATIONLABEL\+ becomes CITATIONLABEL+
            # CITATIONLABEL\# becomes CITATIONLABEL#
            name = name.replace('\\+', '+').replace('\\#', '#').replace('\\!', '!')
            
            # Parse expansion
            expansion = ""
            
            if len(tokens) == 2 and tokens[1] == "{":
                # Multi-line expansion
                expansion_lines = []
                while i < len(lines):
                    line = lines[i]
                    i += 1
                    if line.strip() == "}":
                        break
                    expansion_lines.append(line.rstrip())
                expansion = "\n".join(expansion_lines)
            else:
                # Single-line expansion
                expansion = " ".join(tokens[1:]) if len(tokens) > 1 else ""
            
            # Skip rules with escaped operators and no expansion
            # e.g., "CITATIONLABEL\+" with no expansion means don't create a rule,
            # just let CITATIONLABEL+ be handled as a counter operator
            if not expansion and (name.endswith('+') or name.endswith('#')) and '\\' in original_name:
                continue
            
            # Add rule to ruleset
            rule_name = name
            if rule_name in ruleset.rules:
                rule = ruleset.rules[rule_name]
            else:
                rule = Rule(name=rule_name, no_duplicates=no_duplicates)
                ruleset.rules[rule_name] = rule
            
            rule.add_expansion(expansion, weight)
            
            if self.debug_level > 10:
                print(f"Rule: {rule_name} -> {expansion[:50]}... (weight={weight})")
    
    def expand(self, start_symbol: str, max_iterations: int = 50) -> str:
        """Expand a grammar rule recursively.
        
        Args:
            start_symbol: The starting rule to expand.
            max_iterations: Maximum iterations to prevent infinite loops.
            
        Returns:
            The fully expanded text.
        """
        # Check recursion depth
        self._recursion_depth += 1
        if self._recursion_depth > self.MAX_RECURSION_DEPTH:
            self._recursion_depth -= 1
            return f"<{start_symbol}>"  # Return placeholder if too deep
        
        try:
            result = self._expand_internal(start_symbol, max_iterations)
            return result
        finally:
            self._recursion_depth -= 1
    
    def _expand_internal(self, start_symbol: str, max_iterations: int = 50) -> str:
        """Internal expansion method without recursion tracking.
        
        Args:
            start_symbol: The starting rule to expand.
            max_iterations: Maximum iterations to prevent infinite loops.
            
        Returns:
            The fully expanded text.
        """
        # **PYTHONIC IMPROVEMENT**: Check context first for dynamic variables
        # This overrides static rules, allowing runtime customization
        if start_symbol in self.context:
            options = self.context[start_symbol]
            if options:
                return random.choice(options)
            return ""
        
        # First, try to get the rule as-is (handles rules like CITATIONLABEL+ that are literal)
        rule = self.ruleset.get_rule(start_symbol)
        if rule and rule.expansions:
            # Rule exists exactly as specified, use it
            pass  # Continue to expansion logic below
        elif start_symbol.endswith("+"):
            # No exact rule found, treat as sequential counter
            rule_name = start_symbol[:-1]
            counter = self.counters.get(rule_name, 0)
            self.counters[rule_name] = counter + 1
            return str(counter)
        elif start_symbol.endswith("#"):
            # No exact rule found, treat as random reference to previous counter
            rule_name = start_symbol[:-1]
            max_val = self.counters.get(rule_name, 0)
            if max_val == 0:
                return "0"
            return str(random.randint(0, max_val - 1))
        else:
            # No rule found and no special operator, return as literal
            return start_symbol
        
        # Try to find a non-duplicate expansion
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            
            # Pick random expansion
            expansion = random.choice(rule.expansions)
            
            # Recursively expand
            result = self._expand_text(expansion)
            
            # Check for duplicates if needed
            if rule.no_duplicates:
                cache_key = start_symbol
                if cache_key in self.expansion_cache:
                    if result in self.expansion_cache[cache_key]:
                        # Duplicate found, try again
                        if iteration >= max_iterations:
                            # Give up after too many tries
                            if self.debug_level > 0:
                                print(f"Warning: Could not avoid duplicate for {start_symbol}")
                            break
                        continue
                    else:
                        # New unique expansion
                        self.expansion_cache[cache_key].add(result)
            
            if self.debug_level >= 5:
                print(f"{start_symbol} -> {result[:100]}...")
            
            return result
        
        return result
    
    def _expand_text(self, text: str) -> str:
        """Expand all rule references in a text string.
        
        Matches Perl's pop_first_rule + expand loop:
        - Finds first rule match in text
        - Recursively expands it
        - Continues with remainder
        - Handles concatenated patterns like "NONZDIGIT" naturally
        
        **PYTHONIC IMPROVEMENT**: Also expands context variables (like SYSNAME)
        that aren't defined in grammar but are injected at runtime.
        
        Args:
            text: Text potentially containing rule references.
            
        Returns:
            Text with all rules expanded.
        """
        if not self._pattern and not self.context:
            return text
        
        components = []
        remaining = text
        
        while True:
            # **PYTHONIC IMPROVEMENT**: Check for context variables first
            # These aren't in the main pattern because they're runtime-injected
            context_match = None
            if self.context:
                # Build pattern for context variables: (.*?)(VAR1|VAR2|...)
                context_keys = '|'.join(re.escape(key) for key in sorted(self.context.keys(), key=len, reverse=True))
                if context_keys:
                    context_pattern = re.compile(f'^(.*?)({context_keys})')
                    context_match = context_pattern.match(remaining)
            
            # Check for counter references (RULE+ or RULE#)
            # These aren't in the main pattern to avoid regex complexity
            counter_match = re.match(r'^(.*?)([A-Z_]+)([+#])', remaining)
            pattern_match = self._pattern.match(remaining) if self._pattern else None
            
            # Choose whichever match comes first (preamble is shortest)
            matches = []
            if context_match:
                matches.append(('context', context_match))
            if counter_match:
                matches.append(('counter', counter_match))
            if pattern_match:
                matches.append(('pattern', pattern_match))
            
            if not matches:
                # No more matches
                components.append(remaining)
                break
            
            # Choose the match with the shortest preamble (comes first in text)
            match_type, match = min(matches, key=lambda x: len(x[1].group(1)))
            is_counter = (match_type == 'counter')
            is_context = (match_type == 'context')
            
            # Extract preamble and rule name
            preamble = match.group(1)
            if is_counter:
                rule_name = match.group(2) + match.group(3)  # e.g., "CITATION+"
            else:
                rule_name = match.group(2)  # Just the rule name
            
            # Add preamble
            if preamble:
                components.append(preamble)
            
            # Recursively expand the rule
            expanded = self.expand(rule_name)
            if expanded:
                components.append(expanded)
            
            # Continue with remainder
            remaining = remaining[match.end():]
        
        return "".join(components)
    
    def generate(self, start_symbol: str = "START") -> str:
        """Generate text starting from a given symbol.
        
        Args:
            start_symbol: The starting rule name.
            
        Returns:
            Generated text.
        """
        return self.expand(start_symbol)
    
    def reset_state(self) -> None:
        """Reset counters and caches."""
        self.counters.clear()
        self.expansion_cache.clear()
