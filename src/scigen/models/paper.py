"""Domain models for SCIgen paper generation."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime


@dataclass
class Author:
    """Represents a paper author.
    
    Attributes:
        name: Author's full name.
        email: Optional email address.
        institution: Optional institution affiliation.
    """
    
    name: str
    email: Optional[str] = None
    institution: Optional[str] = None
    
    def to_latex(self) -> str:
        """Convert author to LaTeX format."""
        if self.institution:
            return f"\\author{{\\IEEEauthorblockN{{{self.name}}}\n\\IEEEauthorblockA{{{self.institution}}}}}"
        return f"\\author{{{self.name}}}"


@dataclass
class Reference:
    """Represents a bibliography reference.
    
    Attributes:
        key: BibTeX citation key.
        entry_type: Type of entry (article, inproceedings, etc.).
        fields: Dictionary of BibTeX fields.
    """
    
    key: str
    entry_type: str
    fields: Dict[str, str] = field(default_factory=dict)
    
    def to_bibtex(self) -> str:
        """Convert reference to BibTeX format."""
        lines = [f"@{self.entry_type}{{{self.key},"]
        for key, value in self.fields.items():
            lines.append(f"  {key} = {{{value}}},")
        lines.append("}")
        return "\n".join(lines)


@dataclass
class Section:
    """Represents a paper section.
    
    Attributes:
        title: Section title.
        content: Section content (LaTeX formatted).
        subsections: List of subsections.
        label: Optional LaTeX label for cross-referencing.
    """
    
    title: str
    content: str = ""
    subsections: List["Section"] = field(default_factory=list)
    label: Optional[str] = None
    
    def to_latex(self) -> str:
        """Convert section to LaTeX format."""
        lines = []
        
        # Section header
        if self.label:
            lines.append(f"\\section{{{self.title}}}\\label{{{self.label}}}")
        else:
            lines.append(f"\\section{{{self.title}}}")
        
        # Content
        if self.content:
            lines.append("")
            lines.append(self.content)
        
        # Subsections
        for subsection in self.subsections:
            lines.append("")
            lines.append(subsection.to_latex())
        
        return "\n".join(lines)


@dataclass
class Figure:
    """Represents a figure in the paper.
    
    Attributes:
        filename: Figure file name.
        caption: Figure caption.
        label: LaTeX label for cross-referencing.
        width: Optional width specification.
    """
    
    filename: str
    caption: str
    label: str
    width: str = "0.8\\linewidth"
    
    def to_latex(self) -> str:
        """Convert figure to LaTeX format."""
        return f"""\\begin{{figure}}[t]
\\centering
\\includegraphics[width={self.width}]{{{self.filename}}}
\\caption{{{self.caption}}}
\\label{{{self.label}}}
\\end{{figure}}"""


@dataclass
class Paper:
    """Represents a complete scientific paper.
    
    Attributes:
        title: Paper title.
        authors: List of authors.
        abstract: Abstract text.
        sections: List of main sections.
        references: List of references.
        figures: List of figures.
        metadata: Additional metadata.
        generated_at: Timestamp of generation.
    """
    
    title: str
    authors: List[Author] = field(default_factory=list)
    abstract: str = ""
    sections: List[Section] = field(default_factory=list)
    references: List[Reference] = field(default_factory=list)
    figures: List[Figure] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_latex(self) -> str:
        """Convert complete paper to LaTeX."""
        lines = []
        
        # Document class and packages
        lines.append("\\documentclass[conference]{IEEEtran}")
        lines.append("\\IEEEoverridecommandlockouts")  # Allow column balancing
        lines.append("\\usepackage{graphicx}")
        lines.append("\\usepackage{epsfig}")
        lines.append("\\usepackage{epstopdf}")  # For automatic EPS to PDF conversion
        lines.append("\\usepackage{amsmath}")
        lines.append("\\usepackage{hyperref}")
        lines.append("")
        
        # Begin document
        lines.append("\\begin{document}")
        lines.append("")
        
        # Title
        lines.append(f"\\title{{{self.title}}}")
        lines.append("")
        
        # Authors
        if len(self.authors) == 1:
            lines.append(self.authors[0].to_latex())
        else:
            lines.append("\\author{")
            for i, author in enumerate(self.authors):
                if i > 0:
                    lines.append("\\and")
                lines.append(f"\\IEEEauthorblockN{{{author.name}}}")
                if author.institution:
                    lines.append(f"\\IEEEauthorblockA{{{author.institution}}}")
            lines.append("}")
        lines.append("")
        
        lines.append("\\maketitle")
        lines.append("")
        
        # Abstract
        if self.abstract:
            lines.append("\\begin{abstract}")
            lines.append(self.abstract)
            lines.append("\\end{abstract}")
            lines.append("")
        
        # Sections
        for section in self.sections:
            lines.append(section.to_latex())
            lines.append("")
        
        # Bibliography with column balancing
        if self.references:
            # Trigger column balancing at the last reference
            num_refs = len(self.references)
            lines.append(f"\\IEEEtriggeratref{{{num_refs}}}")
            lines.append("\\bibliographystyle{IEEEtran}")
            # Use the same base name as the .tex file for .bib
            lines.append("\\bibliography{references}")

        
        # End document
        lines.append("\\end{document}")
        
        return "\n".join(lines)
    
    def save_latex(self, path: Path) -> None:
        """Save paper as LaTeX file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_latex())
    
    def save_bibtex(self, path: Path) -> None:
        """Save references as BibTeX file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        bibtex = "\n\n".join(ref.to_bibtex() for ref in self.references)
        path.write_text(bibtex)
