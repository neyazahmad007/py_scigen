"""Graph generation module using matplotlib."""

import random
import math
from pathlib import Path
from typing import List, Tuple, Optional
import io

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from scigen.core.grammar import GrammarEngine
from scigen.models.rules import RuleSet


class GraphGenerator:
    """Generates scientific-looking graphs and plots.
    
    This generator creates various types of graphs commonly found in
    CS papers: line plots, scatter plots, bar charts, etc.
    """
    
    def __init__(self, seed: Optional[int] = None, color: bool = False):
        """Initialize graph generator.
        
        Args:
            seed: Random seed for reproducibility.
            color: Whether to generate color graphs.
        """
        if not MATPLOTLIB_AVAILABLE:
            raise RuntimeError("matplotlib is required for graph generation")
        
        self.seed = seed or random.randint(0, 0xFFFFFFFF)
        self.color = color
        random.seed(self.seed)
        np.random.seed(self.seed)
    
    def generate_line_plot(
        self, 
        num_lines: int = 3,
        num_points: int = 20,
        xlabel: str = "Time (ms)",
        ylabel: str = "Throughput (MB/s)",
        title: str = "System Performance"
    ) -> plt.Figure:
        """Generate a line plot.
        
        Args:
            num_lines: Number of lines to plot.
            num_points: Number of data points per line.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            title: Plot title.
            
        Returns:
            Matplotlib figure.
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        x = np.linspace(0, 100, num_points)
        
        for i in range(num_lines):
            # Generate semi-realistic data with trend and noise
            trend = random.choice(['increasing', 'decreasing', 'stable'])
            
            if trend == 'increasing':
                y = x * random.uniform(0.5, 2.0) + random.uniform(0, 50)
            elif trend == 'decreasing':
                y = -x * random.uniform(0.5, 2.0) + random.uniform(50, 150)
            else:
                y = np.ones_like(x) * random.uniform(20, 80)
            
            # Add noise
            noise = np.random.normal(0, random.uniform(2, 10), num_points)
            y = y + noise
            
            # Ensure non-negative
            y = np.maximum(y, 0)
            
            label = f"Method {i+1}"
            if self.color:
                ax.plot(x, y, marker='o', label=label, linewidth=2)
            else:
                markers = ['o', 's', '^', 'D', 'v']
                linestyles = ['-', '--', '-.', ':']
                ax.plot(
                    x, y,
                    marker=markers[i % len(markers)],
                    linestyle=linestyles[i % len(linestyles)],
                    label=label,
                    color='black',
                    linewidth=2
                )
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def generate_scatter_plot(
        self,
        num_points: int = 100,
        xlabel: str = "Latency (ms)",
        ylabel: str = "Bandwidth (MB/s)",
        title: str = "Performance Scatter"
    ) -> plt.Figure:
        """Generate a scatter plot.
        
        Args:
            num_points: Number of data points.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            title: Plot title.
            
        Returns:
            Matplotlib figure.
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Generate correlated data with noise
        x = np.random.uniform(0, 100, num_points)
        correlation = random.choice([-0.8, -0.5, 0.0, 0.5, 0.8])
        y = x * correlation + np.random.normal(50, 15, num_points)
        y = np.maximum(y, 0)
        
        if self.color:
            ax.scatter(x, y, alpha=0.6, s=50)
        else:
            ax.scatter(x, y, alpha=0.6, s=50, color='black', marker='o')
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def generate_bar_chart(
        self,
        num_bars: int = 10,
        xlabel: str = "Configuration",
        ylabel: str = "Performance (ops/sec)",
        title: str = "Benchmark Results"
    ) -> plt.Figure:
        """Generate a bar chart.
        
        Args:
            num_bars: Number of bars.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            title: Plot title.
            
        Returns:
            Matplotlib figure.
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(num_bars)
        heights = np.random.uniform(20, 100, num_bars)
        
        if self.color:
            ax.bar(x, heights, width=0.6)
        else:
            ax.bar(x, heights, width=0.6, color='gray', edgecolor='black')
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels([f"C{i+1}" for i in range(num_bars)])
        ax.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def save(self, fig: plt.Figure, output_path: Path, format: str = 'eps') -> None:
        """Save figure to file.
        
        Args:
            fig: Matplotlib figure.
            output_path: Output file path.
            format: Output format (eps, pdf, png, etc.).
        """
        fig.savefig(output_path, format=format, dpi=300, bbox_inches='tight')
        plt.close(fig)


class GrammarBasedGraphGenerator:
    """Graph generator that uses grammar rules for labels.
    
    This generator loads grammar rules and uses them to generate
    realistic-looking labels and titles for graphs.
    """
    
    def __init__(
        self,
        rules_file: Path,
        seed: Optional[int] = None,
        color: bool = False
    ):
        """Initialize grammar-based graph generator.
        
        Args:
            rules_file: Path to grammar rules file.
            seed: Random seed.
            color: Whether to use color.
        """
        self.seed = seed or random.randint(0, 0xFFFFFFFF)
        random.seed(self.seed)
        
        # Load grammar
        ruleset = RuleSet()
        self.engine = GrammarEngine(ruleset, debug_level=0)
        if rules_file.exists():
            self.engine.load_rules(rules_file)
        
        # Initialize graph generator
        self.graph_gen = GraphGenerator(seed=self.seed, color=color)
    
    def generate(self, graph_type: str = "line") -> plt.Figure:
        """Generate a graph with grammar-generated labels.
        
        Args:
            graph_type: Type of graph ('line', 'scatter', 'bar').
            
        Returns:
            Matplotlib figure.
        """
        # Generate labels from grammar
        try:
            xlabel = self.engine.expand("GRAPH_XLABEL")
            ylabel = self.engine.expand("GRAPH_YLABEL")
            title = self.engine.expand("GRAPH_TITLE")
        except:
            # Fallback to defaults
            xlabel = "X Axis"
            ylabel = "Y Axis"
            title = "Performance"
        
        # Generate appropriate graph type
        if graph_type == "scatter":
            return self.graph_gen.generate_scatter_plot(
                xlabel=xlabel, ylabel=ylabel, title=title
            )
        elif graph_type == "bar":
            return self.graph_gen.generate_bar_chart(
                xlabel=xlabel, ylabel=ylabel, title=title
            )
        else:  # default to line
            return self.graph_gen.generate_line_plot(
                xlabel=xlabel, ylabel=ylabel, title=title
            )
