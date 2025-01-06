import asyncio
import argparse
from typing import Dict, Any, List
from metrics.market_metrics import MarketMetrics
from metrics.volume_metrics import VolumeMetrics
from metrics.social_metrics import SocialMetrics
from metrics.dev_metrics import DevelopmentMetrics
from utils.logging import setup_logger
from utils.error_handler import APIError, ValidationError

logger = setup_logger('main')

class CryptoMetricsCollector:
    """Main class for collecting all crypto metrics"""
    
    def __init__(self):
        self.market_metrics = MarketMetrics()
        self.volume_metrics = VolumeMetrics()
        self.social_metrics = SocialMetrics()
        self.dev_metrics = DevelopmentMetrics()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
    
    async def cleanup(self):
        """Cleanup all resources"""
        await asyncio.gather(
            self.market_metrics.cleanup(),
            self.volume_metrics.cleanup(),
            self.social_metrics.cleanup(),
            self.dev_metrics.cleanup()
        )
    
    async def collect_all_metrics(self, coin_id: str) -> Dict[str, Any]:
        """Collect all metrics for a specific cryptocurrency"""
        try:
            # Collect all metrics concurrently
            market_task = asyncio.create_task(self.market_metrics.collect(coin_id))
            volume_task = asyncio.create_task(self.volume_metrics.collect(coin_id))
            social_task = asyncio.create_task(self.social_metrics.collect(coin_id))
            dev_task = asyncio.create_task(self.dev_metrics.collect(coin_id))
            
            # Wait for all tasks to complete
            results = await asyncio.gather(
                market_task,
                volume_task,
                social_task,
                dev_task,
                return_exceptions=True
            )
            
            # Process results
            metrics = {}
            for result, category in zip(results, ['market', 'volume', 'social', 'development']):
                if isinstance(result, Exception):
                    logger.error(f'Failed to collect {category} metrics: {str(result)}')
                    metrics[category] = {'error': str(result)}
                else:
                    metrics[category] = result
            
            return metrics
            
        except Exception as e:
            logger.error(f'Error collecting metrics: {str(e)}')
            raise

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Collect comprehensive crypto metrics')
    parser.add_argument('coin_id', help='Cryptocurrency identifier (e.g., bitcoin)')
    parser.add_argument('-o', '--output', help='Output file path for JSON results')
    return parser.parse_args()

async def main():
    """Main entry point"""
    args = parse_arguments()
    
    try:
        async with CryptoMetricsCollector() as collector:
            logger.info(f'Collecting metrics for {args.coin_id}...')
            metrics = await collector.collect_all_metrics(args.coin_id)
            
            # Output results
            if args.output:
                import json
                with open(args.output, 'w') as f:
                    json.dump(metrics, f, indent=2)
                logger.info(f'Results saved to {args.output}')
            else:
                import json
                print(json.dumps(metrics, indent=2))
                
    except Exception as e:
        logger.error(f'Failed to collect metrics: {str(e)}')
        raise

if __name__ == '__main__':
    asyncio.run(main())