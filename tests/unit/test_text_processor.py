"""Unit tests for text processing."""

import pytest
from scigen.processors.text import TextProcessor, LatexEscaper


class TestTextProcessor:
    """Tests for TextProcessor class."""
    
    def test_fix_articles_lowercase(self):
        """Test fixing 'a' to 'an' before vowels."""
        processor = TextProcessor()
        
        assert processor.fix_articles("a apple") == "an apple"
        assert processor.fix_articles("a elephant") == "an elephant"
        assert processor.fix_articles("a interesting") == "an interesting"
        assert processor.fix_articles("a orange") == "an orange"
        assert processor.fix_articles("a umbrella") == "an umbrella"
    
    def test_fix_articles_preserves_consonants(self):
        """Test that 'a' before consonants is preserved."""
        processor = TextProcessor()
        
        assert processor.fix_articles("a book") == "a book"
        assert processor.fix_articles("a cat") == "a cat"
        assert processor.fix_articles("a dog") == "a dog"
    
    def test_fix_articles_case_insensitive(self):
        """Test article fixing is case insensitive."""
        processor = TextProcessor()
        
        assert processor.fix_articles("A apple") == "An apple"
        assert processor.fix_articles("A elephant") == "An elephant"
    
    def test_fix_punctuation_spacing(self):
        """Test removing spaces before punctuation."""
        processor = TextProcessor()
        
        assert processor.fix_punctuation_spacing("hello , world") == "hello, world"
        assert processor.fix_punctuation_spacing("test .") == "test."
        assert processor.fix_punctuation_spacing("what ?") == "what?"
        assert processor.fix_punctuation_spacing("hello ; there") == "hello; there"
    
    def test_capitalize_title(self):
        """Test title case capitalization."""
        processor = TextProcessor()
        
        result = processor.capitalize_title("the quick brown fox")
        assert result == "The Quick Brown Fox"
        
        # Small words should stay lowercase (except first/last)
        result = processor.capitalize_title("a tale of two cities")
        assert result == "A Tale of Two Cities"
    
    def test_capitalize_sentence(self):
        """Test sentence capitalization."""
        processor = TextProcessor()
        
        result = processor.capitalize_sentence("hello. world. test.")
        assert result.startswith("Hello")
        assert "World" in result
        assert "Test" in result
    
    def test_format_latex_section(self):
        """Test LaTeX section formatting."""
        processor = TextProcessor()
        
        result = processor.format_latex_section("introduction to systems")
        assert result[0].isupper()
        assert "Introduction" in result
    
    def test_format_bibtex_field(self):
        """Test BibTeX field formatting."""
        processor = TextProcessor()
        
        # Words with capitals should be wrapped in braces
        result = processor.format_bibtex_field("The LaTeX Companion")
        assert "{LaTeX}" in result
    
    def test_preserve_latex_commands(self):
        """Test preserving LaTeX commands."""
        processor = TextProcessor()
        
        result = processor.preserve_latex_commands("This is \\Em text")
        assert "\\em" in result
        assert "\\Em" not in result
    
    def test_pretty_print_basic(self):
        """Test basic pretty printing."""
        processor = TextProcessor()
        
        text = "this is a test . a elephant ran ."
        result = processor.pretty_print(text)
        
        assert "This is a test." in result
        assert "an elephant" in result


class TestLatexEscaper:
    """Tests for LatexEscaper class."""
    
    def test_escape_ampersand(self):
        """Test escaping ampersand."""
        result = LatexEscaper.escape("foo & bar")
        assert result == "foo \\& bar"
    
    def test_escape_percent(self):
        """Test escaping percent."""
        result = LatexEscaper.escape("100% complete")
        assert result == "100\\% complete"
    
    def test_escape_dollar(self):
        """Test escaping dollar."""
        result = LatexEscaper.escape("$100", skip_math=False)
        assert result == "\\$100"
    
    def test_escape_hash(self):
        """Test escaping hash."""
        result = LatexEscaper.escape("#define")
        assert result == "\\#define"
    
    def test_escape_underscore(self):
        """Test escaping underscore."""
        result = LatexEscaper.escape("hello_world")
        assert result == "hello\\_world"
    
    def test_escape_braces(self):
        """Test escaping braces."""
        result = LatexEscaper.escape("{test}")
        assert result == "\\{test\\}"
    
    def test_skip_math_mode(self):
        """Test skipping math mode when escaping."""
        result = LatexEscaper.escape("Cost is $100 & $200", skip_math=True)
        # & should be escaped, but $ should not
        assert "\\&" in result
        # Note: This is a simplified test; real implementation more complex
    
    def test_escape_all_special_chars(self):
        """Test escaping all special characters."""
        result = LatexEscaper.escape("& % $ # _ { }", skip_math=False)
        assert "\\" in result  # Should have many backslashes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
