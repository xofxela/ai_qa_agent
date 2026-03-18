"""
Advanced orchestration utilities for task scheduling and monitoring.

Provides utilities for retry logic, timeout handling, task batching,
and execution monitoring.
"""

import asyncio
import time
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
from enum import Enum
from dataclasses import dataclass

from src.utils.logger import logger


class RetryStrategy(str, Enum):
    """Retry strategy for failed tasks."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    IMMEDIATE = "immediate"


@dataclass
class RetryConfig:
    """Configuration for task retry."""
    max_retries: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    backoff_factor: float = 2.0


class TaskScheduler:
    """Manages task scheduling and execution."""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.task_queue: List[Callable] = []
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, Any] = {}
    
    async def submit(self, task_name: str, task_coro: Any) -> Any:
        """Submit task for execution."""
        async with self.semaphore:
            logger.info(f"Executing task: {task_name}")
            try:
                result = await task_coro
                self.completed_tasks[task_name] = result
                logger.info(f"Task completed: {task_name}")
                return result
            except Exception as e:
                logger.error(f"Task failed: {task_name} - {e}")
                raise
    
    async def submit_batch(self, tasks: Dict[str, Any]) -> Dict[str, Any]:
        """Submit batch of tasks for execution."""
        results = {}
        for task_name, task_coro in tasks.items():
            results[task_name] = await self.submit(task_name, task_coro)
        return results
    
    def get_active_tasks(self) -> List[str]:
        """Get list of active task names."""
        return list(self.active_tasks.keys())
    
    def get_completed_count(self) -> int:
        """Get count of completed tasks."""
        return len(self.completed_tasks)


class TaskRetryHandler:
    """Handles task retries with configurable strategies."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.retry_counts: Dict[str, int] = {}
    
    async def execute_with_retry(
        self,
        task_name: str,
        task_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute task with retry logic."""
        attempt = 0
        last_error = None
        
        while attempt <= self.config.max_retries:
            try:
                logger.info(f"Executing {task_name} (attempt {attempt + 1}/{self.config.max_retries + 1})")
                result = await task_func(*args, **kwargs) if asyncio.iscoroutinefunction(task_func) else task_func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"Task {task_name} succeeded on retry {attempt}")
                
                self.retry_counts[task_name] = attempt
                return result
                
            except Exception as e:
                last_error = e
                attempt += 1
                
                if attempt <= self.config.max_retries:
                    delay = self._calculate_delay(attempt - 1)
                    logger.warning(
                        f"Task {task_name} failed (attempt {attempt}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Task {task_name} failed after {self.config.max_retries} retries")
        
        self.retry_counts[task_name] = self.config.max_retries
        raise last_error or Exception(f"Task {task_name} failed")
    
    def _calculate_delay(self, retry_count: int) -> float:
        """Calculate delay for retry based on strategy."""
        if self.config.strategy == RetryStrategy.IMMEDIATE:
            return 0.0
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.initial_delay * (retry_count + 1)
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.initial_delay * (self.config.backoff_factor ** retry_count)
        else:
            delay = self.config.initial_delay
        
        return min(delay, self.config.max_delay)
    
    def get_retry_count(self, task_name: str) -> int:
        """Get retry count for task."""
        return self.retry_counts.get(task_name, 0)


class TaskMonitor:
    """Monitors task execution and collects metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}
    
    def record_start(self, task_name: str) -> None:
        """Record task start time."""
        self.metrics[task_name] = {
            "start_time": time.time(),
            "end_time": None,
            "duration": None,
            "status": "running"
        }
    
    def record_end(self, task_name: str, status: str = "completed", error: Optional[str] = None) -> None:
        """Record task end time."""
        if task_name not in self.metrics:
            self.metrics[task_name] = {"start_time": time.time()}
        
        end_time = time.time()
        self.metrics[task_name]["end_time"] = end_time
        self.metrics[task_name]["duration"] = end_time - self.metrics[task_name]["start_time"]
        self.metrics[task_name]["status"] = status
        if error:
            self.metrics[task_name]["error"] = error
    
    def get_metrics(self, task_name: str) -> Dict[str, Any]:
        """Get metrics for task."""
        return self.metrics.get(task_name, {})
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all recorded metrics."""
        return self.metrics
    
    def get_total_duration(self) -> float:
        """Get total execution duration."""
        if not self.metrics:
            return 0.0
        
        start_times = [m["start_time"] for m in self.metrics.values() if "start_time" in m]
        end_times = [m["end_time"] for m in self.metrics.values() if "end_time" in m]
        
        if start_times and end_times:
            return max(end_times) - min(start_times)
        return 0.0
    
    def get_slowest_task(self) -> Optional[tuple]:
        """Get slowest task by duration."""
        if not self.metrics:
            return None
        
        slowest = max(
            ((name, m["duration"]) for name, m in self.metrics.items() if m.get("duration")),
            key=lambda x: x[1],
            default=None
        )
        return slowest
    
    def print_summary(self) -> None:
        """Print execution summary."""
        logger.info("\n" + "=" * 70)
        logger.info("Task Execution Summary")
        logger.info("=" * 70)
        
        total_duration = self.get_total_duration()
        logger.info(f"Total Duration: {total_duration:.2f}s\n")
        
        logger.info(f"{'Task Name':<30} {'Duration (ms)':<15} {'Status':<15}")
        logger.info("-" * 60)
        
        for task_name, metrics in sorted(self.metrics.items()):
            duration = metrics.get("duration", 0) * 1000
            status = metrics.get("status", "unknown")
            logger.info(f"{task_name:<30} {duration:<15.2f} {status:<15}")
        
        slowest = self.get_slowest_task()
        if slowest:
            logger.info(f"\nSlowest Task: {slowest[0]} ({slowest[1]:.2f}s)")
        
        logger.info("=" * 70 + "\n")


def with_retry(
    max_retries: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
):
    """Decorator for adding retry logic to async functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            config = RetryConfig(max_retries=max_retries, strategy=strategy)
            handler = TaskRetryHandler(config)
            return await handler.execute_with_retry(func.__name__, func, *args, **kwargs)
        return wrapper
    return decorator


def with_timeout(timeout_seconds: int):
    """Decorator for adding timeout to async functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.error(f"Task {func.__name__} timed out after {timeout_seconds}s")
                raise
        return wrapper
    return decorator


def with_monitoring(monitor: TaskMonitor):
    """Decorator for monitoring task execution."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            task_name = func.__name__
            monitor.record_start(task_name)
            try:
                result = await func(*args, **kwargs)
                monitor.record_end(task_name, "completed")
                return result
            except Exception as e:
                monitor.record_end(task_name, "failed", str(e))
                raise
        return wrapper
    return decorator
