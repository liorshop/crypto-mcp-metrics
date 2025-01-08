from typing import Dict, Any
from string import Template

class PromptManager:
    """Manages prompt generation for Claude interactions"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.metrics = MetricsCollector()

    def generate_prompt(self, context: Dict[str, Any], template_name: str) -> str:
        """Generate a prompt from context using specified template"""
        try:
            template = self.templates.get(template_name)
            if not template:
                raise ValueError(f'Template not found: {template_name}')

            return template.safe_substitute(context)

        except Exception as e:
            logger.error(f'Prompt generation failed: {str(e)}')
            raise

    def _load_templates(self) -> Dict[str, Template]:
        """Load prompt templates"""
        return {
            'market_analysis': Template("""
                Analyze the following cryptocurrency metrics:
                Market Data: ${market_metrics}
                Volume Data: ${volume_metrics}
                
                Provide insights on:
                1. Market trends
                2. Volume patterns
                3. Key indicators
                4. Risk factors
            """),
            
            'technical_analysis': Template("""
                Perform technical analysis on:
                Price Data: ${price_data}
                Volume Data: ${volume_data}
                
                Include:
                1. Support/Resistance levels
                2. Trend analysis
                3. Volume profile
                4. Key technical indicators
            """),
            
            'sentiment_analysis': Template("""
                Analyze sentiment metrics:
                Social Data: ${social_metrics}
                Development Data: ${dev_metrics}
                
                Provide insights on:
                1. Community sentiment
                2. Development activity
                3. Key trends
                4. Risk indicators
            """)
        }