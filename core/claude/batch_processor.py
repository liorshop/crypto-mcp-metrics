import asyncio
from typing import List, Dict, Any, Optional
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from ..utils.monitoring import PerformanceMonitor
from ..utils.error_handler import BatchProcessingError

@dataclass
class BatchRequest:
    """Represents a batched request to Claude"""
    id: str
    data: Dict[str, Any]
    priority: int
    timestamp: datetime
    future: asyncio.Future

class BatchProcessor:
    """Handles batched requests to Claude.ai"""
    
    def __init__(self, 
                 config: Dict[str, Any],
                 client: 'ClaudeClient'):
        self.config = config
        self.client = client
        self.batch_size = config.get('BATCH_SIZE', 5)
        self.batch_timeout = config.get('BATCH_TIMEOUT', 1.0)
        self.max_retries = config.get('MAX_RETRIES', 3)
        self.queue = asyncio.PriorityQueue()
        self.processing = False
        self.monitor = PerformanceMonitor()

    async def submit(self,
                    data: Dict[str, Any],
                    priority: int = 0) -> Dict[str, Any]:
        """Submit a request for batch processing"""
        future = asyncio.Future()
        request = BatchRequest(
            id=str(hash(str(data))),
            data=data,
            priority=priority,
            timestamp=datetime.now(),
            future=future
        )

        await self.queue.put((priority, request))
        
        if not self.processing:
            asyncio.create_task(self._process_batches())

        return await future

    async def _process_batches(self) -> None:
        """Process batched requests"""
        self.processing = True

        try:
            while not self.queue.empty():
                batch = await self._collect_batch()
                if not batch:
                    continue

                try:
                    results = await self._process_batch(batch)
                    self._distribute_results(batch, results)
                except Exception as e:
                    await self._handle_batch_error(batch, e)

        finally:
            self.processing = False

    async def _collect_batch(self) -> List[BatchRequest]:
        """Collect requests into a batch"""
        batch = []
        start_time = datetime.now()

        while len(batch) < self.batch_size:
            try:
                # Try to get a request with timeout
                _, request = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=self.batch_timeout
                )
                batch.append(request)

            except asyncio.TimeoutError:
                break

            # Check if we've exceeded batch timeout
            if (datetime.now() - start_time).total_seconds() >= self.batch_timeout:
                break

        return batch

    async def _process_batch(self,
                           batch: List[BatchRequest]) -> List[Dict[str, Any]]:
        """Process a batch of requests"""
        with self.monitor.measure('batch_processing'):
            try:
                # Combine requests into a single context
                combined_context = self._combine_contexts(
                    [req.data for req in batch]
                )

                # Process with Claude
                response = await self.client.process_request(combined_context)

                # Split response back into individual results
                return self._split_response(response, len(batch))

            except Exception as e:
                raise BatchProcessingError(
                    f'Failed to process batch: {str(e)}'
                )

    def _combine_contexts(self, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple contexts into a single request"""
        return {
            'type': 'batch',
            'requests': contexts,
            'batch_size': len(contexts)
        }

    def _split_response(self,
                       response: Dict[str, Any],
                       batch_size: int) -> List[Dict[str, Any]]:
        """Split batched response into individual results"""
        if 'results' not in response or len(response['results']) != batch_size:
            raise BatchProcessingError('Invalid batch response format')

        return response['results']

    def _distribute_results(self,
                          batch: List[BatchRequest],
                          results: List[Dict[str, Any]]) -> None:
        """Distribute results to individual futures"""
        for request, result in zip(batch, results):
            if not request.future.done():
                request.future.set_result(result)

    async def _handle_batch_error(self,
                                batch: List[BatchRequest],
                                error: Exception) -> None:
        """Handle errors in batch processing"""
        self.monitor.record_metric('batch_errors', 1)

        # Attempt individual processing
        for request in batch:
            if request.future.done():
                continue

            try:
                result = await self._process_with_retry(request)
                request.future.set_result(result)
            except Exception as e:
                request.future.set_exception(e)

    async def _process_with_retry(self,
                                request: BatchRequest,
                                attempt: int = 0) -> Dict[str, Any]:
        """Process a single request with retry"""
        try:
            return await self.client.process_request(request.data)
        except Exception as e:
            if attempt < self.max_retries:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                return await self._process_with_retry(request, attempt + 1)
            raise e