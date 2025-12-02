#!/usr/bin/env python3
"""Example script showing how to use SCIgen-py programmatically."""

from pathlib import Path
from scigen.config import GeneratorConfig
from scigen.generators.paper import PaperGenerator


def main():
    """Generate a sample paper."""
    
    # Configure the generator
    config = GeneratorConfig(
        seed=42,  # For reproducibility
        authors=["Dr. Alice Johnson", "Prof. Bob Smith"],
        institution="Fictional University",
        pretty_print=True,
        debug_level=0,
        output_dir=Path("example_output")
    )
    
    print("=" * 60)
    print("SCIgen-py Example: Generating a Fake Research Paper")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Seed: {config.seed}")
    print(f"  Authors: {', '.join(config.authors)}")
    print(f"  Institution: {config.institution}")
    print(f"  Output directory: {config.output_dir}")
    print()
    
    # Create generator
    print("Initializing generator...")
    generator = PaperGenerator(config)
    
    # Generate paper (note: requires rules file to be present)
    print("Generating paper...")
    try:
        paper = generator.generate()
        
        print(f"\nPaper generated successfully!")
        print(f"  Title: {paper.title}")
        print(f"  Authors: {len(paper.authors)}")
        print(f"  Sections: {len(paper.sections)}")
        print(f"  References: {len(paper.references)}")
        
        # Save outputs
        output_dir = config.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        tex_file = output_dir / "example_paper.tex"
        bib_file = output_dir / "example_paper.bib"
        
        paper.save_latex(tex_file)
        paper.save_bibtex(bib_file)
        
        print(f"\nFiles saved:")
        print(f"  LaTeX: {tex_file}")
        print(f"  BibTeX: {bib_file}")
        print("\nTo generate PDF:")
        print(f"  cd {output_dir}")
        print(f"  pdflatex example_paper.tex")
        print(f"  bibtex example_paper")
        print(f"  pdflatex example_paper.tex")
        print(f"  pdflatex example_paper.tex")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nNote: This example requires grammar rules to be present.")
        print("Make sure the data directory contains scirules.txt")


if __name__ == "__main__":
    main()
