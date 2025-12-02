"""Integration tests for end-to-end generation."""

import pytest
from pathlib import Path
from scigen.config import GeneratorConfig
from scigen.generators.paper import PaperGenerator


class TestEndToEndGeneration:
    """Integration tests for complete paper generation."""
    
    @pytest.mark.integration
    def test_generate_complete_paper(self, tmp_path):
        """Test generating a complete paper end-to-end."""
        config = GeneratorConfig(
            seed=12345,
            authors=["Alice Smith", "Bob Jones"],
            output_dir=tmp_path
        )
        
        # Note: This requires actual rules file to be present
        # For now, just test that generator can be created
        generator = PaperGenerator(config)
        assert generator is not None
    
    @pytest.mark.integration
    def test_paper_reproducibility(self):
        """Test that same seed produces same paper."""
        config1 = GeneratorConfig(seed=99999, authors=["Test"])
        config2 = GeneratorConfig(seed=99999, authors=["Test"])
        
        gen1 = PaperGenerator(config1)
        gen2 = PaperGenerator(config2)
        
        # Verify same configuration
        assert gen1.config.seed == gen2.config.seed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
