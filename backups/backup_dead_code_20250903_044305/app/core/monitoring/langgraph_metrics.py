"""
from __future__ import annotations

LangGraph-specific metrics collection and monitoring.
"""
import asyncio
import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Deque, Dict, List, Optional, Set, Tuple, Union, Generator
import psutil
logger = logging.getLogger(__name__)

class NodeStatus(Enum): STARTED = 'started'
    SUCCESS = 'success'
    FAILED = 'failed'
    TIMEOUT = 'timeout'
    SKIPPED = 'skipped'
    RETRYING = 'retrying'
    CANCELLED = 'cancelled'

class WorkflowStatus(Enum): STARTED = 'started'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    TIMEOUT = 'timeout'

@dataclass
class NodeExecution:
    """Data class for node execution details."""
    node_name: str
    start_time: float
    end_time: Optional[float] = None
    status: NodeStatus = NodeStatus.STARTED
    error: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: Optional[float] = None

@dataclass
class WorkflowExecution:
    """Data class for workflow execution details."""
    workflow_id: str
    workflow_type: str
    start_time: float
    end_time: Optional[float] = None
    status: WorkflowStatus = WorkflowStatus.STARTED
    nodes: List[NodeExecution] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class NodeExecutionTracker:
    """Tracks execution of individual LangGraph nodes."""

    def __init__(self, max_history: int=1000):
        """Initialize node execution tracker.

        Args:
            max_history: Maximum number of executions to keep in history
        """
        self.max_history = max_history
        self._executions: Deque[NodeExecution] = deque(maxlen=max_history)
        self._active_nodes: Dict[str, NodeExecution] = {}
        self._node_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {'total_executions': 0, 'successful': 0, 'failed': 0, 'timeouts': 0, 'total_duration': 0.0, 'min_duration': float('inf'), 'max_duration': 0.0, 'avg_duration': 0.0, 'retry_counts': [], 'total_started': 0, 'executing': 0})
        self._retry_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {'total_retries': 0, 'successful_retries': 0, 'failed_retries': 0, 'retry_reasons': defaultdict(int)})

    def start_node_execution(self, node_name: str, workflow_id: str=None, metadata: Dict[str, Any]=None, timeout_seconds: Optional[float]=None) -> str:
        """Start tracking a node execution.

        Args:
            node_name: Name of the node
            workflow_id: Associated workflow ID
            metadata: Additional metadata
            timeout_seconds: Optional timeout for node execution

        Returns:
            Execution ID
        """
        exec_id = f'{node_name}_{time.time()}'
        execution = NodeExecution(node_name=node_name, start_time=time.time(), metadata=metadata or {}, timeout_seconds=timeout_seconds)
        if workflow_id:
            execution.metadata['workflow_id'] = workflow_id
        if metadata:
            execution.metadata.update(metadata)
        if timeout_seconds is not None:
            execution.metadata['timeout_seconds'] = timeout_seconds
            execution.metadata['timeout_at'] = time.time() + timeout_seconds
        self._active_nodes[exec_id] = execution
        stats = self._node_stats[node_name]
        stats['total_started'] += 1
        stats['executing'] += 1
        return exec_id

    def complete_node_execution(self, node_id: str, status: str='success', output_size_bytes: int=None, records_processed: int=None, error: Optional[str]=None) -> Dict[str, Any]:
        """Complete a node execution.

        Args:
            node_id: Execution ID
            status: Final status of the node
            output_size_bytes: Size of output data
            records_processed: Number of records processed
            error: Error message if failed

        Returns:
            Execution metrics
        """
        if node_id not in self._active_nodes:
            logger.warning(f'Unknown execution ID: {node_id}')
            return {}
        execution = self._active_nodes.pop(node_id)
        execution.end_time = time.time()
        status_map = {'success': NodeStatus.SUCCESS, 'failed': NodeStatus.FAILED, 'timeout': NodeStatus.TIMEOUT, 'cancelled': NodeStatus.CANCELLED}
        execution.status = status_map.get(status, NodeStatus.SUCCESS)
        execution.error = error
        duration = execution.end_time - execution.start_time
        stats = self._node_stats[execution.node_name]
        stats['total_executions'] += 1
        stats['executing'] -= 1
        if execution.status == NodeStatus.SUCCESS:
            stats['successful'] += 1
        elif execution.status == NodeStatus.FAILED:
            stats['failed'] += 1
        elif execution.status == NodeStatus.TIMEOUT:
            stats['timeouts'] += 1
        stats['total_duration'] += duration
        stats['min_duration'] = min(stats['min_duration'], duration)
        stats['max_duration'] = max(stats['max_duration'], duration)
        stats['avg_duration'] = stats['total_duration'] / stats['total_executions']
        if execution.retry_count > 0:
            stats['retry_counts'].append(execution.retry_count)
        self._executions.append(execution)
        metrics = {'status': status, 'duration_ms': duration * 1000, 'node_name': execution.node_name}
        if output_size_bytes is not None:
            metrics['output_size_bytes'] = output_size_bytes
        if records_processed is not None:
            metrics['records_processed'] = records_processed
        return metrics

    def fail_node_execution(self, node_id: str, error_type: str, error_message: str, stack_trace: Optional[str]=None) -> Any:
        """Mark a node execution as failed.

        Args:
            node_id: Execution ID
            error_type: Type of error
            error_message: Error description
            stack_trace: Optional stack trace for debugging

        Returns:
            Dict containing execution metrics
        """
        error_details = f'{error_type}: {error_message}'
        if stack_trace:
            error_details += f'\nStack trace:\n{stack_trace}'
        metrics = self.complete_node_execution(node_id=node_id, status='failed', error=error_details)
        if metrics:
            metrics['error_type'] = error_type
            metrics['error_message'] = error_message
            if stack_trace:
                metrics['stack_trace'] = stack_trace
        return metrics

    def check_timeout(self, node_id: str) -> bool:
        """Check if a node execution has timed out.

        Args:
            node_id: Execution ID to check

        Returns:
            True if the node has timed out, False otherwise
        """
        if node_id not in self._active_nodes:
            return False
        node = self._active_nodes[node_id]
        if node.timeout_seconds is None:
            return False
        elapsed = time.time() - node.start_time
        return elapsed > node.timeout_seconds

    def timeout_node_execution(self, node_id: str) -> Dict[str, Any]:
        """Mark a node execution as timed out.

        Args:
            node_id: Execution ID

        Returns:
            Execution metrics with timeout status
        """
        return self.complete_node_execution(node_id=node_id, status='timeout', error='Node execution timed out')

    def start_node_retry(self, original_node_id: str, retry_attempt: int, retry_reason: str) -> str:
        """Start a retry of a failed node execution.

        Args:
            original_node_id: ID of the original failed execution
            retry_attempt: Number of retry attempt
            retry_reason: Reason for retry

        Returns:
            New execution ID for the retry
        """
        original_exec = None
        for exec in self._executions:
            if hasattr(exec, 'exec_id') and exec.exec_id == original_node_id:
                original_exec = exec
                break
        if not original_exec:
            for exec in self._executions:
                if exec.node_name in original_node_id:
                    original_exec = exec
                    break
        if not original_exec:
            node_name = original_node_id.split('_')[0] if '_' in original_node_id else 'unknown'
        else:
            node_name = original_exec.node_name
        retry_id = self.start_node_execution(node_name=node_name, metadata={'retry_attempt': retry_attempt, 'retry_reason': retry_reason, 'original_node_id': original_node_id})
        retry_stats = self._retry_stats[node_name]
        retry_stats['total_retries'] += 1
        retry_stats['retry_reasons'][retry_reason] += 1
        if retry_id in self._active_nodes:
            self._active_nodes[retry_id].retry_count = retry_attempt
        return retry_id

    def is_node_executing(self, node_id: str) -> bool:
        """Check if a node is currently executing.

        Args:
            node_id: Execution ID

        Returns:
            True if node is executing
        """
        return node_id in self._active_nodes

    def get_node_details(self, node_id: str) -> Dict[str, Any]:
        """Get detailed information about a node execution.

        Args:
            node_id: Execution ID

        Returns:
            Node execution details
        """
        if node_id in self._active_nodes:
            execution = self._active_nodes[node_id]
            return {'node_name': execution.node_name, 'workflow_id': execution.metadata.get('workflow_id'), 'status': 'executing', 'start_time': execution.start_time, 'metadata': execution.metadata}
        for exec in self._executions:
            if hasattr(exec, 'exec_id') and exec.exec_id == node_id:
                return {'node_name': exec.node_name, 'workflow_id': exec.metadata.get('workflow_id'), 'status': exec.status.value if exec.status else 'unknown', 'start_time': exec.start_time, 'end_time': exec.end_time, 'duration': exec.end_time - exec.start_time if exec.end_time else None, 'metadata': exec.metadata}
        return {}

    def get_executing_count(self) -> int:
        """Get count of currently executing nodes.

        Returns:
            Number of executing nodes
        """
        return len(self._active_nodes)

    def get_executing_nodes(self, workflow_id: str=None) -> List[str]:
        """Get list of currently executing node IDs.

        Args:
            workflow_id: Optional workflow ID to filter by

        Returns:
            List of executing node IDs
        """
        if workflow_id is None:
            return list(self._active_nodes.keys())
        return [node_id for node_id, execution in self._active_nodes.items() if execution.metadata.get('workflow_id') == workflow_id]

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get aggregated execution statistics.

        Returns:
            Statistics dictionary
        """
        total_started = sum((stats['total_started'] for stats in self._node_stats.values()))
        successful = sum((stats['successful'] for stats in self._node_stats.values()))
        failed = sum((stats['failed'] for stats in self._node_stats.values()))
        executing = len(self._active_nodes)
        return {'total_started': total_started, 'successful': successful, 'failed': failed, 'executing': executing, 'completed': successful + failed, 'nodes': dict(self._node_stats)}

    def get_retry_stats(self, node_name: str) -> Dict[str, Any]:
        """Get retry statistics for a specific node.

        Args:
            node_name: Name of the node

        Returns:
            Retry statistics
        """
        stats = self._retry_stats.get(node_name, {})
        if not stats:
            return {'total_retries': 0, 'successful_retries': 0, 'failed_retries': 0, 'retry_reasons': {}}
        successful_retries = 0
        for exec in self._executions:
            if exec.node_name == node_name and exec.metadata.get('retry_attempt') and (exec.status == NodeStatus.SUCCESS):
                successful_retries += 1
        stats['successful_retries'] = successful_retries
        stats['failed_retries'] = stats['total_retries'] - successful_retries
        return dict(stats)

    def start_node(self, node_name: str, metadata: Dict[str, Any]=None) -> str: return self.start_node_execution(node_name, metadata=metadata)

    def complete_node(self, exec_id: str, status: NodeStatus=NodeStatus.SUCCESS, error: Optional[str]=None) -> None: status_str = 'success' if status == NodeStatus.SUCCESS else 'failed'
        self.complete_node_execution(exec_id, status=status_str, error=error)

    def retry_node(self, exec_id: str) -> None: if exec_id in self._active_nodes:
            self._active_nodes[exec_id].retry_count += 1
            self._active_nodes[exec_id].status = NodeStatus.RETRYING

    def get_active_nodes(self) -> List[str]: return [exec.node_name for exec in self._active_nodes.values()]

    def get_node_stats(self, node_name: Optional[str]=None) -> Dict[str, Any]: if node_name:
            return dict(self._node_stats.get(node_name, {}))
        return dict(self._node_stats)

    def get_failure_rate(self, node_name: str, window_seconds: int=300) -> float: cutoff_time = time.time() - window_seconds
        recent_executions = [exec for exec in self._executions if exec.node_name == node_name and exec.start_time >= cutoff_time]
        if not recent_executions:
            return 0.0
        failures = sum((1 for exec in recent_executions if exec.status == NodeStatus.FAILED))
        return failures / len(recent_executions)

    @contextmanager
    def track_node(self, node_name: str, metadata: Dict[str, Any]=None) -> Generator[Any, None, None]: exec_id = self.start_node_execution(node_name, metadata=metadata)
        try:
            yield exec_id
            self.complete_node_execution(exec_id, 'success')
        except TimeoutError:
            self.complete_node_execution(exec_id, 'timeout', error='Execution timeout')
            raise
        except (ValueError, TypeError) as e:
            self.complete_node_execution(exec_id, 'failed', error=str(e))
            raise

class WorkflowMetricsTracker:
    """Tracks metrics for complete LangGraph workflows."""

    def __init__(self, max_history: int=100):
        """Initialize workflow metrics tracker.

        Args:
            max_history: Maximum number of workflows to keep in history
        """
        self.max_history = max_history
        self._workflows: Deque[WorkflowExecution] = deque(maxlen=max_history)
        self._active_workflows: Dict[str, WorkflowExecution] = {}
        self._workflow_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {'total_executions': 0, 'completed': 0, 'failed': 0, 'cancelled': 0, 'total_duration': 0.0, 'avg_duration': 0.0, 'avg_nodes_per_workflow': 0.0, 'throughput_per_minute': 0.0, 'total_started': 0, 'active': 0})
        self._throughput_window: Deque[Tuple[float, str]] = deque(maxlen=1000)

    def start_workflow(self, workflow_type: str, trigger_source: str='unknown', metadata: Dict[str, Any]=None, timestamp: Optional[Union[float, datetime]]=None) -> str:
        """Start tracking a workflow execution.

        Args:
            workflow_type: Type of workflow
            trigger_source: What triggered the workflow
            metadata: Additional metadata
            timestamp: Optional timestamp for when workflow started (float or datetime)

        Returns:
            Workflow ID
        """
        if timestamp is not None:
            if isinstance(timestamp, datetime):
                start_time = timestamp.timestamp()
            else:
                start_time = timestamp
        else:
            start_time = time.time()
        workflow_id = f'{workflow_type}_{start_time}'
        execution = WorkflowExecution(workflow_id=workflow_id, workflow_type=workflow_type, start_time=start_time, metadata=metadata or {})
        if trigger_source:
            execution.metadata['trigger_source'] = trigger_source
        if metadata:
            execution.metadata.update(metadata)
        self._active_workflows[workflow_id] = execution
        stats = self._workflow_stats[workflow_type]
        stats['total_started'] += 1
        stats['active'] += 1
        return workflow_id

    def is_workflow_active(self, workflow_id: str) -> bool:
        """Check if a workflow is currently active.

        Args:
            workflow_id: Workflow ID

        Returns:
            True if workflow is active
        """
        return workflow_id in self._active_workflows

    def add_node_execution(self, workflow_id: str, node_name: str, duration_ms: float, status: str='success', error_info: Dict[str, Any]=None) -> None:
        """Add a node execution to a workflow.

        Args:
            workflow_id: Workflow ID
            node_name: Name of the node
            duration_ms: Duration in milliseconds
            status: Node execution status
        """
        if workflow_id not in self._active_workflows:
            logger.warning(f'Unknown workflow ID: {workflow_id}')
            return
        node_exec = NodeExecution(node_name=node_name, start_time=time.time() - duration_ms / 1000, end_time=time.time(), status=NodeStatus(status) if isinstance(status, str) else status)
        node_exec.metadata = {'duration_ms': duration_ms}
        if error_info:
            node_exec.error = error_info.get('message', str(error_info))
            node_exec.metadata.update(error_info)
        self._active_workflows[workflow_id].nodes.append(node_exec)

    def complete_workflow(self, workflow_id: str, status: str='completed', output: Dict[str, Any]=None, output_size_bytes: int=None, records_processed: int=None, timestamp: Optional[Union[float, datetime]]=None) -> Dict[str, Any]:
        """Complete a workflow execution.

        Args:
            workflow_id: Workflow ID
            status: Final status of the workflow
            output_size_bytes: Size of output data
            records_processed: Number of records processed

        Returns:
            Workflow metrics summary
        """
        if workflow_id not in self._active_workflows:
            logger.warning(f'Unknown workflow ID: {workflow_id}')
            return {}
        workflow = self._active_workflows.pop(workflow_id)
        if timestamp is not None:
            if isinstance(timestamp, datetime):
                workflow.end_time = timestamp.timestamp()
            else:
                workflow.end_time = timestamp
        else:
            workflow.end_time = time.time()
        status_map = {'completed': WorkflowStatus.COMPLETED, 'success': WorkflowStatus.COMPLETED, 'failed': WorkflowStatus.FAILED, 'cancelled': WorkflowStatus.CANCELLED, 'error': WorkflowStatus.FAILED}
        workflow.status = status_map.get(status, WorkflowStatus.COMPLETED)
        duration = workflow.end_time - workflow.start_time
        stats = self._workflow_stats[workflow.workflow_type]
        stats['total_executions'] += 1
        stats['active'] -= 1
        if workflow.status == WorkflowStatus.COMPLETED:
            stats['completed'] += 1
        elif workflow.status == WorkflowStatus.FAILED:
            stats['failed'] += 1
        elif workflow.status == WorkflowStatus.CANCELLED:
            stats['cancelled'] += 1
        stats['total_duration'] += duration
        stats['avg_duration'] = stats['total_duration'] / stats['total_executions']
        node_count = len(workflow.nodes)
        total_nodes = stats.get('total_nodes', 0) + node_count
        stats['total_nodes'] = total_nodes
        stats['avg_nodes_per_workflow'] = total_nodes / stats['total_executions']
        self._throughput_window.append((workflow.end_time, workflow.workflow_type))
        self.calculate_throughput(workflow.workflow_type)
        self._workflows.append(workflow)
        total_node_duration_ms = sum((node.metadata.get('duration_ms', (node.end_time - node.start_time) * 1000) for node in workflow.nodes if hasattr(node, 'metadata') and node.metadata))
        metrics = {'workflow_id': workflow_id, 'workflow_type': workflow.workflow_type, 'status': status, 'duration_ms': duration * 1000, 'workflow_duration_ms': duration * 1000, 'duration_seconds': duration, 'total_nodes_executed': node_count, 'total_node_duration_ms': total_node_duration_ms, 'metadata': workflow.metadata}
        if output:
            metrics['output'] = output
        if output_size_bytes is not None:
            metrics['output_size_bytes'] = output_size_bytes
        if records_processed is not None:
            metrics['records_processed'] = records_processed
        return metrics

    def fail_workflow(self, workflow_id: str, failure_node: str=None, error_type: str=None, error_message: str=None) -> Dict[str, Any]:
        """Mark a workflow as failed.

        Args:
            workflow_id: Workflow ID
            failure_node: Node that caused the failure
            error_type: Type of error
            error_message: Error description

        Returns:
            Workflow failure metrics
        """
        if workflow_id in self._active_workflows:
            workflow = self._active_workflows[workflow_id]
            successful_nodes = sum((1 for node in workflow.nodes if node.status == NodeStatus.SUCCESS))
            failed_nodes = sum((1 for node in workflow.nodes if node.status == NodeStatus.FAILED))
            if error_type:
                workflow.metadata['error_type'] = error_type
            if error_message:
                workflow.metadata['error_message'] = error_message
            if failure_node:
                workflow.metadata['failure_node'] = failure_node
            metrics = self.complete_workflow(workflow_id, status='failed')
            metrics['successful_nodes'] = successful_nodes
            metrics['failed_nodes'] = failed_nodes
            if failure_node:
                metrics['failure_node'] = failure_node
            if error_type:
                metrics['error_type'] = error_type
            if error_message:
                metrics['error_message'] = error_message
            return metrics
        return {'workflow_id': workflow_id, 'status': 'failed', 'error': 'Workflow not found', 'successful_nodes': 0, 'failed_nodes': 0}

    def cancel_workflow(self, workflow_id: str, cancellation_reason: str=None) -> Dict[str, Any]:
        """Cancel an active workflow.

        Args:
            workflow_id: Workflow ID
            cancellation_reason: Optional reason for cancellation

        Returns:
            Workflow metrics including cancellation details
        """
        if workflow_id not in self._active_workflows:
            return {'status': 'not_found', 'message': f'Workflow {workflow_id} not found in active workflows'}
        workflow = self._active_workflows[workflow_id]
        workflow.status = WorkflowStatus.CANCELLED
        workflow.end_time = time.time()
        nodes_completed = sum((1 for node in workflow.nodes if node.status in [NodeStatus.SUCCESS, NodeStatus.FAILED]))
        self._workflow_stats[workflow.workflow_type]['cancelled'] += 1
        self._workflow_stats[workflow.workflow_type]['active'] -= 1
        self._workflows.append(workflow)
        del self._active_workflows[workflow_id]
        return {'workflow_id': workflow_id, 'status': 'cancelled', 'cancellation_reason': cancellation_reason, 'nodes_completed_before_cancellation': nodes_completed, 'duration': workflow.end_time - workflow.start_time if workflow.end_time else 0, 'workflow_type': workflow.workflow_type}

    def get_workflow_details(self, workflow_id: str) -> Dict[str, Any]:
        """Get detailed information about a workflow.

        Args:
            workflow_id: Workflow ID

        Returns:
            Workflow details
        """
        if workflow_id in self._active_workflows:
            workflow = self._active_workflows[workflow_id]
            return {'workflow_id': workflow_id, 'workflow_type': workflow.workflow_type, 'status': 'active', 'start_time': workflow.start_time, 'duration_so_far': time.time() - workflow.start_time, 'nodes_executed': len(workflow.nodes), 'metadata': workflow.metadata}
        for wf in self._workflows:
            if wf.workflow_id == workflow_id:
                return {'workflow_id': workflow_id, 'workflow_type': wf.workflow_type, 'status': wf.status.value if wf.status else 'unknown', 'start_time': wf.start_time, 'end_time': wf.end_time, 'duration': wf.end_time - wf.start_time if wf.end_time else None, 'nodes_executed': len(wf.nodes), 'metadata': wf.metadata}
        return {}

    def get_active_count(self, workflow_type: Optional[str]=None) -> int:
        """Get count of currently active workflows.

        Args:
            workflow_type: Optional workflow type to filter by

        Returns:
            Number of active workflows
        """
        if workflow_type is None:
            return len(self._active_workflows)
        return sum((1 for wf in self._active_workflows.values() if wf.workflow_type == workflow_type))

    def get_workflow_stats(self, workflow_type: Optional[str]=None) -> Dict[str, Any]:
        """Get statistics for workflows.

        Args:
            workflow_type: Specific workflow type or None for all

        Returns:
            Statistics dictionary
        """
        if workflow_type:
            stats = dict(self._workflow_stats.get(workflow_type, {}))
            stats['active_count'] = sum((1 for wf in self._active_workflows.values() if wf.workflow_type == workflow_type))
            return stats
        all_stats = dict(self._workflow_stats)
        total_active = len(self._active_workflows)
        total_started = sum((s.get('total_started', 0) for s in all_stats.values()))
        total_completed = sum((s.get('completed', 0) for s in all_stats.values()))
        total_failed = sum((s.get('failed', 0) for s in all_stats.values()))
        return {'workflows': all_stats, 'total_started': total_started, 'total_active': total_active, 'total_completed': total_completed, 'total_failed': total_failed}

    def get_performance_stats(self, workflow_type: str) -> Dict[str, Any]:
        """Get performance statistics for a workflow type.

        Args:
            workflow_type: Type of workflow to get stats for

        Returns:
            Performance statistics including percentiles
        """
        stats = self._workflow_stats.get(workflow_type, {})
        recent_workflows = [wf for wf in self._workflows if wf.workflow_type == workflow_type and wf.end_time]
        total_workflows = len([wf for wf in self._workflows if wf.workflow_type == workflow_type])
        successful_workflows = len([wf for wf in self._workflows if wf.workflow_type == workflow_type and wf.status == WorkflowStatus.COMPLETED])
        if not recent_workflows:
            return {'workflow_type': workflow_type, 'sample_size': 0, 'total_workflows': total_workflows, 'successful_workflows': successful_workflows, 'p50_duration_ms': 0.0, 'p90_duration_ms': 0.0, 'p95_duration_ms': 0.0, 'p99_duration_ms': 0.0, 'min_duration_ms': 0.0, 'max_duration_ms': 0.0, 'average_duration_ms': 0.0}
        durations = sorted([wf.end_time - wf.start_time for wf in recent_workflows])

        def percentile(data, p) -> Any:
            """Percentile"""
            if not data:
                return 0.0
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = f + 1 if f < len(data) - 1 else f
            return data[f] if f == c else data[f] + (k - f) * (data[c] - data[f])
        durations_ms = [d * 1000 for d in durations]
        return {'workflow_type': workflow_type, 'sample_size': len(durations), 'total_workflows': total_workflows, 'successful_workflows': successful_workflows, 'p50_duration_ms': percentile(durations_ms, 50), 'p90_duration_ms': percentile(durations_ms, 90), 'p95_duration_ms': percentile(durations_ms, 95), 'p99_duration_ms': percentile(durations_ms, 99), 'min_duration_ms': min(durations_ms) if durations_ms else 0.0, 'max_duration_ms': max(durations_ms) if durations_ms else 0.0, 'average_duration_ms': sum(durations_ms) / len(durations_ms) if durations_ms else 0.0}

    def get_throughput_metrics(self, workflow_type: str, window_minutes: int=5) -> Dict[str, float]:
        """Get throughput metrics for a workflow type.

        Args:
            workflow_type: Type of workflow
            window_minutes: Time window in minutes

        Returns:
            Throughput metrics
        """
        cutoff_time = time.time() - window_minutes * 60
        recent_workflows = [(ts, wf_type) for ts, wf_type in self._throughput_window if ts >= cutoff_time and wf_type == workflow_type]
        if not recent_workflows:
            return {'workflows_per_minute': 0.0, 'avg_per_minute': 0.0, 'peak_per_minute': 0.0}
        minutes_data = defaultdict(int)
        for ts, _ in recent_workflows:
            minute_bucket = int(ts / 60)
            minutes_data[minute_bucket] += 1
        rates = list(minutes_data.values())
        return {'workflows_per_minute': len(recent_workflows) / window_minutes, 'avg_per_minute': sum(rates) / len(rates) if rates else 0, 'peak_per_minute': max(rates) if rates else 0}

    def calculate_throughput(self, workflow_type: str, time_window_seconds: int=60) -> Dict[str, float]:
        """Calculate throughput for a workflow type.

        Args:
            workflow_type: Type of workflow
            time_window_seconds: Time window in seconds for calculation

        Returns:
            Throughput metrics
        """
        cutoff_time = time.time() - time_window_seconds
        recent_workflows = [(ts, wf_type) for ts, wf_type in self._throughput_window if ts >= cutoff_time and wf_type == workflow_type]
        workflow_count = len(recent_workflows)
        workflows_per_second = workflow_count / time_window_seconds if time_window_seconds > 0 else 0
        workflows_per_minute = workflows_per_second * 60
        recent_completed = [wf for wf in self._workflows if wf.workflow_type == workflow_type and wf.end_time is not None and (wf.start_time is not None) and (wf.end_time >= cutoff_time)]
        avg_duration_ms = 0.0
        if recent_completed:
            durations = [(wf.end_time - wf.start_time) * 1000 for wf in recent_completed]
            avg_duration_ms = sum(durations) / len(durations)
        stats = self._workflow_stats[workflow_type]
        stats['throughput_per_minute'] = workflows_per_minute
        return {'workflows_per_second': workflows_per_second, 'workflows_per_minute': workflows_per_minute, 'average_duration_ms': avg_duration_ms}

    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get list of currently active workflows.

        Returns:
            List of workflow summaries
        """
        return [{'workflow_id': wf.workflow_id, 'workflow_type': wf.workflow_type, 'duration_so_far': time.time() - wf.start_time, 'nodes_executed': len(wf.nodes), 'metadata': wf.metadata} for wf in self._active_workflows.values()]

    def set_concurrency_limit(self, workflow_type: str, max_concurrent: int) -> None:
        """Set concurrency limit for a workflow type.

        Args:
            workflow_type: Type of workflow
            max_concurrent: Maximum number of concurrent workflows allowed
        """
        if not hasattr(self, '_concurrency_limits'):
            self._concurrency_limits = {}
        self._concurrency_limits[workflow_type] = max_concurrent

    def can_start_workflow(self, workflow_type: str) -> bool:
        """Check if a new workflow can be started based on concurrency limits.

        Args:
            workflow_type: Type of workflow to check

        Returns:
            True if the workflow can be started, False otherwise
        """
        limit = self._concurrency_limits.get(workflow_type)
        if limit is None:
            return True
        active_count = sum((1 for wf in self._active_workflows.values() if wf.workflow_type == workflow_type))
        return active_count < limit

    def check_concurrency_limit(self, workflow_type: str, limit: int) -> bool:
        """Check if workflow type has reached concurrency limit.

        Args:
            workflow_type: Type of workflow
            limit: Maximum concurrent workflows

        Returns:
            True if limit reached, False otherwise
        """
        active_count = sum((1 for wf in self._active_workflows.values() if wf.workflow_type == workflow_type))
        return active_count >= limit

class StateTransitionTracker:
    """Tracks state transitions in LangGraph workflows."""

    def __init__(self, max_history: int=5000):
        """Initialize state transition tracker.

        Args:
            max_history: Maximum number of transitions to keep
        """
        self.max_history = max_history
        self._transitions: Deque[Dict[str, Any]] = deque(maxlen=max_history)
        self._transition_counts: Dict[Tuple[str, str], int] = defaultdict(int)
        self._state_durations: Dict[str, List[float]] = defaultdict(list)
        self._current_states: Dict[str, Tuple[str, float]] = {}

    def define_state_machine(self, state_machine: Dict[str, Any]) -> None:
        """Define valid state transitions for validation.

        Args:
            state_machine: Dictionary defining valid states and transitions
                          Can be either:
                          1. Simple format: {
                              "state1": ["state2", "state3"],
                              "state2": ["state3"],
                              ...
                          }
                          2. Complex format: {
                              "initial": "state_name",
                              "states": ["state1", "state2", ...],
                              "transitions": {
                                  "state1": ["state2", "state3"],
                                  "state2": ["state3"],
                                  ...
                              }
                          }
        """
        if not hasattr(self, '_state_machines'):
            self._state_machines = {}
        is_simple_format = all((isinstance(v, list) for v in state_machine.values()))
        if is_simple_format:
            states = list(state_machine.keys())
            for transitions in state_machine.values():
                for state in transitions:
                    if state not in states:
                        states.append(state)
            initial_state = states[0] if states else None
            converted_machine = {'initial': initial_state, 'states': states, 'transitions': state_machine}
            state_machine = converted_machine
        self._state_machines['default'] = state_machine
        if 'initial' not in state_machine or state_machine['initial'] is None:
            raise ValueError('State machine must define an initial state')
        if 'states' not in state_machine:
            raise ValueError('State machine must define available states')
        if 'transitions' not in state_machine:
            raise ValueError('State machine must define valid transitions')
        self._valid_states = set(state_machine['states'])
        self._valid_transitions = state_machine['transitions']
        self._initial_state = state_machine['initial']

    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a transition from one state to another is valid.

        Args:
            from_state: The state transitioning from
            to_state: The state transitioning to

        Returns:
            True if the transition is valid, False otherwise
        """
        if not hasattr(self, '_valid_transitions'):
            return True
        if from_state not in self._valid_transitions:
            return False
        return to_state in self._valid_transitions[from_state]

    def record_transition(self, workflow_id: str, from_state: str, to_state: str, metadata: Dict[str, Any]=None, transition_trigger: Optional[str]=None) -> str:
        """Record a state transition.

        Args:
            workflow_id: Workflow ID
            from_state: Previous state
            to_state: New state
            metadata: Additional metadata
            transition_trigger: What triggered the transition

        Returns:
            Transition ID
        """
        transition_time = time.time()
        transition_id = f'{workflow_id}_{from_state}_{to_state}_{int(transition_time * 1000)}'
        if workflow_id in self._current_states:
            current_state, start_time = self._current_states[workflow_id]
            duration = transition_time - start_time
            self._state_durations[current_state].append(duration)
        self._current_states[workflow_id] = (to_state, transition_time)
        transition = {'id': transition_id, 'workflow_id': workflow_id, 'from_state': from_state, 'to_state': to_state, 'timestamp': transition_time, 'metadata': metadata or {}, 'trigger': transition_trigger}
        self._transitions.append(transition)
        self._transition_counts[from_state, to_state] += 1
        return transition_id

    def enter_state(self, workflow_id: str, state: str, metadata: Dict[str, Any]=None) -> str:
        """Enter a new state (convenience method for initial state or simple transitions).

        Args:
            workflow_id: Workflow ID
            state: State to enter
            metadata: Additional metadata

        Returns:
            State entry ID
        """
        if workflow_id in self._current_states:
            current_state, _ = self._current_states[workflow_id]
            return self.record_transition(workflow_id=workflow_id, from_state=current_state, to_state=state, metadata=metadata)
        entry_time = time.time()
        entry_id = f'{workflow_id}_{state}_{int(entry_time * 1000)}'
        self._current_states[workflow_id] = (state, entry_time)
        transition = {'id': entry_id, 'workflow_id': workflow_id, 'from_state': None, 'to_state': state, 'timestamp': entry_time, 'metadata': metadata or {}, 'trigger': 'initial'}
        self._transitions.append(transition)
        return entry_id

    def get_transition_matrix(self) -> Dict[str, Dict[str, int]]:
        """Get transition matrix showing counts between states.

        Returns:
            Nested dictionary of transition counts
        """
        matrix = defaultdict(lambda: defaultdict(int))
        for (from_state, to_state), count in self._transition_counts.items():
            matrix[from_state][to_state] = count
        return dict(matrix)

    def get_transition_details(self, transition_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a specific transition.

        Args:
            transition_id: The transition ID to look up

        Returns:
            Dictionary with transition details or None if not found
        """
        for transition in self._transitions:
            if transition['id'] == transition_id:
                return {'from_state': transition['from_state'], 'to_state': transition['to_state'], 'transition_trigger': transition.get('trigger'), 'timestamp': transition['timestamp'], 'workflow_id': transition['workflow_id'], 'metadata': transition.get('metadata', {})}
        return None

    def get_state_durations(self, workflow_id: Optional[str]=None) -> Dict[str, float]:
        """Get duration statistics for states.

        Args:
            workflow_id: Specific workflow ID or None for all workflows

        Returns:
            Dictionary mapping state names to average durations in milliseconds
        """
        if workflow_id:
            workflow_durations = {}
            workflow_transitions = [t for t in self._transitions if t.get('workflow_id') == workflow_id]
            workflow_transitions.sort(key=lambda x: x['timestamp'])
            for i in range(len(workflow_transitions) - 1):
                current = workflow_transitions[i]
                next_trans = workflow_transitions[i + 1]
                state = current.get('to_state')
                if state:
                    duration_ms = (next_trans['timestamp'] - current['timestamp']) * 1000
                    workflow_durations[state] = duration_ms
            return workflow_durations
        result = {}
        for state_name, durations in self._state_durations.items():
            if durations:
                result[state_name] = sum(durations) / len(durations) * 1000
        return result

    def validate_transition(self, from_state: str, to_state: str, allowed_transitions: Dict[str, List[str]]) -> bool:
        """Validate if a transition is allowed.

        Args:
            from_state: Current state
            to_state: Target state
            allowed_transitions: Dictionary of allowed transitions

        Returns:
            True if transition is valid
        """
        if from_state not in allowed_transitions:
            return False
        return to_state in allowed_transitions[from_state]

    def get_transition_history(self, workflow_id: Optional[str]=None, limit: int=100) -> List[Dict[str, Any]]:
        """Get transition history.

        Args:
            workflow_id: Specific workflow or None for all
            limit: Maximum number of transitions to return

        Returns:
            List of transitions
        """
        if workflow_id:
            transitions = [t for t in self._transitions if t['workflow_id'] == workflow_id]
        else:
            transitions = list(self._transitions)
        return transitions[-limit:]

    def detect_patterns(self, min_count: int=3) -> List[List[Tuple[str, str]]]:
        """Detect common transition patterns.

        Args:
            min_count: Minimum count for a pattern to be considered common

        Returns:
            List of common transition sequences
        """
        workflow_sequences = defaultdict(list)
        for transition in self._transitions:
            workflow_sequences[transition['workflow_id']].append((transition['from_state'], transition['to_state']))
        pattern_counts = defaultdict(int)
        for sequence in workflow_sequences.values():
            for length in range(2, min(6, len(sequence) + 1)):
                for i in range(len(sequence) - length + 1):
                    pattern = tuple(sequence[i:i + length])
                    pattern_counts[pattern] += 1
        common_patterns = [list(pattern) for pattern, count in pattern_counts.items() if count >= min_count]
        common_patterns.sort(key=lambda p: pattern_counts[tuple(p)], reverse=True)
        return common_patterns

    def get_workflow_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get the complete transition history for a workflow.

        Args:
            workflow_id: Workflow ID to get history for

        Returns:
            List of transitions for the workflow
        """
        history = []
        for transition in self._transitions:
            if transition['workflow_id'] == workflow_id:
                history.append({'from_state': transition['from_state'], 'to_state': transition['to_state'], 'timestamp': transition['timestamp'], 'trigger': transition.get('trigger'), 'metadata': transition.get('metadata', {})})
        return sorted(history, key=lambda x: x['timestamp'])

    def analyze_transition_patterns(self, workflow_id: str=None, min_frequency: int=1) -> Dict[str, Any]:
        """Analyze state transition patterns.

        Args:
            workflow_id: Optional workflow ID to filter by
            min_frequency: Minimum frequency for patterns to be included

        Returns:
            Analysis of transition patterns including most common paths
        """
        if workflow_id:
            transitions = [t for t in self._transitions if t['workflow_id'] == workflow_id]
        else:
            transitions = list(self._transitions)
        if not transitions:
            return {}
        pattern_counts = defaultdict(int)
        from_state_counts = defaultdict(int)
        for transition in transitions:
            from_state = transition.get('from_state')
            to_state = transition.get('to_state')
            if from_state and to_state:
                pattern_key = f'{from_state}->{to_state}'
                pattern_counts[pattern_key] += 1
                from_state_counts[from_state] += 1
        result = {}
        for pattern, count in pattern_counts.items():
            if count >= min_frequency:
                from_state = pattern.split('->')[0]
                total_from_state = from_state_counts[from_state]
                result[pattern] = {'count': count, 'probability': count / total_from_state if total_from_state > 0 else 0}
        return result

class CheckpointMetrics:
    """Tracks checkpoint operations in LangGraph."""

    def __init__(self): self._save_times: List[float] = []
        self._load_times: List[float] = []
        self._checkpoint_sizes: Dict[str, int] = {}
        self._save_failures = 0
        self._load_failures = 0
        self._total_saves = 0
        self._total_loads = 0
        self._save_error_types: List[str] = []
        self._load_error_types: List[str] = []

    @contextmanager
    def track_save(self, checkpoint_id: str) -> Generator[Any, None, None]:
        """Track checkpoint save operation.

        Args:
            checkpoint_id: Checkpoint identifier
        """
        start_time = time.time()
        self._total_saves += 1
        try:
            yield
            duration = time.time() - start_time
            self._save_times.append(duration)
        except (ValueError, TypeError):
            self._save_failures += 1
            raise

    @contextmanager
    def track_load(self, checkpoint_id: str) -> Generator[Any, None, None]:
        """Track checkpoint load operation.

        Args:
            checkpoint_id: Checkpoint identifier
        """
        start_time = time.time()
        self._total_loads += 1
        try:
            yield
            duration = time.time() - start_time
            self._load_times.append(duration)
        except (ValueError, TypeError):
            self._load_failures += 1
            raise

    def record_checkpoint_size(self, checkpoint_id: str, size_bytes: int) -> None:
        """Record checkpoint size.

        Args:
            checkpoint_id: Checkpoint identifier
            size_bytes: Size in bytes
        """
        self._checkpoint_sizes[checkpoint_id] = size_bytes

    def get_statistics(self) -> Dict[str, Any]:
        """Get checkpoint statistics.

        Returns:
            Statistics dictionary
        """
        stats = {'total_saves': self._total_saves, 'total_loads': self._total_loads, 'save_failures': self._save_failures, 'load_failures': self._load_failures, 'save_failure_rate': self._save_failures / max(1, self._total_saves), 'load_failure_rate': self._load_failures / max(1, self._total_loads)}
        if self._save_times:
            stats['save_time_avg'] = sum(self._save_times) / len(self._save_times)
            stats['save_time_min'] = min(self._save_times)
            stats['save_time_max'] = max(self._save_times)
        if self._load_times:
            stats['load_time_avg'] = sum(self._load_times) / len(self._load_times)
            stats['load_time_min'] = min(self._load_times)
            stats['load_time_max'] = max(self._load_times)
        if self._checkpoint_sizes:
            sizes = list(self._checkpoint_sizes.values())
            stats['checkpoint_size_avg'] = sum(sizes) / len(sizes)
            stats['checkpoint_size_min'] = min(sizes)
            stats['checkpoint_size_max'] = max(sizes)
            stats['total_storage_bytes'] = sum(sizes)
        return stats

    def get_retention_metrics(self, retention_days: int=7) -> Dict[str, Any]:
        """Get metrics for checkpoint retention.

        Args:
            retention_days: Retention period in days

        Returns:
            Retention metrics
        """
        total_checkpoints = len(self._checkpoint_sizes)
        total_size = sum(self._checkpoint_sizes.values())
        return {'total_checkpoints': total_checkpoints, 'total_size_bytes': total_size, 'retention_days': retention_days, 'estimated_daily_growth': total_size / max(1, retention_days), 'checkpoints_per_day': total_checkpoints / max(1, retention_days)}

    def record_checkpoint_save(self, workflow_id: str, checkpoint_size_bytes: int, storage_backend: str='memory', compression_ratio: float=1.0) -> str:
        """Record the start of a checkpoint save operation.

        Args:
            workflow_id: ID of the workflow being checkpointed
            checkpoint_size_bytes: Size of the checkpoint in bytes
            storage_backend: Storage backend being used
            compression_ratio: Compression ratio achieved

        Returns:
            Checkpoint ID for tracking
        """
        checkpoint_id = f'ckpt-{workflow_id}-{int(time.time() * 1000)}'
        if not hasattr(self, '_active_saves'):
            self._active_saves = {}
        self._active_saves[checkpoint_id] = {'workflow_id': workflow_id, 'size_bytes': checkpoint_size_bytes, 'storage_backend': storage_backend, 'compression_ratio': compression_ratio, 'start_time': time.time()}
        self.record_checkpoint_size(checkpoint_id, checkpoint_size_bytes)
        return checkpoint_id

    def complete_checkpoint_save(self, checkpoint_id: str, success: bool=True, error_type: Optional[str]=None, error_message: Optional[str]=None) -> Dict[str, Any]:
        """Complete a checkpoint save operation.

        Args:
            checkpoint_id: ID of the checkpoint operation
            success: Whether the save was successful
            error_type: Type of error if failed
            error_message: Error message if failed

        Returns:
            Save metrics
        """
        if not hasattr(self, '_active_saves'):
            self._active_saves = {}
        if checkpoint_id not in self._active_saves:
            return {'error': 'Unknown checkpoint ID'}
        save_info = self._active_saves.pop(checkpoint_id)
        duration = time.time() - save_info['start_time']
        if success:
            self._save_times.append(duration)
            self._total_saves += 1
        else:
            self._save_failures += 1
            if error_type:
                self._save_error_types.append(error_type)
        return {'checkpoint_id': checkpoint_id, 'workflow_id': save_info['workflow_id'], 'duration_ms': duration * 1000, 'size_bytes': save_info['size_bytes'], 'storage_backend': save_info['storage_backend'], 'compression_ratio': save_info['compression_ratio'], 'success': success, 'error_type': error_type, 'error_message': error_message}

    def record_checkpoint_load(self, workflow_id: str, checkpoint_id: str, storage_backend: str='memory') -> str:
        """Record the start of a checkpoint load operation.

        Args:
            workflow_id: ID of the workflow being loaded
            checkpoint_id: ID of the checkpoint being loaded
            storage_backend: Storage backend being used

        Returns:
            Load operation ID for tracking
        """
        load_id = f'load-{workflow_id}-{int(time.time() * 1000)}'
        if not hasattr(self, '_active_loads'):
            self._active_loads = {}
        self._active_loads[load_id] = {'workflow_id': workflow_id, 'checkpoint_id': checkpoint_id, 'storage_backend': storage_backend, 'start_time': time.time()}
        return load_id

    def complete_checkpoint_load(self, load_id: str, success: bool=True, checkpoint_size_bytes: Optional[int]=None, error_type: Optional[str]=None, error_message: Optional[str]=None) -> Dict[str, Any]:
        """Complete a checkpoint load operation.

        Args:
            load_id: ID of the load operation
            success: Whether the load was successful
            checkpoint_size_bytes: Size of loaded checkpoint in bytes
            error_type: Type of error if failed
            error_message: Error message if failed

        Returns:
            Load metrics
        """
        if not hasattr(self, '_active_loads'):
            self._active_loads = {}
        if load_id not in self._active_loads:
            return {'error': 'Unknown load ID'}
        load_info = self._active_loads.pop(load_id)
        duration = time.time() - load_info['start_time']
        if success:
            self._load_times.append(duration)
            self._total_loads += 1
        else:
            self._load_failures += 1
            if error_type:
                self._load_error_types.append(error_type)
        return {'load_id': load_id, 'workflow_id': load_info['workflow_id'], 'checkpoint_id': load_info['checkpoint_id'], 'duration_ms': duration * 1000, 'size_bytes': checkpoint_size_bytes, 'storage_backend': load_info['storage_backend'], 'success': success, 'error_type': error_type, 'error_message': error_message}

    def get_failure_stats(self) -> Dict[str, Any]:
        """Get statistics about checkpoint failures.

        Returns:
            Dictionary with failure statistics
        """
        save_error_types = []
        load_error_types = []
        if not hasattr(self, '_save_error_types'):
            self._save_error_types = []
        if not hasattr(self, '_load_error_types'):
            self._load_error_types = []
        return {'save_failures': self._save_failures, 'load_failures': self._load_failures, 'save_error_types': self._save_error_types, 'load_error_types': self._load_error_types, 'total_failures': self._save_failures + self._load_failures}

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get statistics about checkpoint storage usage.

        Returns:
            Dictionary with storage statistics
        """
        if not self._checkpoint_sizes:
            return {'total_checkpoints': 0, 'total_size_bytes': 0, 'average_size_bytes': 0, 'largest_checkpoint_bytes': 0, 'smallest_checkpoint_bytes': 0}
        sizes = list(self._checkpoint_sizes.values())
        total_size = sum(sizes)
        return {'total_checkpoints': len(self._checkpoint_sizes), 'total_size_bytes': total_size, 'average_size_bytes': total_size / len(sizes) if sizes else 0, 'largest_checkpoint_bytes': max(sizes) if sizes else 0, 'smallest_checkpoint_bytes': min(sizes) if sizes else 0}

    def record_checkpoint_with_timestamp(self, workflow_id: str, checkpoint_size_bytes: int, timestamp: datetime=None) -> str:
        """Record a checkpoint with a specific timestamp.

        Args:
            workflow_id: ID of the workflow
            checkpoint_size_bytes: Size of the checkpoint in bytes
            timestamp: Timestamp for the checkpoint (defaults to now)

        Returns:
            Checkpoint ID
        """
        from datetime import datetime
        if timestamp is None:
            timestamp = datetime.now()
        checkpoint_id = f'ckpt-{workflow_id}-{int(timestamp.timestamp() * 1000)}'
        if not hasattr(self, '_checkpoint_timestamps'):
            self._checkpoint_timestamps = {}
        self._checkpoint_timestamps[checkpoint_id] = timestamp
        self._checkpoint_sizes[checkpoint_id] = checkpoint_size_bytes
        return checkpoint_id

    def cleanup_old_checkpoints(self, retention_hours: int) -> Dict[str, Any]:
        """Clean up checkpoints older than the retention period.

        Args:
            retention_hours: Number of hours to retain checkpoints

        Returns:
            Cleanup metrics
        """
        from datetime import datetime, timedelta
        if not hasattr(self, '_checkpoint_timestamps'):
            return {'removed_count': 0, 'removed_size_bytes': 0, 'retained_count': 0, 'retained_size_bytes': 0}
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)
        removed_count = 0
        removed_size = 0
        retained_count = 0
        retained_size = 0
        checkpoints_to_remove = []
        for checkpoint_id, timestamp in self._checkpoint_timestamps.items():
            size = self._checkpoint_sizes.get(checkpoint_id, 0)
            if timestamp < cutoff_time:
                checkpoints_to_remove.append(checkpoint_id)
                removed_count += 1
                removed_size += size
            else:
                retained_count += 1
                retained_size += size
        for checkpoint_id in checkpoints_to_remove:
            del self._checkpoint_timestamps[checkpoint_id]
            if checkpoint_id in self._checkpoint_sizes:
                del self._checkpoint_sizes[checkpoint_id]
        return {'removed_count': removed_count, 'freed_bytes': removed_size, 'remaining_count': retained_count, 'retained_size_bytes': retained_size}

class MemoryUsageTracker:
    """Tracks memory usage for LangGraph components."""

    def __init__(self, sample_interval: int=60):
        """Initialize memory usage tracker.

        Args:
            sample_interval: Sampling interval in seconds
        """
        self.sample_interval = sample_interval
        self._samples: Deque[Dict[str, Any]] = deque(maxlen=1000)
        self._component_memory: Dict[str, List[int]] = defaultdict(list)
        self._process = psutil.Process()
        self._last_sample_time = 0

    def sample_memory(self) -> Dict[str, Any]:
        """Sample current memory usage.

        Returns:
            Memory usage statistics
        """
        current_time = time.time()
        if current_time - self._last_sample_time < self.sample_interval:
            return {}
        memory_info = self._process.memory_info()
        memory_percent = self._process.memory_percent()
        sample = {'timestamp': current_time, 'rss_bytes': memory_info.rss, 'vms_bytes': memory_info.vms, 'memory_percent': memory_percent, 'available_mb': psutil.virtual_memory().available / (1024 * 1024)}
        self._samples.append(sample)
        self._last_sample_time = current_time
        return sample

    def track_component(self, component_name: str, size_bytes: int) -> None:
        """Track memory usage for a specific component.

        Args:
            component_name: Name of the component
            size_bytes: Memory usage in bytes
        """
        self._component_memory[component_name].append(size_bytes)
        if len(self._component_memory[component_name]) > 100:
            self._component_memory[component_name] = self._component_memory[component_name][-100:]

    def get_memory_trends(self) -> Dict[str, Any]:
        """Get memory usage trends.

        Returns:
            Memory trend analysis
        """
        if not self._samples:
            return {}
        recent_samples = list(self._samples)[-10:]
        older_samples = list(self._samples)[:-10] if len(self._samples) > 10 else []
        trends = {}
        if recent_samples:
            recent_avg = sum((s['rss_bytes'] for s in recent_samples)) / len(recent_samples)
            trends['current_rss_mb'] = recent_avg / (1024 * 1024)
        if older_samples:
            older_avg = sum((s['rss_bytes'] for s in older_samples)) / len(older_samples)
            trends['previous_rss_mb'] = older_avg / (1024 * 1024)
            trends['growth_rate'] = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        return trends

    def detect_memory_leak(self, threshold_mb: float=100) -> bool:
        """Detect potential memory leaks.

        Args:
            threshold_mb: Threshold for leak detection in MB

        Returns:
            True if potential leak detected
        """
        if len(self._samples) < 10:
            return False
        samples = list(self._samples)[-10:]
        rss_values = [s['rss_bytes'] for s in samples]
        is_growing = all((rss_values[i] > rss_values[i - 1] for i in range(1, len(rss_values))))
        total_growth = (rss_values[-1] - rss_values[0]) / (1024 * 1024)
        return is_growing and total_growth > threshold_mb

    def detect_memory_leaks(self, growth_threshold_mb_per_hour: float=10.0) -> Dict[str, Dict[str, Any]]:
        """Detect potential memory leaks across all components.

        Args:
            growth_threshold_mb_per_hour: Memory growth threshold in MB/hour to consider a leak

        Returns:
            Dictionary mapping component names to leak detection results
        """
        leaks = {}
        current_time = time.time()
        for component, entries in self._component_memory.items():
            if len(entries) < 2:
                continue
            first = entries[0]
            last = entries[-1]
            time_diff_seconds = last['timestamp'] - first['timestamp']
            if time_diff_seconds <= 0:
                continue
            time_diff_hours = time_diff_seconds / 3600.0
            growth_bytes = last['bytes_used'] - first['bytes_used']
            growth_mb = growth_bytes / (1024 * 1024)
            growth_rate_mb_per_hour = growth_mb / time_diff_hours if time_diff_hours > 0 else 0
            suspected_leak = growth_rate_mb_per_hour >= growth_threshold_mb_per_hour
            if suspected_leak or growth_mb > 0:
                leaks[component] = {'suspected_leak': suspected_leak, 'growth_rate_mb_per_hour': growth_rate_mb_per_hour, 'total_growth_mb': growth_mb, 'time_window_hours': time_diff_hours, 'initial_mb': first['bytes_used'] / (1024 * 1024), 'current_mb': last['bytes_used'] / (1024 * 1024)}
        return leaks

    def get_component_stats(self, component: str=None) -> Dict[str, Any]:
        """Get memory statistics for a specific component or all components.

        Args:
            component: Component name to get stats for, or None for all

        Returns:
            Dictionary with memory statistics
        """
        if component:
            if component not in self._component_memory:
                return {'current_bytes': 0, 'allocated_bytes': 0, 'usage_ratio': 0.0, 'current_mb': 0.0, 'average_mb': 0.0, 'peak_mb': 0.0, 'min_mb': 0.0}
            entries = self._component_memory[component]
            if not entries:
                return {'current_bytes': 0, 'allocated_bytes': 0, 'usage_ratio': 0.0, 'current_mb': 0.0, 'average_mb': 0.0, 'peak_mb': 0.0, 'min_mb': 0.0}
            latest = entries[-1]
            current_bytes = latest['bytes_used']
            allocated_bytes = latest.get('bytes_allocated', current_bytes)
            bytes_used_values = [e['bytes_used'] for e in entries]
            return {'current_bytes': current_bytes, 'allocated_bytes': allocated_bytes, 'usage_ratio': current_bytes / allocated_bytes if allocated_bytes > 0 else 0.0, 'current_mb': current_bytes / (1024 * 1024), 'average_mb': sum(bytes_used_values) / len(bytes_used_values) / (1024 * 1024), 'peak_mb': max(bytes_used_values) / (1024 * 1024), 'min_mb': min(bytes_used_values) / (1024 * 1024)}
        else:
            all_stats = {}
            for comp_name in self._component_memory:
                all_stats[comp_name] = self.get_component_stats(comp_name)
            return all_stats

    def get_total_memory_usage(self) -> Dict[str, Any]:
        """Get total memory usage across all components.

        Returns:
            Dictionary with total memory statistics
        """
        total_used = 0
        total_allocated = 0
        for component, entries in self._component_memory.items():
            if entries:
                latest = entries[-1]
                total_used += latest['bytes_used']
                total_allocated += latest.get('bytes_allocated', latest['bytes_used'])
        return {'total_used_bytes': total_used, 'total_allocated_bytes': total_allocated, 'usage_ratio': total_used / total_allocated if total_allocated > 0 else 0.0, 'total_used_mb': total_used / (1024 * 1024), 'total_allocated_mb': total_allocated / (1024 * 1024)}

    def analyze_memory_growth(self, component: str) -> Dict[str, Any]:
        """Analyze memory growth patterns for a component.

        Args:
            component: Component name to analyze

        Returns:
            Dictionary with growth analysis
        """
        if component not in self._component_memory or len(self._component_memory[component]) < 1:
            return {'initial_bytes': 0, 'current_bytes': 0, 'growth_bytes': 0, 'growth_rate_bytes_per_second': 0.0, 'growth_rate_mb_per_sec': 0.0, 'total_growth_mb': 0.0, 'growth_percentage': 0.0, 'is_growing': False}
        entries = self._component_memory[component]
        first_entry = entries[0]
        last_entry = entries[-1]
        first_bytes = first_entry['bytes_used']
        last_bytes = last_entry['bytes_used']
        if len(entries) > 1:
            time_diff = last_entry['timestamp'] - first_entry['timestamp']
            if time_diff <= 0:
                time_diff = 1
        else:
            time_diff = 1
        growth_bytes = last_bytes - first_bytes
        growth_mb = growth_bytes / (1024 * 1024)
        growth_rate_bytes = growth_bytes / time_diff if time_diff > 0 else 0
        growth_rate_mb = growth_mb / time_diff if time_diff > 0 else 0
        growth_percentage = (last_bytes - first_bytes) / first_bytes * 100 if first_bytes > 0 else 0
        return {'initial_bytes': first_bytes, 'current_bytes': last_bytes, 'growth_bytes': growth_bytes, 'growth_rate_bytes_per_second': growth_rate_bytes, 'growth_rate_mb_per_sec': growth_rate_mb, 'total_growth_mb': growth_mb, 'growth_percentage': growth_percentage, 'is_growing': growth_bytes > 0}

    def set_memory_limit(self, component: str, max_bytes: int) -> None:
        """Set memory limit for a component.

        Args:
            component: Component name
            max_bytes: Maximum allowed memory in bytes
        """
        if not hasattr(self, '_memory_limits'):
            self._memory_limits = {}
        self._memory_limits[component] = max_bytes

    def check_memory_limit(self, component: str) -> Dict[str, Any]:
        """Check if a component is within its memory limit.

        Args:
            component: Component name to check

        Returns:
            Dictionary with limit check results
        """
        if not hasattr(self, '_memory_limits'):
            self._memory_limits = {}
        if component not in self._memory_limits:
            return {'has_limit': False, 'within_limit': True, 'current_bytes': 0, 'limit_bytes': 0, 'usage_ratio': 0.0}
        limit = self._memory_limits[component]
        if component in self._component_memory and self._component_memory[component]:
            current_bytes = self._component_memory[component][-1]['bytes_used']
        else:
            current_bytes = 0
        within_limit = current_bytes <= limit
        usage_ratio = current_bytes / limit if limit > 0 else 0.0
        return {'has_limit': True, 'within_limit': within_limit, 'current_bytes': current_bytes, 'limit_bytes': limit, 'usage_ratio': usage_ratio}

    def check_memory_limit(self, component: str, current_bytes: int=None) -> bool:
        """Check if a component is within its memory limit.

        Args:
            component: Component name to check
            current_bytes: Current memory usage in bytes (if not provided, uses latest recorded)

        Returns:
            True if within limit or no limit set, False if over limit
        """
        if not hasattr(self, '_memory_limits'):
            self._memory_limits = {}
        if component not in self._memory_limits:
            return True
        limit = self._memory_limits[component]
        if current_bytes is None:
            if component in self._component_memory and self._component_memory[component]:
                current_bytes = self._component_memory[component][-1]['bytes_used']
            else:
                current_bytes = 0
        return current_bytes <= limit

    def get_limit_violations(self) -> Dict[str, Dict[str, Any]]:
        """Get components that have violated their memory limits.

        Returns:
            Dictionary mapping component names to violation details
        """
        if not hasattr(self, '_memory_limits'):
            return {}
        violations = {}
        for component, limit in self._memory_limits.items():
            current_bytes = 0
            if component in self._component_memory and self._component_memory[component]:
                current_bytes = self._component_memory[component][-1]['bytes_used']
            if current_bytes > limit:
                violations[component] = {'current_bytes': current_bytes, 'limit_bytes': limit, 'over_limit_bytes': current_bytes - limit, 'usage_ratio': current_bytes / limit if limit > 0 else 0}
        return violations

    def record_memory_usage(self, component: str, bytes_used: int, bytes_allocated: int=None) -> None:
        """Record memory usage for a component.

        Args:
            component: Name of the component
            bytes_used: Bytes currently used
            bytes_allocated: Bytes allocated (optional)
        """
        if component not in self._component_memory:
            self._component_memory[component] = []
        entry = {'timestamp': time.time(), 'bytes_used': bytes_used, 'bytes_allocated': bytes_allocated or bytes_used}
        self._component_memory[component].append(entry)

class ErrorMetricsCollector:
    """Collects and analyzes error metrics for LangGraph."""

    def __init__(self, window_size: int=1000):
        """Initialize error metrics collector.

        Args:
            window_size: Size of the sliding window for error tracking
        """
        self.window_size = window_size
        self._errors: Deque[Dict[str, Any]] = deque(maxlen=window_size)
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._error_rates: Dict[str, List[float]] = defaultdict(list)
        self._recovery_times: List[float] = []

    def record_error(self, error_type: str, error_message: str=None, component: str=None, message: str=None, workflow_id: str=None, node_name: str=None, severity: str='error', retry_count: int=0, metadata: Dict[str, Any]=None, timestamp: float=None) -> None:
        """Record an error occurrence.

        Args:
            error_type: Type of error
            error_message: Error message (preferred over 'message')
            component: Component where error occurred
            message: Error message (deprecated, use error_message)
            workflow_id: Workflow ID where error occurred
            node_name: Node name where error occurred
            severity: Error severity level
            retry_count: Number of retries attempted
            metadata: Additional metadata
        """
        from datetime import datetime
        final_message = error_message or message or ''
        if timestamp is not None:
            if isinstance(timestamp, datetime):
                timestamp = timestamp.timestamp()
        else:
            timestamp = time.time()
        error = {'timestamp': timestamp, 'error_type': error_type, 'component': component, 'message': final_message, 'workflow_id': workflow_id, 'node_name': node_name, 'severity': severity, 'retry_count': retry_count, 'metadata': metadata or {}}
        self._errors.append(error)
        self._error_counts[error_type] += 1
        if not hasattr(self, '_severity_counts'):
            self._severity_counts = defaultdict(int)
        self._severity_counts[severity] += 1
        if component:
            if not hasattr(self, '_component_errors'):
                self._component_errors = defaultdict(list)
            self._component_errors[component].append(error)

    def record_success(self, component: str=None, operation: str=None, timestamp: float=None) -> None:
        """Record a successful operation.

        Args:
            component: Component that succeeded
            operation: Operation that succeeded
            timestamp: Custom timestamp
        """
        from datetime import datetime
        if not hasattr(self, '_successes'):
            self._successes = []
        if timestamp is not None:
            if isinstance(timestamp, datetime):
                timestamp = timestamp.timestamp()
        else:
            timestamp = time.time()
        success_record = {'timestamp': timestamp, 'component': component, 'operation': operation}
        self._successes.append(success_record)
        if not hasattr(self, '_success_count'):
            self._success_count = 0
        self._success_count += 1

    def get_error_stats(self) -> Dict[str, Any]:
        """Get comprehensive error statistics.

        Returns:
            Dictionary with error statistics
        """
        if not self._errors:
            return {'total_errors': 0, 'by_type': {}, 'by_severity': {}, 'by_component': {}, 'error_rate_per_minute': 0.0, 'most_common_error': None}
        timestamps = [e['timestamp'] for e in self._errors]
        time_window = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 1
        time_window_minutes = time_window / 60.0
        by_severity = defaultdict(int)
        for error in self._errors:
            by_severity[error.get('severity', 'error')] += 1
        by_component = defaultdict(int)
        for error in self._errors:
            if error.get('component'):
                by_component[error['component']] += 1
        most_common_error = None
        if self._error_counts:
            most_common_error = max(self._error_counts.items(), key=lambda x: x[1])[0]
        return {'total_errors': len(self._errors), 'by_type': dict(self._error_counts), 'by_severity': dict(by_severity), 'by_component': dict(by_component), 'error_rate_per_minute': len(self._errors) / time_window_minutes if time_window_minutes > 0 else 0, 'most_common_error': most_common_error}

    def calculate_error_rate(self, time_window_seconds: int=60, window_seconds: int=None) -> Dict[str, float]:
        """Calculate overall error rate.

        Args:
            time_window_seconds: Time window in seconds
            window_seconds: Deprecated parameter for backwards compatibility

        Returns:
            Dictionary with error rate metrics
        """
        actual_window = time_window_seconds if window_seconds is None else window_seconds
        cutoff_time = time.time() - actual_window
        recent_errors = [e for e in self._errors if e['timestamp'] >= cutoff_time]
        recent_successes = 0
        if hasattr(self, '_successes'):
            recent_successes = len([s for s in self._successes if s['timestamp'] >= cutoff_time])
        total_operations = recent_successes
        error_rate = len(recent_errors) / total_operations if total_operations > 0 else 0.0
        success_rate = (total_operations - len(recent_errors)) / total_operations if total_operations > 0 else 1.0
        return {'error_rate': error_rate, 'errors_per_minute': len(recent_errors) * 60 / actual_window if actual_window > 0 else 0, 'success_rate': success_rate, 'total_errors': len(recent_errors), 'total_successes': recent_successes, 'total_operations': total_operations}

    def get_error_distribution(self) -> Dict[str, float]:
        """Get error distribution by type.

        Returns:
            Percentage distribution of errors
        """
        total_errors = sum(self._error_counts.values())
        if total_errors == 0:
            return {}
        return {error_type: count / total_errors for error_type, count in self._error_counts.items()}

    def detect_error_patterns(self) -> List[Dict[str, Any]]:
        """Detect recurring error patterns.

        Returns:
            List of detected patterns
        """
        patterns = []
        error_groups = defaultdict(list)
        for error in self._errors:
            key = (error['error_type'], error['component'])
            error_groups[key].append(error)
        for (error_type, component), errors in error_groups.items():
            if len(errors) >= 3:
                intervals = []
                for i in range(1, len(errors)):
                    intervals.append(errors[i]['timestamp'] - errors[i - 1]['timestamp'])
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    std_interval = (sum(((i - avg_interval) ** 2 for i in intervals)) / len(intervals)) ** 0.5
                    if std_interval < avg_interval * 0.3:
                        patterns.append({'error_type': error_type, 'component': component, 'frequency': len(errors), 'avg_interval_seconds': avg_interval, 'pattern_type': 'periodic'})
        return patterns

    def record_recovery(self, recovery_time: float) -> None:
        """Record error recovery time.

        Args:
            recovery_time: Time taken to recover in seconds
        """
        self._recovery_times.append(recovery_time)

    def get_recovery_stats(self) -> Dict[str, float]:
        """Get recovery time statistics.

        Returns:
            Recovery statistics
        """
        if not self._recovery_times:
            return {}
        return {'avg_recovery_seconds': sum(self._recovery_times) / len(self._recovery_times), 'min_recovery_seconds': min(self._recovery_times), 'max_recovery_seconds': max(self._recovery_times), 'total_recoveries': len(self._recovery_times)}

class PerformanceAnalyzer:
    """Analyzes performance metrics for LangGraph workflows."""

    def __init__(self): self._node_tracker = NodeExecutionTracker()
        self._workflow_tracker = WorkflowMetricsTracker()
        self._memory_tracker = MemoryUsageTracker()
        self._baselines: Dict[str, Dict[str, float]] = {}

    def set_baseline(self, metric_name: str, value: float) -> None:
        """Set performance baseline for comparison.

        Args:
            metric_name: Name of the metric
            value: Baseline value
        """
        self._baselines[metric_name] = {'value': value, 'timestamp': time.time()}

    def detect_bottlenecks(self) -> List[Dict[str, Any]]:
        """Detect performance bottlenecks.

        Returns:
            List of detected bottlenecks
        """
        bottlenecks = []
        node_stats = self._node_tracker.get_node_stats()
        for node_name, stats in node_stats.items():
            if stats['avg_duration'] > 1.0:
                bottlenecks.append({'type': 'slow_node', 'component': node_name, 'avg_duration': stats['avg_duration'], 'severity': 'high' if stats['avg_duration'] > 5.0 else 'medium'})
        workflow_stats = self._workflow_tracker.get_workflow_stats()
        for workflow_type, stats in workflow_stats.items():
            if stats['throughput_per_minute'] < 1.0:
                bottlenecks.append({'type': 'low_throughput', 'component': workflow_type, 'throughput': stats['throughput_per_minute'], 'severity': 'medium'})
        if self._memory_tracker.detect_memory_leak():
            bottlenecks.append({'type': 'memory_leak', 'component': 'system', 'severity': 'high'})
        return bottlenecks

    def check_regression(self, metric_name: str, current_value: float) -> Optional[Dict[str, Any]]:
        """Check for performance regression.

        Args:
            metric_name: Name of the metric
            current_value: Current value to check

        Returns:
            Regression details if detected, None otherwise
        """
        if metric_name not in self._baselines:
            return None
        baseline = self._baselines[metric_name]['value']
        if baseline > 0:
            change_percent = (current_value - baseline) / baseline * 100
        else:
            change_percent = 100 if current_value > 0 else 0
        if change_percent > 20:
            return {'metric': metric_name, 'baseline': baseline, 'current': current_value, 'change_percent': change_percent, 'severity': 'high' if change_percent > 50 else 'medium'}
        return None

    def generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations.

        Returns:
            List of recommendations
        """
        recommendations = []
        bottlenecks = self.detect_bottlenecks()
        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'slow_node':
                recommendations.append(f"Optimize node '{bottleneck['component']}' - average duration {bottleneck['avg_duration']:.2f}s")
            elif bottleneck['type'] == 'low_throughput':
                recommendations.append(f"Improve throughput for workflow '{bottleneck['component']}' - currently {bottleneck['throughput']:.2f}/min")
            elif bottleneck['type'] == 'memory_leak':
                recommendations.append('Investigate potential memory leak - consistent memory growth detected')
        node_stats = self._node_tracker.get_node_stats()
        for node_name, stats in node_stats.items():
            if stats['failed'] > stats['successful']:
                recommendations.append(f"Fix errors in node '{node_name}' - failure rate {stats['failed'] / max(1, stats['total_executions']) * 100:.1f}%")
        return recommendations

    def analyze_trends(self, window_hours: int=24) -> Dict[str, Any]:
        """Analyze performance trends over time.

        Args:
            window_hours: Time window in hours

        Returns:
            Trend analysis results
        """
        return {'node_performance': self._node_tracker.get_node_stats(), 'workflow_performance': self._workflow_tracker.get_workflow_stats(), 'memory_trends': self._memory_tracker.get_memory_trends(), 'recommendations': self.generate_recommendations()}

class LangGraphMetricsCollector:
    """
    Main collector that aggregates all LangGraph metrics components.

    This class provides a unified interface for collecting and managing
    all LangGraph-related metrics including node execution, workflow tracking,
    state transitions, checkpoints, memory usage, errors, and performance.
    """

    def __init__(self): self.node_tracker = NodeExecutionTracker()
        self.workflow_tracker = WorkflowMetricsTracker()
        self.state_tracker = StateTransitionTracker()
        self.checkpoint_metrics = CheckpointMetrics()
        self.memory_tracker = MemoryUsageTracker()
        self.error_collector = ErrorMetricsCollector()
        self.performance_analyzer = PerformanceAnalyzer()

    async def start_workflow(self, workflow_id: str, workflow_name: str, metadata: Optional[Dict[str, Any]]=None) -> None: Start tracking a new workflow execution.

        Args:
            workflow_id: Unique identifier for the workflow
            workflow_name: Name of the workflow
            metadata: Optional metadata for the workflow
        """
        await self.workflow_tracker.start_workflow(workflow_id, workflow_name)
        if metadata:
            pass

    async def track_node_execution(self, node_name: str, execution_time: float, status: str, workflow_id: Optional[str]=None, metadata: Optional[Dict[str, Any]]=None) -> None: Track a node execution.

        Args:
            node_name: Name of the node
            execution_time: Time taken to execute the node
            status: Status of the execution (success/failure)
            workflow_id: Optional workflow ID
            metadata: Optional metadata
        """
        await self.node_tracker.track_execution(node_name=node_name, execution_time=execution_time, status=status, workflow_id=workflow_id)

    async def track_state_transition(self, from_state: str, to_state: str, transition_time: float, metadata: Optional[Dict[str, Any]]=None) -> None: Track a state transition.

        Args:
            from_state: Source state
            to_state: Target state
            transition_time: Time taken for transition
            metadata: Optional metadata
        """
        await self.state_tracker.track_transition(from_state=from_state, to_state=to_state, transition_time=transition_time)

    async def track_checkpoint(self, checkpoint_id: str, size_bytes: int, save_time: float, metadata: Optional[Dict[str, Any]]=None) -> None: Track checkpoint metrics.

        Args:
            checkpoint_id: Unique checkpoint identifier
            size_bytes: Size of checkpoint in bytes
            save_time: Time taken to save checkpoint
            metadata: Optional metadata
        """
        await self.checkpoint_metrics.track_save(checkpoint_id=checkpoint_id, size_bytes=size_bytes, save_time=save_time)

    async def track_memory_usage(self, node_name: str, memory_mb: float, metadata: Optional[Dict[str, Any]]=None) -> None: Track memory usage for a node.

        Args:
            node_name: Name of the node
            memory_mb: Memory usage in MB
            metadata: Optional metadata
        """
        await self.memory_tracker.track_usage(node_name=node_name, memory_mb=memory_mb)

    async def track_error(self, error_type: str, node_name: Optional[str]=None, workflow_id: Optional[str]=None, error_details: Optional[Dict[str, Any]]=None) -> None: Track an error occurrence.

        Args:
            error_type: Type of error
            node_name: Optional node where error occurred
            workflow_id: Optional workflow ID
            error_details: Optional error details
        """
        await self.error_collector.track_error(error_type=error_type, node_name=node_name, workflow_id=workflow_id, details=error_details)

    async def complete_workflow(self, workflow_id: str, status: str, metadata: Optional[Dict[str, Any]]=None) -> None: Complete workflow tracking.

        Args:
            workflow_id: Workflow identifier
            status: Final status of workflow
            metadata: Optional metadata
        """
        await self.workflow_tracker.complete_workflow(workflow_id, status)

    async def get_metrics_summary(self) -> Dict[str, Any]: Get a summary of all collected metrics.

        Returns:
            Dictionary containing metrics from all collectors
        """
        summary = {}
        if hasattr(self.node_tracker, 'get_stats'):
            summary['node_stats'] = await self.node_tracker.get_stats()
        if hasattr(self.workflow_tracker, 'get_summary'):
            summary['workflow_summary'] = await self.workflow_tracker.get_summary()
        if hasattr(self.state_tracker, 'get_transition_stats'):
            summary['state_transitions'] = await self.state_tracker.get_transition_stats()
        if hasattr(self.checkpoint_metrics, 'get_stats'):
            summary['checkpoint_stats'] = await self.checkpoint_metrics.get_stats()
        if hasattr(self.memory_tracker, 'get_peak_usage'):
            summary['memory_peak'] = await self.memory_tracker.get_peak_usage()
        if hasattr(self.error_collector, 'get_error_summary'):
            summary['error_summary'] = await self.error_collector.get_error_summary()
        if hasattr(self.performance_analyzer, 'analyze'):
            summary['performance_analysis'] = await self.performance_analyzer.analyze()
        return summary

    async def reset_metrics(self) -> None: for tracker in [self.node_tracker, self.workflow_tracker, self.state_tracker, self.checkpoint_metrics, self.memory_tracker, self.error_collector, self.performance_analyzer]:
            if hasattr(tracker, 'reset'):
                await tracker.reset()