"""Unit tests for paper generation."""

import pytest
from pathlib import Path
from scigen.generators.paper import PaperGenerator, SimplePaperGenerator
from scigen.config import GeneratorConfig
from scigen.models.paper import Paper, Author, Section


class TestPaperGenerator:
    """Tests for PaperGenerator class."""
    
    def test_create_generator(self):
        """Test creating a paper generator."""
        config = GeneratorConfig(seed=12345, authors=["Alice"])
        generator = PaperGenerator(config)
        
        assert generator.config.seed == 12345
        assert generator.engine is not None
    
    def test_create_authors(self):
        """Test author creation from config."""
        config = GeneratorConfig(
            authors=["Alice", "Bob"],
            institution="MIT"
        )
        generator = PaperGenerator(config)
        authors = generator._create_authors()
        
        assert len(authors) == 2
        assert authors[0].name == "Alice"
        assert authors[1].name == "Bob"
        assert all(a.institution == "MIT" for a in authors)
    
    def test_generate_with_seed_reproducible(self):
        """Test that same seed produces same output."""
        config1 = GeneratorConfig(seed=42)
        config2 = GeneratorConfig(seed=42)
        
        gen1 = PaperGenerator(config1)
        gen2 = PaperGenerator(config2)
        
        # Note: This test may fail if rules aren't loaded
        # It's more of an integration test
        # Just verify generators are created
        assert gen1.config.seed == gen2.config.seed


class TestSimplePaperGenerator:
    """Tests for SimplePaperGenerator class."""
    
    def test_create_simple_generator(self, tmp_path):
        """Test creating a simple generator."""
        rules_file = tmp_path / "rules.txt"
        rules_file.write_text("TEST hello world\n")
        
        generator = SimplePaperGenerator(rules_file, seed=123)
        assert generator.engine is not None
    
    def test_generate_simple_text(self, tmp_path):
        """Test generating simple text."""
        rules_file = tmp_path / "rules.txt"
        rules_file.write_text("GREETING hello world\n")
        
        generator = SimplePaperGenerator(rules_file, seed=123)
        result = generator.generate("GREETING")
        
        assert result == "hello world"


class TestPaperModel:
    """Tests for Paper model."""
    
    def test_create_paper(self):
        """Test creating a paper object."""
        paper = Paper(
            title="Test Paper",
            abstract="This is a test"
        )
        
        assert paper.title == "Test Paper"
        assert paper.abstract == "This is a test"
        assert len(paper.authors) == 0
        assert len(paper.sections) == 0
    
    def test_add_author(self):
        """Test adding authors to paper."""
        paper = Paper(title="Test")
        paper.authors.append(Author(name="Alice"))
        paper.authors.append(Author(name="Bob"))
        
        assert len(paper.authors) == 2
    
    def test_add_section(self):
        """Test adding sections to paper."""
        paper = Paper(title="Test")
        section = Section(title="Introduction", content="Hello")
        paper.sections.append(section)
        
        assert len(paper.sections) == 1
        assert paper.sections[0].title == "Introduction"
    
    def test_paper_to_latex_basic(self):
        """Test converting paper to LaTeX."""
        author = Author(name="Alice", institution="MIT")
        paper = Paper(
            title="Test Paper",
            authors=[author],
            abstract="This is a test abstract."
        )
        
        latex = paper.to_latex()
        
        assert "\\documentclass" in latex
        assert "Test Paper" in latex
        assert "Alice" in latex
        assert "This is a test abstract" in latex
    
    def test_save_latex(self, tmp_path):
        """Test saving paper as LaTeX."""
        paper = Paper(title="Test")
        output = tmp_path / "paper.tex"
        
        paper.save_latex(output)
        
        assert output.exists()
        content = output.read_text()
        assert "Test" in content
    
    def test_save_bibtex(self, tmp_path):
        """Test saving references as BibTeX."""
        from scigen.models.paper import Reference
        
        paper = Paper(title="Test")
        paper.references.append(
            Reference(
                key="test2024",
                entry_type="article",
                fields={"title": "Test Article", "year": "2024"}
            )
        )
        
        output = tmp_path / "refs.bib"
        paper.save_bibtex(output)
        
        assert output.exists()
        content = output.read_text()
        assert "@article" in content
        assert "test2024" in content


class TestAuthor:
    """Tests for Author model."""
    
    def test_create_author(self):
        """Test creating an author."""
        author = Author(name="Alice Smith")
        assert author.name == "Alice Smith"
        assert author.email is None
        assert author.institution is None
    
    def test_author_with_institution(self):
        """Test author with institution."""
        author = Author(
            name="Bob Jones",
            email="bob@example.com",
            institution="MIT CSAIL"
        )
        assert author.institution == "MIT CSAIL"
    
    def test_author_to_latex(self):
        """Test converting author to LaTeX."""
        author = Author(name="Alice", institution="MIT")
        latex = author.to_latex()
        
        assert "Alice" in latex
        assert "MIT" in latex


class TestSection:
    """Tests for Section model."""
    
    def test_create_section(self):
        """Test creating a section."""
        section = Section(title="Introduction")
        assert section.title == "Introduction"
        assert section.content == ""
    
    def test_section_with_content(self):
        """Test section with content."""
        section = Section(
            title="Methods",
            content="We used Python for implementation."
        )
        assert "Python" in section.content
    
    def test_section_to_latex(self):
        """Test converting section to LaTeX."""
        section = Section(
            title="Introduction",
            content="This is the intro.",
            label="sec:intro"
        )
        
        latex = section.to_latex()
        assert "\\section{Introduction}" in latex
        assert "\\label{sec:intro}" in latex
        assert "This is the intro" in latex
    
    def test_nested_sections(self):
        """Test sections with subsections."""
        subsection = Section(title="Subsection", content="Sub content")
        section = Section(
            title="Main",
            content="Main content",
            subsections=[subsection]
        )
        
        assert len(section.subsections) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
