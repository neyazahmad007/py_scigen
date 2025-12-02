"""Unit tests for grammar engine."""

import pytest
from pathlib import Path
from scigen.core.grammar import GrammarEngine
from scigen.models.rules import Rule, RuleSet


class TestRule:
    """Tests for Rule class."""
    
    def test_create_simple_rule(self):
        """Test creating a simple rule."""
        rule = Rule(name="TEST", expansions=["hello", "world"])
        assert rule.name == "TEST"
        assert len(rule.expansions) == 2
        assert "hello" in rule.expansions
    
    def test_rule_with_weights(self):
        """Test rule with weighted expansions."""
        rule = Rule(
            name="TEST",
            expansions=["a", "b", "c"],
            weights=[1, 2, 3]
        )
        assert len(rule.weights) == 3
    
    def test_rule_weight_mismatch_raises_error(self):
        """Test that mismatched weights raise an error."""
        with pytest.raises(ValueError):
            Rule(
                name="TEST",
                expansions=["a", "b"],
                weights=[1, 2, 3]  # Mismatch
            )
    
    def test_add_expansion(self):
        """Test adding expansions to a rule."""
        rule = Rule(name="TEST")
        rule.add_expansion("first", weight=1)
        rule.add_expansion("second", weight=2)
        
        assert len(rule.expansions) == 3  # "second" added twice due to weight
        assert rule.expansions.count("second") == 2


class TestRuleSet:
    """Tests for RuleSet class."""
    
    def test_create_empty_ruleset(self):
        """Test creating an empty ruleset."""
        ruleset = RuleSet()
        assert len(ruleset) == 0
        assert not ruleset.has_rule("ANYTHING")
    
    def test_add_rule(self):
        """Test adding a rule to ruleset."""
        ruleset = RuleSet()
        rule = Rule(name="TEST", expansions=["value"])
        ruleset.add_rule(rule)
        
        assert len(ruleset) == 1
        assert ruleset.has_rule("TEST")
        assert "TEST" in ruleset
    
    def test_merge_rules(self):
        """Test merging rules with the same name."""
        ruleset = RuleSet()
        
        rule1 = Rule(name="TEST", expansions=["a", "b"])
        rule2 = Rule(name="TEST", expansions=["c", "d"])
        
        ruleset.add_rule(rule1)
        ruleset.add_rule(rule2)
        
        assert len(ruleset) == 1
        merged = ruleset.get_rule("TEST")
        assert len(merged.expansions) == 4
    
    def test_get_nonexistent_rule(self):
        """Test getting a nonexistent rule."""
        ruleset = RuleSet()
        assert ruleset.get_rule("NONEXISTENT") is None


class TestGrammarEngine:
    """Tests for GrammarEngine class."""
    
    def test_create_engine(self):
        """Test creating a grammar engine."""
        engine = GrammarEngine()
        assert engine.ruleset is not None
        assert engine.debug_level == 0
    
    def test_expand_simple_rule(self):
        """Test expanding a simple rule."""
        ruleset = RuleSet()
        rule = Rule(name="GREETING", expansions=["hello"])
        ruleset.add_rule(rule)
        
        engine = GrammarEngine(ruleset)
        result = engine.expand("GREETING")
        assert result == "hello"
    
    def test_expand_with_reference(self):
        """Test expanding a rule that references another."""
        ruleset = RuleSet()
        ruleset.add_rule(Rule(name="WORD", expansions=["world"]))
        ruleset.add_rule(Rule(name="GREETING", expansions=["hello WORD"]))
        
        engine = GrammarEngine(ruleset)
        result = engine.expand("GREETING")
        assert result == "hello world"
    
    def test_expand_nested_references(self):
        """Test expanding nested rule references."""
        ruleset = RuleSet()
        ruleset.add_rule(Rule(name="A", expansions=["a"]))
        ruleset.add_rule(Rule(name="B", expansions=["b A"]))
        ruleset.add_rule(Rule(name="C", expansions=["c B"]))
        
        engine = GrammarEngine(ruleset)
        result = engine.expand("C")
        assert result == "c b a"
    
    def test_expand_nonexistent_rule(self):
        """Test expanding a rule that doesn't exist."""
        engine = GrammarEngine()
        result = engine.expand("NONEXISTENT")
        assert result == "NONEXISTENT"  # Returns as literal
    
    def test_counter_plus(self):
        """Test + suffix for sequential counters."""
        ruleset = RuleSet()
        ruleset.add_rule(Rule(name="COUNT", expansions=["dummy"]))
        
        engine = GrammarEngine(ruleset)
        
        # First call returns 0
        assert engine.expand("COUNT+") == "0"
        # Second call returns 1
        assert engine.expand("COUNT+") == "1"
        # Third call returns 2
        assert engine.expand("COUNT+") == "2"
    
    def test_counter_hash(self):
        """Test # suffix for random counter reference."""
        ruleset = RuleSet()
        ruleset.add_rule(Rule(name="COUNT", expansions=["dummy"]))
        
        engine = GrammarEngine(ruleset)
        
        # Build up counter
        engine.expand("COUNT+")
        engine.expand("COUNT+")
        engine.expand("COUNT+")
        
        # Should return random value 0-2
        result = int(engine.expand("COUNT#"))
        assert 0 <= result < 3
    
    def test_reset_state(self):
        """Test resetting engine state."""
        ruleset = RuleSet()
        ruleset.add_rule(Rule(name="COUNT", expansions=["dummy"]))
        
        engine = GrammarEngine(ruleset)
        
        engine.expand("COUNT+")
        engine.expand("COUNT+")
        
        engine.reset_state()
        
        # After reset, counter should start at 0 again
        assert engine.expand("COUNT+") == "0"
    
    def test_weighted_selection(self):
        """Test that weighted rules are selected more often."""
        ruleset = RuleSet()
        rule = Rule(name="TEST", expansions=["rare", "common"])
        # Add "common" multiple times to increase weight
        for _ in range(9):
            rule.expansions.append("common")
        ruleset.add_rule(rule)
        
        engine = GrammarEngine(ruleset)
        
        # Generate many samples
        results = [engine.expand("TEST") for _ in range(100)]
        
        # "common" should appear much more often
        common_count = results.count("common")
        assert common_count > 70  # Should be ~90%, allow some variance


class TestGrammarEngineFileLoading:
    """Tests for loading rules from files."""
    
    def test_load_simple_rules(self, tmp_path):
        """Test loading simple rules from a file."""
        rules_file = tmp_path / "test.txt"
        rules_file.write_text("""
# Comment line
GREETING hello world
FAREWELL goodbye
""")
        
        engine = GrammarEngine()
        engine.load_rules(rules_file)
        
        assert engine.ruleset.has_rule("GREETING")
        assert engine.ruleset.has_rule("FAREWELL")
    
    def test_load_multiline_rule(self, tmp_path):
        """Test loading multiline rule."""
        rules_file = tmp_path / "test.txt"
        rules_file.write_text("""
MULTI {
This is a
multiline
expansion
}
""")
        
        engine = GrammarEngine()
        engine.load_rules(rules_file)
        
        rule = engine.ruleset.get_rule("MULTI")
        assert rule is not None
        assert "multiline" in rule.expansions[0]
    
    def test_load_weighted_rule(self, tmp_path):
        """Test loading rule with weight."""
        rules_file = tmp_path / "test.txt"
        rules_file.write_text("""
TEST+3 value
""")
        
        engine = GrammarEngine()
        engine.load_rules(rules_file)
        
        rule = engine.ruleset.get_rule("TEST")
        assert len(rule.expansions) == 3
        assert all(e == "value" for e in rule.expansions)
    
    def test_file_not_found(self):
        """Test loading from nonexistent file."""
        engine = GrammarEngine()
        with pytest.raises(FileNotFoundError):
            engine.load_rules(Path("/nonexistent/file.txt"))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
