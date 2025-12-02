"""Configuration management for SCIgen."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List
import random


@dataclass
class GeneratorConfig:
    """Configuration for paper generation.
    
    Attributes:
        seed: Random seed for reproducibility. If None, uses random seed.
        authors: List of author names for the paper.
        institution: Institution name for authors.
        pretty_print: Whether to apply pretty printing to output.
        debug_level: Debug verbosity level (0=none, 1=info, 2+=verbose).
        data_dir: Directory containing grammar rules and templates.
        output_dir: Directory for generated outputs.
    """
    
    seed: Optional[int] = None
    authors: List[str] = field(default_factory=lambda: ["John Doe"])
    institution: str = "MIT CSAIL"
    pretty_print: bool = True
    debug_level: int = 0
    data_dir: Optional[Path] = None
    output_dir: Path = field(default_factory=lambda: Path("output"))
    
    def __post_init__(self) -> None:
        """Initialize configuration after dataclass creation."""
        if self.seed is None:
            self.seed = random.randint(0, 0xFFFFFFFF)
        
        # Set default data directory relative to package
        if self.data_dir is None:
            self.data_dir = Path(__file__).parent / "data"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize random seed
        random.seed(self.seed)
    
    @property
    def rules_file(self) -> Path:
        """Path to main grammar rules file."""
        return self.data_dir / "scirules.txt"
    
    @property
    def graphviz_rules_file(self) -> Path:
        """Path to graphviz rules file."""
        return self.data_dir / "graphviz.txt"
    
    @property
    def functions_file(self) -> Path:
        """Path to functions data file."""
        return self.data_dir / "functions.txt"


@dataclass
class LogConfig:
    """Logging configuration.
    
    Attributes:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format: Log message format string.
        file: Optional log file path.
        structured: Whether to use structured logging (JSON).
    """
    
    level: str = "INFO"
    format: str = "{time} | {level} | {message}"
    file: Optional[Path] = None
    structured: bool = False
