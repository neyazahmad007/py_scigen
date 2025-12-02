"""Text processing and formatting utilities."""

import re
from typing import List


class TextProcessor:
    """Handles text formatting and prettification for generated content.
    
    This class provides utilities for:
    - LaTeX formatting
    - Title case conversion
    - Article correction (a/an)
    - Whitespace normalization
    - Section capitalization
    """
    
    @staticmethod
    def fix_articles(text: str) -> str:
        """Fix 'a' vs 'an' based on following vowel sounds.
        
        Args:
            text: Input text.
            
        Returns:
            Text with corrected articles.
        """
        # Replace 'a' with 'an' before vowels
        text = re.sub(r'\b(a)\s+([aeiou])', r'\1n \2', text, flags=re.IGNORECASE)
        return text
    
    @staticmethod
    def fix_punctuation_spacing(text: str) -> str:
        """Remove spaces before punctuation.
        
        Args:
            text: Input text.
            
        Returns:
            Text with fixed punctuation spacing.
        """
        # Remove spaces before punctuation
        text = re.sub(r'\s+([.,;:?!])', r'\1', text)
        return text
    
    @staticmethod
    def capitalize_title(text: str) -> str:
        """Convert text to title case, preserving certain words lowercase.
        
        Args:
            text: Input text.
            
        Returns:
            Title-cased text.
        """
        # Words that should stay lowercase in titles
        lowercase_words = {
            'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for',
            'in', 'nor', 'of', 'on', 'or', 'so', 'the', 'to', 'up', 'yet'
        }
        
        words = text.split()
        result = []
        
        for i, word in enumerate(words):
            # First and last words always capitalized
            if i == 0 or i == len(words) - 1:
                result.append(word.capitalize())
            # Check if word should stay lowercase
            elif word.lower() in lowercase_words:
                result.append(word.lower())
            else:
                result.append(word.capitalize())
        
        return ' '.join(result)
    
    @staticmethod
    def capitalize_sentence(text: str) -> str:
        """Capitalize the first letter of each sentence.
        
        Args:
            text: Input text.
            
        Returns:
            Text with capitalized sentences.
        """
        # Split by sentence boundaries
        sentences = re.split(r'([.!?]+\s+)', text)
        result = []
        
        for i, part in enumerate(sentences):
            if i % 2 == 0 and part:  # Actual sentence content
                # Find the first alphabetic character and capitalize it
                for j, char in enumerate(part):
                    if char.isalpha():
                        result.append(part[:j] + char.upper() + part[j+1:])
                        break
                else:
                    # No alphabetic character found
                    result.append(part)
            else:
                result.append(part)
        
        return ''.join(result)
    
    @staticmethod
    def preserve_latex_commands(text: str) -> str:
        """Ensure LaTeX commands are not broken by formatting.
        
        Args:
            text: Input text.
            
        Returns:
            Text with preserved LaTeX commands.
        """
        # Fix common LaTeX command issues
        text = re.sub(r'\\Em\b', r'\\em', text)
        return text
    
    @staticmethod
    def format_latex_section(title: str) -> str:
        """Format a section title for LaTeX.
        
        Args:
            title: Section title.
            
        Returns:
            Formatted title.
        """
        title = TextProcessor.capitalize_title(title)
        title = TextProcessor.fix_articles(title)
        return title
    
    @staticmethod
    def format_bibtex_field(text: str) -> str:
        """Format a BibTeX field value, preserving capitalization.
        
        Args:
            text: Field text.
            
        Returns:
            Formatted text with capitalized words in braces.
        """
        # Place braces around words containing capital letters
        words = text.split()
        result = []
        
        for word in words:
            # Skip if word is all lowercase or starts with special char
            if word.islower() or word.startswith('\\'):
                result.append(word)
            # Check if contains capital letters
            elif any(c.isupper() for c in word if c.isalpha()):
                # Don't double-brace
                if not (word.startswith('{') and word.endswith('}')):
                    result.append(f'{{{word}}}')
                else:
                    result.append(word)
            else:
                result.append(word)
        
        return ' '.join(result)
    
    def pretty_print(self, text: str, case_style: str = "sentence") -> str:
        """Apply pretty printing to generated text.
        
        Args:
            text: Input text.
            case_style: Style for capitalization ('sentence', 'title', or 'none').
            
        Returns:
            Formatted text.
        """
        lines = text.split('\n')
        result_lines = []
        
        for line in lines:
            # Skip LaTeX commands and empty lines
            if not line.strip() or line.strip().startswith('\\'):
                result_lines.append(line)
                continue
            
            # Apply fixes
            line = self.fix_punctuation_spacing(line)
            line = self.fix_articles(line)
            
            # Apply capitalization based on style
            if case_style == "sentence":
                line = self.capitalize_sentence(line)
            elif case_style == "title":
                line = self.capitalize_title(line)
            
            # Preserve LaTeX commands
            line = self.preserve_latex_commands(line)
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)


class LatexEscaper:
    """Handles LaTeX special character escaping."""
    
    # Characters that need escaping in LaTeX
    SPECIAL_CHARS = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    
    @classmethod
    def escape(cls, text: str, skip_math: bool = True) -> str:
        """Escape LaTeX special characters.
        
        Args:
            text: Text to escape.
            skip_math: If True, don't escape content inside $ $.
            
        Returns:
            Escaped text.
        """
        if skip_math:
            # Split by math mode delimiters and only escape non-math parts
            parts = re.split(r'(\$.*?\$)', text)
            result = []
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Not in math mode
                    result.append(cls._escape_text(part))
                else:  # In math mode
                    result.append(part)
            return ''.join(result)
        else:
            return cls._escape_text(text)
    
    @classmethod
    def _escape_text(cls, text: str) -> str:
        """Escape special characters in text.
        
        Args:
            text: Text to escape.
            
        Returns:
            Escaped text.
        """
        result = text
        for char, escaped in cls.SPECIAL_CHARS.items():
            result = result.replace(char, escaped)
        return result
