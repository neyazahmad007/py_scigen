"""Paper generation module."""

import random
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional

from scigen.config import GeneratorConfig
from scigen.core.grammar import GrammarEngine
from scigen.models.paper import Paper, Author, Section, Reference
from scigen.models.rules import RuleSet
from scigen.processors.text import TextProcessor

# Optional imports for diagram/graph generation
try:
    from scigen.generators.diagram import DiagramGenerator
    DIAGRAM_AVAILABLE = True
except ImportError:
    DIAGRAM_AVAILABLE = False

try:
    from scigen.generators.graph import GraphGenerator
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False


class PaperGenerator:
    """High-level paper generation orchestrator.
    
    This class coordinates the entire paper generation process, managing
    the grammar engine, text processing, and assembly of paper components.
    
    Attributes:
        config: Generator configuration.
        engine: Grammar engine for text generation.
        processor: Text processor for formatting.
    """
    
    def __init__(self, config: GeneratorConfig):
        """Initialize the paper generator.
        
        Args:
            config: Generator configuration.
        """
        self.config = config
        
        # Initialize random seed
        random.seed(config.seed)
        
        # Load rules
        ruleset = RuleSet()
        self.engine = GrammarEngine(ruleset, debug_level=config.debug_level)
        
        # Load main rules file if it exists
        if config.rules_file.exists():
            self.engine.load_rules(config.rules_file)
        
        # Load system names dictionary for realistic vocabulary
        system_names_file = config.rules_file.parent / "system_names.txt"
        if system_names_file.exists():
            self.engine.load_rules(system_names_file)
        
        # Initialize text processor
        self.processor = TextProcessor()
    
    def generate(self) -> Paper:
        """Generate a complete scientific paper.
        
        Returns:
            Generated Paper object.
        """
        # Reset engine state for fresh generation
        self.engine.reset_state()
        
        # **PYTHONIC IMPROVEMENT**: Set context for dynamic variables
        # This is cleaner than Perl's manual rule injection
        system_name = self._generate_system_name()
        author_names = self.config.authors
        
        self.engine.set_context(
            SYSNAME=system_name,  # System name for titles and references
            AUTHOR_NAME=author_names,  # Author names for references
        )
        
        # Generate paper components
        title = self._generate_title()
        authors = self._create_authors()
        abstract = self._generate_abstract()
        sections = self._generate_sections()
        references = self._generate_references()
        
        # Create paper object
        paper = Paper(
            title=title,
            authors=authors,
            abstract=abstract,
            sections=sections,
            references=references,
            metadata={
                "seed": self.config.seed,
                "generator_version": "2.0.0",
            }
        )
        
        return paper
    
    def _generate_title(self) -> str:
        """Generate paper title.
        
        Returns:
            Paper title.
        """
        title = self.engine.expand("SCI_TITLE")
        
        if self.config.pretty_print:
            title = self.processor.capitalize_title(title)
            title = self.processor.fix_articles(title)
        
        return title
    
    def _generate_system_name(self) -> str:
        """Generate a random system name.
        
        Uses the grammar's system name generator which produces
        names from dictionary words (matching Perl's get_system_name).
        
        Returns:
            Generated system name.
        """
        # The grammar has a SYSTEM_NAME rule that generates creative names
        # If it doesn't exist, fall back to a simple generation
        system_name = self.engine.expand("SYSTEM_NAME")
        
        # Capitalize first letter for consistency
        if system_name:
            system_name = system_name[0].upper() + system_name[1:] if len(system_name) > 1 else system_name.upper()
        
        return system_name or "SysX"  # Fallback
    
    def _create_authors(self) -> List[Author]:
        """Create author list from configuration.
        
        Returns:
            List of Author objects.
        """
        return [
            Author(name=name, institution=self.config.institution)
            for name in self.config.authors
        ]
    
    def _generate_abstract(self) -> str:
        """Generate paper abstract.
        
        Returns:
            Abstract text.
        """
        abstract = self.engine.expand("SCI_ABSTRACT")
        
        if self.config.pretty_print:
            abstract = self.processor.pretty_print(abstract, case_style="sentence")
        
        return abstract
    
    def _generate_sections(self) -> List[Section]:
        """Generate main paper sections.
        
        Returns:
            List of Section objects.
        """
        sections = []
        
        # Define standard sections
        section_specs = [
            ("Introduction", "SCI_INTRO", "intro"),
            ("Model", "SCI_MODEL", "model"),
            ("Implementation", "SCI_IMPL", "impl"),
            ("Evaluation", "SCI_EVAL", "eval"),
            ("Related Work", "SCI_RELWORK", "related"),
            ("Conclusion", "SCI_CONCL", "conclusion"),
        ]
        
        for title, rule_name, label in section_specs:
            content = self.engine.expand(rule_name)
            
            if self.config.pretty_print:
                content = self.processor.pretty_print(content, case_style="sentence")
            
            # Remove any \section{} commands from content since we add them in the Section model
            # This prevents duplicate section headers
            import re
            content = re.sub(r'\\section\{[^}]*\}\s*', '', content)
            
            section = Section(
                title=title,
                content=content,
                label=f"sec:{label}"
            )
            sections.append(section)
        
        return sections
    
    def _generate_references(self) -> List[Reference]:
        """Generate bibliography references using grammar rules.
        
        Returns:
            List of Reference objects.
        """
        references = []
        
        # Generate random number of references (10-30)
        num_refs = random.randint(10, 30)
        
        # Populate SCI_SOURCE with author names for use in citations
        # This matches what the Perl version does
        author_names = self.config.authors  # These are already strings
        for _ in range(10):  # Add each author multiple times
            for author_name in author_names:
                # Add to rules so CITE_AUTHOR_LIST can use it
                if "SCI_SOURCE" not in self.engine.ruleset.rules:
                    from scigen.models.rules import Rule
                    self.engine.ruleset.rules["SCI_SOURCE"] = Rule(name="SCI_SOURCE")
                self.engine.ruleset.rules["SCI_SOURCE"].add_expansion(author_name)
        
        for i in range(num_refs):
            # Set the citation label
            cite_label = f"cite:{i}"
            if "CITE_LABEL_GIVEN" not in self.engine.ruleset.rules:
                from scigen.models.rules import Rule
                self.engine.ruleset.rules["CITE_LABEL_GIVEN"] = Rule(name="CITE_LABEL_GIVEN")
            else:
                self.engine.ruleset.rules["CITE_LABEL_GIVEN"].expansions.clear()
            self.engine.ruleset.rules["CITE_LABEL_GIVEN"].add_expansion(cite_label)
            
            # **PYTHONIC IMPROVEMENT**: Generate a unique system name for this reference
            # and inject it via context (cleaner than Perl's rule manipulation)
            ref_sysname = self._generate_system_name()
            self.engine.set_context(SYSNAME=ref_sysname)
            
            # Generate complete BibTeX entry using grammar
            bibtex_entry = self.engine.expand("BIBTEX_ENTRY")
            
            # Parse the generated BibTeX entry
            reference = self._parse_bibtex_entry(bibtex_entry, cite_label)
            if reference:
                references.append(reference)
        
        return references


    def generate_diagrams(self, output_dir: Path, system_name: Optional[str] = None) -> List[Path]:
        """Generate diagram files referenced in the paper.
        
        Args:
            output_dir: Directory to save diagram files.
            system_name: System name for diagrams (uses paper's SYSNAME if None).
            
        Returns:
            List of generated diagram file paths.
        """
        if not DIAGRAM_AVAILABLE:
            print("Warning: networkx not available, skipping diagram generation")
            return []
        
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = []
        
        sysname = system_name or self.engine.expand("SYSNAME")
        
        # Generate diagrams (typically dia0.eps, dia1.eps, etc.)
        # Increase to match typical paper generation (up to 4 diagrams)
        num_diagrams = 4
        
        for i in range(num_diagrams):
            try:
                # Load diagram grammar rules
                rules_file = Path(__file__).parent.parent / "data" / "graphviz.txt"
                
                diagram_gen = DiagramGenerator(
                    sysname=sysname,
                    seed=self.config.seed + i,  # Different seed for each diagram
                    rules_file=rules_file if rules_file.exists() else None
                )
                
                # Generate directed graph
                graph = diagram_gen.generate_directed_graph(num_nodes=random.randint(6, 12))
                
                # Save as DOT file
                dot_path = output_dir / f"dia{i}.dot"
                diagram_gen.save_dot(graph, dot_path)
                
                # Convert to EPS if dot command available
                eps_path = output_dir / f"dia{i}.eps"
                if shutil.which("dot"):
                    subprocess.run(
                        ["dot", "-Teps", str(dot_path), "-o", str(eps_path)],
                        check=True,
                        capture_output=True
                    )
                    generated_files.append(eps_path)
                    print(f"Generated diagram: {eps_path}")
                else:
                    print(f"Warning: 'dot' command not found. Install Graphviz to generate .eps files.")
                    print(f"DOT file saved: {dot_path}")
                    generated_files.append(dot_path)
                    
            except Exception as e:
                print(f"Warning: Failed to generate diagram {i}: {e}")
        
        return generated_files
    
    def generate_figures(self, output_dir: Path) -> List[Path]:
        """Generate figure/graph files referenced in the paper.
        
        Args:
            output_dir: Directory to save figure files.
            
        Returns:
            List of generated figure file paths.
        """
        if not GRAPH_AVAILABLE:
            print("Warning: matplotlib not available, skipping figure generation")
            return []
        
        output_dir.mkdir(parents=True, exist_ok=True)
        generated_files = []
        
        # Generate figures (typically figure0.eps, figure1.eps, etc.)
        # Increase to match typical paper generation (up to 6 figures)
        num_figures = 6
        
        graph_types = ['line', 'bar']
        
        for i in range(num_figures):
            try:
                graph_gen = GraphGenerator(seed=self.config.seed + i + 100, color=False)
                
                # Randomly choose graph type
                graph_type = random.choice(graph_types)
                
                if graph_type == 'line':
                    fig = graph_gen.generate_line_plot(
                        num_lines=random.randint(2, 4),
                        xlabel=self.engine.expand("GRAPH_X_AXIS"),
                        ylabel=self.engine.expand("GRAPH_Y_AXIS"),
                        title=""
                    )
                else:  # bar
                    fig = graph_gen.generate_bar_chart(
                        num_bars=random.randint(4, 8),
                        xlabel=self.engine.expand("GRAPH_X_AXIS"),
                        ylabel=self.engine.expand("GRAPH_Y_AXIS"),
                        title=""
                    )
                
                # Save as EPS
                eps_path = output_dir / f"figure{i}.eps"
                graph_gen.save(fig, eps_path, format='eps')
                generated_files.append(eps_path)
                print(f"Generated figure: {eps_path}")
                
            except Exception as e:
                print(f"Warning: Failed to generate figure {i}: {e}")
        
        return generated_files
    
    @staticmethod
    def compile_pdf(tex_file: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Compile LaTeX file to PDF using pdflatex and bibtex.
        
        Args:
            tex_file: Path to .tex file.
            output_dir: Output directory (defaults to tex_file's directory).
            
        Returns:
            Path to generated PDF file, or None if compilation failed.
        """
        if not shutil.which("pdflatex"):
            print("Error: pdflatex not found. Please install a LaTeX distribution (e.g., TeX Live, MiKTeX)")
            return None
        
        output_dir = output_dir or tex_file.parent
        tex_file = tex_file.resolve()
        output_dir = output_dir.resolve()
        base_name = tex_file.stem
        
        # Check if .bib file exists
        bib_file = output_dir / f"{base_name}.bib"
        has_bib = bib_file.exists()
        
        if has_bib:
            # Also check for references.bib (the name used in \bibliography{references})
            ref_bib = output_dir / "references.bib"
            if not ref_bib.exists() and bib_file.exists():
                # Copy the .bib file to references.bib
                shutil.copy(bib_file, ref_bib)
                print(f"Copied {bib_file.name} to references.bib")
        
        try:
            # Run pdflatex first time (with -shell-escape for EPS conversion)
            print("Running pdflatex (pass 1/3)...")
            subprocess.run(
                ["pdflatex", "-shell-escape", "-interaction=nonstopmode", "-output-directory", str(output_dir), str(tex_file)],
                capture_output=True,
                cwd=output_dir,
                check=False
            )
            
            # Run bibtex if .bib file exists
            if has_bib and shutil.which("bibtex"):
                print("Running bibtex...")
                subprocess.run(
                    ["bibtex", base_name],
                    capture_output=True,
                    cwd=output_dir,
                    check=False
                )
            
            # Run pdflatex second time (for bibtex references)
            print("Running pdflatex (pass 2/3)...")
            subprocess.run(
                ["pdflatex", "-shell-escape", "-interaction=nonstopmode", "-output-directory", str(output_dir), str(tex_file)],
                capture_output=True,
                cwd=output_dir,
                check=False
            )
            
            # Run pdflatex third time (for cross-references)
            print("Running pdflatex (pass 3/3)...")
            result = subprocess.run(
                ["pdflatex", "-shell-escape", "-interaction=nonstopmode", "-output-directory", str(output_dir), str(tex_file)],
                capture_output=True,
                cwd=output_dir,
                check=False
            )
            
            if result.returncode != 0:
                print(f"Warning: pdflatex exited with code {result.returncode}")
                # Still might have generated PDF
                
        except Exception as e:
            print(f"Error during PDF compilation: {e}")
            return None
        
        pdf_path = output_dir / f"{base_name}.pdf"
        if pdf_path.exists():
            print(f"✅ PDF generated: {pdf_path}")
            
            # Clean up auxiliary files (keep .log for debugging)
            for ext in ['.aux', '.out', '.bbl', '.blg']:
                aux_file = output_dir / f"{base_name}{ext}"
                if aux_file.exists():
                    try:
                        aux_file.unlink()
                    except:
                        pass
            
            # Clean up the copied references.bib
            ref_bib = output_dir / "references.bib"
            if ref_bib.exists() and ref_bib != bib_file:
                try:
                    ref_bib.unlink()
                except:
                    pass
            
            return pdf_path
        else:
            print("Error: PDF file was not generated")
            # Print last few lines of log for debugging
            log_file = output_dir / f"{base_name}.log"
            if log_file.exists():
                print("\nLast few lines of LaTeX log:")
                log_lines = log_file.read_text().split('\n')
                for line in log_lines[-20:]:
                    if line.strip():
                        print(f"  {line}")
            return None
    
    
    def _parse_bibtex_entry(self, bibtex_text: str, cite_label: str) -> Optional[Reference]:
        """Parse a BibTeX entry string into a Reference object.
        
        Args:
            bibtex_text: Raw BibTeX entry text.
            cite_label: Citation label.
            
        Returns:
            Reference object or None if parsing fails.
        """
        import re
        
        # Extract entry type
        entry_match = re.search(r'@(\w+)\s*\{', bibtex_text)
        if not entry_match:
            return None
        entry_type = entry_match.group(1).lower()
        
        # Extract fields
        fields = {}
        field_pattern = re.compile(r'(\w+)\s*=\s*\{([^}]+)\}|(\w+)\s*=\s*(\S+)')
        for match in field_pattern.finditer(bibtex_text):
            if match.group(1):
                field_name = match.group(1)
                field_value = match.group(2)
            else:
                field_name = match.group(3)
                field_value = match.group(4)
            fields[field_name] = field_value
        
        return Reference(
            key=cite_label,
            entry_type=entry_type,
            fields=fields
        )
    


class SimplePaperGenerator:
    """Simplified paper generator for basic use cases.
    
    This generator provides a simpler interface when you just need
    to generate text without full paper structure.
    """
    
    def __init__(self, rules_file: Path, seed: Optional[int] = None):
        """Initialize simple generator.
        
        Args:
            rules_file: Path to rules file.
            seed: Optional random seed.
        """
        if seed is not None:
            random.seed(seed)
        
        ruleset = RuleSet()
        self.engine = GrammarEngine(ruleset)
        self.engine.load_rules(rules_file)
    
    def generate(self, start_symbol: str = "START", pretty: bool = False) -> str:
        """Generate text from a starting symbol.
        
        Args:
            start_symbol: Starting rule name.
            pretty: Whether to apply pretty printing.
            
        Returns:
            Generated text.
        """
        text = self.engine.expand(start_symbol)
        
        if pretty:
            processor = TextProcessor()
            text = processor.pretty_print(text)
        
        return text
