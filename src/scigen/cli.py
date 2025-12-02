"""Command-line interface for SCIgen."""

import sys
import random
from pathlib import Path
from typing import Optional
import click

from scigen import __version__
from scigen.config import GeneratorConfig
from scigen.generators.paper import PaperGenerator, SimplePaperGenerator


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """SCIgen - Automatic Computer Science Paper Generator.
    
    Generate fake but realistic-looking CS research papers, complete with
    graphs, figures, and citations.
    """
    pass


@cli.command()
@click.option(
    "--author",
    "-a",
    multiple=True,
    help="Author name (can be specified multiple times)"
)
@click.option(
    "--seed",
    "-s",
    type=int,
    help="Random seed for reproducibility"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="output/paper.tex",
    help="Output LaTeX file path"
)
@click.option(
    "--pdf",
    is_flag=True,
    help="Also generate PDF (requires pdflatex)"
)
@click.option(
    "--figures",
    is_flag=True,
    default=True,
    help="Generate figures and diagrams (default: True)"
)
@click.option(
    "--debug",
    "-d",
    count=True,
    help="Debug level (repeat for more verbosity)"
)
@click.option(
    "--no-pretty",
    is_flag=True,
    help="Disable pretty printing"
)
def generate_paper(
    author: tuple,
    seed: Optional[int],
    output: str,
    pdf: bool,
    figures: bool,
    debug: int,
    no_pretty: bool
) -> None:
    """Generate a complete scientific paper with figures and optional PDF output."""
    
    # Set defaults
    if not author:
        author = ("Alice Smith", "Bob Jones")
    
    if seed is None:
        seed = random.randint(0, 0xFFFFFFFF)
        click.echo(f"Using random seed: {seed}")
    
    output_path = Path(output)
    output_dir = output_path.parent
    
    # Configure generator
    config = GeneratorConfig(
        seed=seed,
        authors=list(author),
        pretty_print=not no_pretty,
        debug_level=debug,
        output_dir=output_dir
    )
    
    click.echo(f"Generating paper with {len(author)} author(s)...")
    
    # Generate paper
    generator = PaperGenerator(config)
    paper = generator.generate()
    
    # Save LaTeX
    output_dir.mkdir(parents=True, exist_ok=True)
    paper.save_latex(output_path)
    click.echo(f"✅ Saved LaTeX: {output_path}")
    
    # Save BibTeX
    bib_path = output_path.with_suffix('.bib')
    paper.save_bibtex(bib_path)
    click.echo(f"✅ Saved BibTeX: {bib_path}")
    
    # Generate figures and diagrams
    if figures:
        click.echo("\nGenerating figures and diagrams...")
        
        # Generate diagrams
        diagram_files = generator.generate_diagrams(output_dir)
        if diagram_files:
            click.echo(f"✅ Generated {len(diagram_files)} diagram(s)")
        
        # Generate figures/graphs
        figure_files = generator.generate_figures(output_dir)
        if figure_files:
            click.echo(f"✅ Generated {len(figure_files)} figure(s)")
    
    # Generate PDF if requested
    if pdf:
        click.echo("\nCompiling PDF...")
        pdf_path = PaperGenerator.compile_pdf(output_path, output_dir)
        if pdf_path:
            click.echo(f"✅ PDF complete: {pdf_path}")
        else:
            click.echo("❌ PDF compilation failed")
            click.echo("   Make sure LaTeX is installed (TeX Live, MiKTeX, etc.)")
    
    click.echo("\nDone!")


@cli.command()
@click.option(
    "--seed",
    "-s",
    type=int,
    help="Random seed for reproducibility"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="output/graph.eps",
    help="Output file path"
)
@click.option(
    "--type",
    "-t",
    type=click.Choice(['line', 'scatter', 'bar']),
    default='line',
    help="Type of graph to generate"
)
@click.option(
    "--color",
    is_flag=True,
    help="Generate color graph"
)
def generate_graph(
    seed: Optional[int],
    output: str,
    type: str,
    color: bool
) -> None:
    """Generate a scientific graph/plot."""
    
    try:
        from scigen.generators.graph import GraphGenerator
    except ImportError:
        click.echo("Error: matplotlib is required for graph generation", err=True)
        click.echo("Install it with: pip install matplotlib", err=True)
        sys.exit(1)
    
    if seed is None:
        seed = random.randint(0, 0xFFFFFFFF)
        click.echo(f"Using random seed: {seed}")
    
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    click.echo(f"Generating {type} graph...")
    
    generator = GraphGenerator(seed=seed, color=color)
    
    if type == 'line':
        fig = generator.generate_line_plot()
    elif type == 'scatter':
        fig = generator.generate_scatter_plot()
    elif type == 'bar':
        fig = generator.generate_bar_chart()
    
    # Determine format from extension
    format = output_path.suffix[1:] if output_path.suffix else 'eps'
    
    generator.save(fig, output_path, format=format)
    click.echo(f"Saved graph to: {output_path}")
    click.echo("Done!")


@cli.command()
@click.option(
    "--sysname",
    "-n",
    required=True,
    help="Name of the system to diagram"
)
@click.option(
    "--seed",
    "-s",
    type=int,
    help="Random seed for reproducibility"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="output/diagram.dot",
    help="Output DOT file path"
)
@click.option(
    "--nodes",
    type=int,
    help="Number of nodes (default: random 5-15)"
)
@click.option(
    "--directed/--undirected",
    default=True,
    help="Generate directed or undirected graph"
)
def generate_diagram(
    sysname: str,
    seed: Optional[int],
    output: str,
    nodes: Optional[int],
    directed: bool
) -> None:
    """Generate a system architecture diagram."""
    
    try:
        from scigen.generators.diagram import DiagramGenerator
    except ImportError:
        click.echo("Error: networkx is required for diagram generation", err=True)
        click.echo("Install it with: pip install networkx", err=True)
        sys.exit(1)
    
    if seed is None:
        seed = random.randint(0, 0xFFFFFFFF)
        click.echo(f"Using random seed: {seed}")
    
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    graph_type = "directed" if directed else "undirected"
    click.echo(f"Generating {graph_type} diagram for '{sysname}'...")
    
    generator = DiagramGenerator(sysname=sysname, seed=seed)
    
    if directed:
        graph = generator.generate_directed_graph(num_nodes=nodes)
    else:
        graph = generator.generate_undirected_graph(num_nodes=nodes)
    
    generator.save_dot(graph, output_path)
    click.echo(f"Saved diagram to: {output_path}")
    click.echo(f"To render: dot -Teps {output_path} -o {output_path.with_suffix('.eps')}")
    click.echo("Done!")


@cli.command()
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    required=True,
    help="Grammar rules file"
)
@click.option(
    "--start",
    "-s",
    default="START",
    help="Starting rule symbol"
)
@click.option(
    "--seed",
    type=int,
    help="Random seed"
)
@click.option(
    "--pretty/--no-pretty",
    default=True,
    help="Apply pretty printing"
)
@click.option(
    "--debug",
    "-d",
    count=True,
    help="Debug level"
)
@click.argument("variables", nargs=-1)
def expand(
    file: str,
    start: str,
    seed: Optional[int],
    pretty: bool,
    debug: int,
    variables: tuple
) -> None:
    """Expand a grammar rule (low-level interface).
    
    VARIABLES should be in the form NAME=VALUE.
    """
    
    if seed is None:
        seed = random.randint(0, 0xFFFFFFFF)
    
    generator = SimplePaperGenerator(Path(file), seed=seed)
    generator.engine.debug_level = debug
    
    # Parse and set variables
    for var in variables:
        if '=' in var:
            name, value = var.split('=', 1)
            # Add as a single-expansion rule
            from scigen.models.rules import Rule
            rule = Rule(name=name, expansions=[value])
            generator.engine.ruleset.add_rule(rule)
    
    # Generate
    result = generator.generate(start_symbol=start, pretty=pretty)
    click.echo(result)


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
