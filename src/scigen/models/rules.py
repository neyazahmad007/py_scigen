"""Data models for grammar rules."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from pathlib import Path


@dataclass
class Rule:
    """Represents a single grammar rule.
    
    Attributes:
        name: Rule name/identifier.
        expansions: List of possible expansions for this rule.
        weights: Optional weights for each expansion (for weighted random selection).
        no_duplicates: Whether to prevent duplicate expansions.
    """
    
    name: str
    expansions: List[str] = field(default_factory=list)
    weights: List[int] = field(default_factory=list)
    no_duplicates: bool = False
    
    def __post_init__(self) -> None:
        """Validate rule after creation."""
        if self.weights and len(self.weights) != len(self.expansions):
            raise ValueError(
                f"Rule '{self.name}': weights length ({len(self.weights)}) "
                f"must match expansions length ({len(self.expansions)})"
            )
    
    def add_expansion(self, expansion: str, weight: int = 1) -> None:
        """Add an expansion to this rule.
        
        Args:
            expansion: The expansion text.
            weight: Weight for random selection (default 1).
        """
        for _ in range(weight):
            self.expansions.append(expansion)
            if self.weights is not None:
                self.weights.append(weight)


@dataclass
class RuleSet:
    """Collection of grammar rules.
    
    Attributes:
        rules: Dictionary mapping rule names to Rule objects.
        included_files: Set of files that have been included.
        metadata: Additional metadata about the ruleset.
    """
    
    rules: Dict[str, Rule] = field(default_factory=dict)
    included_files: Set[Path] = field(default_factory=set)
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def add_rule(self, rule: Rule) -> None:
        """Add or merge a rule into the ruleset.
        
        Args:
            rule: Rule to add.
        """
        if rule.name in self.rules:
            # Merge with existing rule
            existing = self.rules[rule.name]
            existing.expansions.extend(rule.expansions)
            if existing.weights and rule.weights:
                existing.weights.extend(rule.weights)
        else:
            self.rules[rule.name] = rule
    
    def get_rule(self, name: str) -> Optional[Rule]:
        """Get a rule by name.
        
        Args:
            name: Rule name.
            
        Returns:
            Rule if found, None otherwise.
        """
        return self.rules.get(name)
    
    def has_rule(self, name: str) -> bool:
        """Check if a rule exists.
        
        Args:
            name: Rule name.
            
        Returns:
            True if rule exists.
        """
        return name in self.rules
    
    def __len__(self) -> int:
        """Return number of rules."""
        return len(self.rules)
    
    def __contains__(self, name: str) -> bool:
        """Check if rule exists using 'in' operator."""
        return name in self.rules
