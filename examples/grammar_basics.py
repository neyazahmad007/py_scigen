#!/usr/bin/env python3
"""Example of using the grammar engine directly."""

from pathlib import Path
from scigen.core.grammar import GrammarEngine
from scigen.models.rules import Rule, RuleSet


def simple_grammar_example():
    """Show basic grammar expansion."""
    print("=" * 60)
    print("Example 1: Simple Grammar Expansion")
    print("=" * 60)
    
    # Create rules manually
    ruleset = RuleSet()
    
    # Add some simple rules
    ruleset.add_rule(Rule(name="GREETING", expansions=["Hello", "Hi", "Hey"]))
    ruleset.add_rule(Rule(name="NAME", expansions=["World", "Universe", "Everyone"]))
    ruleset.add_rule(Rule(name="START", expansions=["GREETING NAME!"]))
    
    # Create engine
    engine = GrammarEngine(ruleset, debug_level=0)
    
    # Generate several times
    print("\nGenerating 5 greetings:")
    for i in range(5):
        result = engine.generate("START")
        print(f"  {i+1}. {result}")


def weighted_rules_example():
    """Show weighted random selection."""
    print("\n" + "=" * 60)
    print("Example 2: Weighted Rules")
    print("=" * 60)
    
    ruleset = RuleSet()
    
    # Create rule with different weights
    rule = Rule(name="RESPONSE", expansions=[])
    rule.add_expansion("Common response", weight=5)
    rule.add_expansion("Rare response", weight=1)
    ruleset.add_rule(rule)
    
    # Generate many times to see distribution
    engine = GrammarEngine(ruleset)
    results = [engine.expand("RESPONSE") for _ in range(100)]
    
    print(f"\nGenerated 100 responses:")
    print(f"  'Common response': {results.count('Common response')}")
    print(f"  'Rare response': {results.count('Rare response')}")
    print(f"\nExpected ratio: ~5:1")


def counter_example():
    """Show counter functionality."""
    print("\n" + "=" * 60)
    print("Example 3: Counters")
    print("=" * 60)
    
    ruleset = RuleSet()
    ruleset.add_rule(Rule(name="ID", expansions=["dummy"]))
    
    engine = GrammarEngine(ruleset)
    
    print("\nSequential counter (ID+):")
    for i in range(5):
        result = engine.expand("ID+")
        print(f"  {i+1}. {result}")
    
    print("\nRandom reference to previous IDs (ID#):")
    for i in range(5):
        result = engine.expand("ID#")
        print(f"  {i+1}. {result}")


def nested_rules_example():
    """Show nested rule expansion."""
    print("\n" + "=" * 60)
    print("Example 4: Nested Rules")
    print("=" * 60)
    
    ruleset = RuleSet()
    
    # Create hierarchical rules
    ruleset.add_rule(Rule(name="ADJECTIVE", expansions=["amazing", "brilliant", "fantastic"]))
    ruleset.add_rule(Rule(name="NOUN", expansions=["algorithm", "system", "framework"]))
    ruleset.add_rule(Rule(name="VERB", expansions=["implements", "describes", "presents"]))
    ruleset.add_rule(Rule(
        name="TITLE",
        expansions=[
            "This paper VERB a ADJECTIVE NOUN",
            "A ADJECTIVE approach to NOUN",
            "NOUN: a ADJECTIVE perspective"
        ]
    ))
    
    engine = GrammarEngine(ruleset)
    
    print("\nGenerating paper titles:")
    for i in range(5):
        result = engine.generate("TITLE")
        print(f"  {i+1}. {result}")


def main():
    """Run all examples."""
    simple_grammar_example()
    weighted_rules_example()
    counter_example()
    nested_rules_example()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
