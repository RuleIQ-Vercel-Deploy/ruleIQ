"""
Prometheus metrics exporter with HTTP server and formatting.
"""

import asyncio
import logging
import re
import time
from collections import defaultdict
import http.server
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from threading import Thread
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)


# Constants for Prometheus
CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"


class CollectorRegistry:
    """Mock Prometheus CollectorRegistry for compatibility."""
    
    def __init__(self):
        """Initialize registry."""
        self.collectors = []
        
    def register(self, collector):
        """Register a collector."""
        self.collectors.append(collector)
        
    def unregister(self, collector):
        """Unregister a collector."""
        if collector in self.collectors:
            self.collectors.remove(collector)
            
    def collect(self):
        """Collect metrics from all collectors."""
        for collector in self.collectors:
            yield from collector.collect()

class PrometheusFormatter:
    """Formats metrics in Prometheus text format."""
    
    def __init__(self):
        """Initialize Prometheus formatter."""
        self.metric_families: Dict[str, Dict[str, Any]] = {}
        self._type_map = {
            "counter": "counter",
            "gauge": "gauge",
            "histogram": "histogram",
            "summary": "summary",
            "untyped": "untyped"
        }
        
    def format_counter(self, metric_data: Dict[str, Any]) -> str:
        """Format counter metric.
        
        Args:
            metric_data: Metric data with name, value, labels, etc.
            
        Returns:
            Formatted counter string
        """
        name = metric_data["name"]
        value = metric_data.get("value", 0)
        labels = metric_data.get("labels", {})
        help_text = metric_data.get("description", metric_data.get("help", f"Counter {name}"))
        
        output = []
        output.append(f"# HELP {name} {help_text}")
        output.append(f"# TYPE {name} counter")
        
        if labels:
            label_str = self._format_labels(labels)
            output.append(f"{name}{{{label_str}}} {value}")
        else:
            output.append(f"{name} {value}")
            
        return "\n".join(output)
        
    def format_gauge(self, metric_data: Dict[str, Any]) -> str:
        """Format gauge metric.
        
        Args:
            metric_data: Metric data with name, value, labels, etc.
            
        Returns:
            Formatted gauge string
        """
        name = metric_data["name"]
        value = metric_data.get("value", 0)
        labels = metric_data.get("labels", {})
        help_text = metric_data.get("description", metric_data.get("help", f"Gauge {name}"))
        
        output = []
        output.append(f"# HELP {name} {help_text}")
        output.append(f"# TYPE {name} gauge")
        
        if labels:
            label_str = self._format_labels(labels)
            output.append(f"{name}{{{label_str}}} {value}")
        else:
            output.append(f"{name} {value}")
            
        return "\n".join(output)
        
    def format_histogram(self, metric_data: Dict[str, Any]) -> str:
        """Format histogram metric.
        
        Args:
            metric_data: Metric data with name, buckets, sum, count, labels, etc.
            
        Returns:
            Formatted histogram string
        """
        name = metric_data["name"]
        buckets = metric_data.get("buckets", {})
        sum_value = metric_data.get("sum", 0)
        count_value = metric_data.get("count", 0)
        labels = metric_data.get("labels", {})
        help_text = metric_data.get("description", metric_data.get("help", f"Histogram {name}"))
        
        output = []
        output.append(f"# HELP {name} {help_text}")
        output.append(f"# TYPE {name} histogram")
        
        # Format bucket lines
        base_labels = self._format_labels(labels) if labels else ""
        
        # Sort buckets by boundary
        sorted_buckets = sorted(buckets.items(), key=lambda x: float(x[0]) if x[0] not in ("+Inf", "inf", float("inf")) else float("inf"))
        
        # Buckets are already cumulative in the input
        for boundary, count in sorted_buckets:
            # Handle inf variations
            if boundary == float("inf") or boundary == "inf":
                boundary = "+Inf"
            if base_labels:
                output.append(f'{name}_bucket{{{base_labels},le="{boundary}"}} {count}')
            else:
                output.append(f'{name}_bucket{{le="{boundary}"}} {count}')
                
        # Add +Inf bucket if not present
        if "+Inf" not in [str(b) if b != float("inf") else "+Inf" for b, _ in buckets.items()]:
            if base_labels:
                output.append(f'{name}_bucket{{{base_labels},le="+Inf"}} {count_value}')
            else:
                output.append(f'{name}_bucket{{le="+Inf"}} {count_value}')
                
        # Add sum and count
        if base_labels:
            output.append(f"{name}_sum{{{base_labels}}} {sum_value}")
            output.append(f"{name}_count{{{base_labels}}} {count_value}")
        else:
            output.append(f"{name}_sum {sum_value}")
            output.append(f"{name}_count {count_value}")
            
        return "\n".join(output)
        
    def format_summary(self, metric_data: Dict[str, Any]) -> str:
        """Format summary metric.
        
        Args:
            metric_data: Metric data with name, quantiles, sum, count, labels, etc.
            
        Returns:
            Formatted summary string
        """
        name = metric_data["name"]
        quantiles = metric_data.get("quantiles", {})
        sum_value = metric_data.get("sum", 0)
        count_value = metric_data.get("count", 0)
        labels = metric_data.get("labels", {})
        help_text = metric_data.get("description", metric_data.get("help", f"Summary {name}"))
        
        output = []
        output.append(f"# HELP {name} {help_text}")
        output.append(f"# TYPE {name} summary")
        
        # Format quantile lines
        base_labels = self._format_labels(labels) if labels else ""
        
        for quantile, value in sorted(quantiles.items()):
            if base_labels:
                output.append(f'{name}{{{base_labels},quantile="{quantile}"}} {value}')
            else:
                output.append(f'{name}{{quantile="{quantile}"}} {value}')
                
        # Add sum and count
        if base_labels:
            output.append(f"{name}_sum{{{base_labels}}} {sum_value}")
            output.append(f"{name}_count{{{base_labels}}} {count_value}")
        else:
            output.append(f"{name}_sum {sum_value}")
            output.append(f"{name}_count {count_value}")
            
        return "\n".join(output)
        
    def _format_labels(self, labels: Dict[str, str]) -> str:
        """Format labels for Prometheus.
        
        Args:
            labels: Dictionary of label key-value pairs
            
        Returns:
            Formatted label string
        """
        if not labels:
            return ""
            
        formatted = []
        for key, value in labels.items():
            # Escape special characters
            escaped_value = self._escape_label_value(str(value))
            formatted.append(f'{key}="{escaped_value}"')
            
        return ",".join(formatted)
        
    def _escape_label_value(self, value: str) -> str:
        """Escape special characters in label values.
        
        Args:
            value: Label value to escape
            
        Returns:
            Escaped label value
        """
        # Escape backslashes first, then quotes, then newlines
        value = value.replace("\\", "\\\\")
        value = value.replace('"', '\\"')
        value = value.replace("\n", "\\n")
        return value

    def format_metric(self, metric_data: Dict[str, Any]) -> str:
        """Format a metric based on its type.
        
        Args:
            metric_data: Metric data including type, name, value, labels, etc.
            
        Returns:
            Formatted metric string
        """
        metric_type = metric_data.get("type", "untyped")
        
        if metric_type == "counter":
            return self.format_counter(metric_data)
        elif metric_type == "gauge":
            return self.format_gauge(metric_data)
        elif metric_type == "histogram":
            return self.format_histogram(metric_data)
        elif metric_type == "summary":
            return self.format_summary(metric_data)
        else:
            # Default to gauge for untyped metrics
            return self.format_gauge(metric_data)
    
    def is_valid_metric_name(self, name: str) -> bool:
        """Check if a metric name is valid according to Prometheus naming rules.
        
        Args:
            name: Metric name to validate
            
        Returns:
            True if valid, False otherwise
        """
        import re
        # Prometheus metric names must match [a-zA-Z_:][a-zA-Z0-9_:]*
        pattern = r'^[a-zA-Z_:][a-zA-Z0-9_:]*$'
        return bool(re.match(pattern, name))

    def sanitize_metric_name(self, name: str) -> str:
        """Sanitize metric name to be Prometheus-compliant.
        
        Args:
            name: Metric name to sanitize
            
        Returns:
            Sanitized metric name
        """
        # Replace invalid characters with underscores
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_:]', '_', name)
        
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = '_' + sanitized
            
        return sanitized


class LabelSanitizer:
    """Sanitizes metric and label names for Prometheus compatibility."""
    
    def __init__(self):
        """Initialize label sanitizer."""
        # Prometheus metric name regex
        self.metric_name_re = re.compile(r"^[a-zA-Z_:][a-zA-Z0-9_:]*$")
        # Prometheus label name regex
        self.label_name_re = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
        
    def sanitize_metric_name(self, name: str) -> str:
        """Sanitize metric name for Prometheus.
        
        Args:
            name: Original metric name
            
        Returns:
            Sanitized metric name
        """
        # Replace invalid characters with underscores
        sanitized = re.sub(r"[^a-zA-Z0-9_:]", "_", name)
        
        # Ensure it starts with letter or underscore
        if sanitized and not re.match(r"^[a-zA-Z_:]", sanitized):
            sanitized = "_" + sanitized
            
        # Remove consecutive underscores
        sanitized = re.sub(r"_{2,}", "_", sanitized)
        
        # Validate final name
        if not self.metric_name_re.match(sanitized):
            # Fallback to generic name
            sanitized = f"metric_{hash(name) % 1000000}"
            
        return sanitized
        
    def sanitize_label_name(self, name: str) -> str:
        """Sanitize label name for Prometheus.
        
        Args:
            name: Original label name
            
        Returns:
            Sanitized label name
        """
        original_name = name
        
        # First remove leading double underscores
        if name.startswith("__"):
            name = name[2:]
            
        # Remove trailing double underscores
        if name.endswith("__"):
            name = name[:-2]
        
        # Replace invalid characters with underscores
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        
        # Ensure it starts with letter or underscore
        if sanitized and not re.match(r"^[a-zA-Z_]", sanitized):
            sanitized = "_" + sanitized
            
        # Remove consecutive underscores
        sanitized = re.sub(r"_{2,}", "_", sanitized)
        
        # Reserved label names - append underscore only if original had trailing __
        reserved = {"__name__", "job", "instance", "reserved"}
        if sanitized in reserved and original_name.endswith("__"):
            sanitized = f"{sanitized}_"
            
        # Validate final name
        if not self.label_name_re.match(sanitized):
            # Fallback to generic name
            sanitized = f"label_{hash(name) % 1000000}"
            
        return sanitized

    
    def sanitize_label_value(self, value: Any) -> str:
        """Sanitize label value for Prometheus.
        
        Args:
            value: Original label value
            
        Returns:
            Sanitized label value as string
        """
        # Convert to string
        str_value = str(value)
        
        # Escape special characters for Prometheus
        str_value = str_value.replace('\\', '\\\\')  # Backslash must be first
        str_value = str_value.replace('"', '\\"')
        str_value = str_value.replace('\n', '\\n')
        str_value = str_value.replace('\r', '\\r')
        str_value = str_value.replace('\t', '\\t')
        
        # Limit length
        if len(str_value) > 128:
            str_value = str_value[:125] + "..."
            
        return str_value
        
    def sanitize_labels(self, labels: Dict[str, Any]) -> Dict[str, str]:
        """Sanitize all labels in a dictionary.
        
        Args:
            labels: Original labels dictionary
            
        Returns:
            Sanitized labels dictionary
        """
        sanitized = {}
        for key, value in labels.items():
            sanitized_key = self.sanitize_label_name(key)
            sanitized_value = self.sanitize_label_value(value)
            sanitized[sanitized_key] = sanitized_value
            
        return sanitized
        
    def batch_sanitize(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Batch sanitize multiple metrics.
        
        Args:
            metrics: List of metric dictionaries
            
        Returns:
            List of sanitized metric dictionaries
        """
        sanitized_metrics = []
        
        for metric in metrics:
            sanitized_metric = metric.copy()
            
            # Sanitize metric name
            if "name" in sanitized_metric:
                sanitized_metric["name"] = self.sanitize_metric_name(
                    sanitized_metric["name"]
                )
                
            # Sanitize labels
            if "labels" in sanitized_metric:
                sanitized_metric["labels"] = self.sanitize_labels(
                    sanitized_metric["labels"]
                )
                
            sanitized_metrics.append(sanitized_metric)
            
        return sanitized_metrics


class MetricTypeMapper:
    """Maps between different metric type systems."""
    
    def __init__(self):
        """Initialize metric type mapper."""
        self.otel_to_prometheus_map = {
            "Counter": "counter",
            "UpDownCounter": "gauge",
            "Histogram": "histogram",
            "ObservableCounter": "counter",
            "ObservableUpDownCounter": "gauge",
            "ObservableGauge": "gauge"
        }
        
        self.prometheus_to_otel = {
            "counter": "Counter",
            "gauge": "ObservableGauge",
            "histogram": "Histogram",
            "summary": "Histogram"
        }
        
    def map_otel_to_prometheus(self, otel_type: str) -> str:
        """Map OpenTelemetry metric type to Prometheus.
        
        Args:
            otel_type: OpenTelemetry metric type
            
        Returns:
            Prometheus metric type
        """
        return self.otel_to_prometheus_map.get(otel_type, "untyped")
        
    def map_prometheus_to_otel(self, prom_type: str) -> str:
        """Map Prometheus metric type to OpenTelemetry.
        
        Args:
            prom_type: Prometheus metric type
            
        Returns:
            OpenTelemetry metric type
        """
        return self.prometheus_to_otel.get(prom_type, "Counter")
        
    def validate_type(self, metric_type: str, system: str = "prometheus") -> bool:
        """Validate if metric type is valid for the system.
        
        Args:
            metric_type: Metric type to validate
            system: Metric system (prometheus or opentelemetry)
            
        Returns:
            True if valid, False otherwise
        """
        if system == "prometheus":
            valid_types = {"counter", "gauge", "histogram", "summary", "untyped"}
            return metric_type in valid_types
        elif system == "opentelemetry":
            valid_types = set(self.otel_to_prometheus.keys())
            return metric_type in valid_types
        else:
            return False

    
    # Wrapper methods for backward compatibility with tests
    def otel_to_prometheus(self, otel_type: str) -> str:
        """Wrapper for map_otel_to_prometheus for backward compatibility."""
        return self.map_otel_to_prometheus(otel_type)
    
    def custom_to_prometheus(self, custom_type: str) -> str:
        """Map custom metric types to Prometheus types.
        
        Args:
            custom_type: Custom metric type name
            
        Returns:
            Prometheus metric type
        """
        custom_mappings = {
            "incrementing_counter": "counter",
            "current_value": "gauge",
            "distribution": "histogram",
            "percentiles": "summary"
        }
        return custom_mappings.get(custom_type, "untyped")
    
    def is_valid_prometheus_type(self, metric_type: str) -> bool:
        """Check if a metric type is valid for Prometheus.
        
        Args:
            metric_type: Metric type to validate
            
        Returns:
            True if valid, False otherwise
        """
        return self.validate_type(metric_type, "prometheus")


class MetricsHTTPServer:
    """HTTP server for Prometheus metrics endpoint."""
    
    def __init__(self, port: int = 9090, path: str = "/metrics"):
        """Initialize metrics HTTP server.
        
        Args:
            port: Port to listen on
            path: Path for metrics endpoint
        """
        self.port = port
        self.path = path
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[Thread] = None
        self.metrics_callback: Optional[callable] = None
        self._is_running = False
        
    def set_metrics_callback(self, callback: callable):
        """Set callback function to get metrics.
        
        Args:
            callback: Function that returns metrics in Prometheus format
        """
        self.metrics_callback = callback
        
    async def start(self):
        """Start the metrics HTTP server asynchronously.
        
        This method is async for compatibility with test expectations.
        The actual server runs in a background thread.
        """
        if self._is_running:
            return
            
        class MetricsHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(handler_self):
                if handler_self.path == self.path:
                    # Serve metrics
                    if self.metrics_callback:
                        try:
                            metrics = self.metrics_callback()
                            handler_self.send_response(200)
                            handler_self.send_header("Content-Type", CONTENT_TYPE_LATEST)
                            handler_self.end_headers()
                            handler_self.wfile.write(metrics.encode())
                        except Exception as e:
                            handler_self.send_response(500)
                            handler_self.end_headers()
                            handler_self.wfile.write(f"Error: {str(e)}".encode())
                    else:
                        handler_self.send_response(503)
                        handler_self.end_headers()
                        handler_self.wfile.write(b"No metrics callback registered")
                elif handler_self.path == "/health":
                    # Health check endpoint
                    handler_self.send_response(200)
                    handler_self.send_header("Content-Type", CONTENT_TYPE_LATEST)
                    handler_self.end_headers()
                    handler_self.wfile.write(b"OK")
                else:
                    handler_self.send_response(404)
                    handler_self.end_headers()
                    
            def log_message(self, format, *args):
                pass  # Suppress logging
                
        self.server = http.server.HTTPServer(("", self.port), MetricsHandler)
        self.thread = threading.Thread(target=self._run_server)
        self.thread.daemon = True
        self.thread.start()
        self._is_running = True
        
        # Give server time to start
        await asyncio.sleep(0.1)
        
    def _run_server(self):
        """Run the HTTP server."""
        self.server.serve_forever()
        
    async def stop(self):
        """Stop the metrics HTTP server."""
        if self.server:
            self.server.shutdown()
            self.server = None
        if self.thread:
            self.thread.join(timeout=1)
            self.thread = None
        self._is_running = False
        
    async def shutdown(self):
        """Shutdown the metrics HTTP server (alias for stop)."""
        await self.stop()
            
    def is_running(self) -> bool:
        """Check if server is running.
        
        Returns:
            True if server is running
        """
        return self._is_running

class PrometheusMetricsExporter:
    """Main Prometheus metrics exporter with registry support."""
    
    def __init__(self, port: int = 9090, registry=None):
        """Initialize Prometheus metrics exporter.
        
        Args:
            port: Port for HTTP server
            registry: Optional Prometheus registry
        """
        self.port = port
        self.registry = registry or {}
        self.formatter = PrometheusFormatter()
        self.server = MetricsHTTPServer(port=port)
        self.metrics = {}
        self._collectors = []
        
    def register_metric(self, metric_name: str, metric_type: str, description: str = "", labels: List[str] = None):
        """Register a new metric.
        
        Args:
            metric_name: Name of the metric
            metric_type: Type of metric (counter, gauge, histogram, summary)
            description: Metric description
            labels: List of label names
        """
        self.metrics[metric_name] = {
            "type": metric_type,
            "description": description,
            "labels": labels or [],
            "values": {}
        }
        
    def update_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Update a metric value.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            labels: Label values
        """
        if metric_name not in self.metrics:
            raise ValueError(f"Metric {metric_name} not registered")
            
        label_key = self._get_label_key(labels)
        self.metrics[metric_name]["values"][label_key] = {
            "value": value,
            "labels": labels or {},
            "timestamp": time.time()
        }
        
    def update_metrics(self, updates: List[Tuple[str, float, Dict[str, str]]]):
        """Update multiple metrics at once.
        
        Args:
            updates: List of (metric_name, value, labels) tuples
        """
        for metric_name, value, labels in updates:
            self.update_metric(metric_name, value, labels)
            
    def collect(self) -> str:
        """Collect all metrics in Prometheus format.
        
        Returns:
            Prometheus formatted metrics string
        """
        output = []
        
        for metric_name, metric_info in self.metrics.items():
            for label_key, value_info in metric_info["values"].items():
                metric_data = {
                    "name": metric_name,
                    "type": metric_info["type"],
                    "description": metric_info["description"],
                    "value": value_info["value"],
                    "labels": value_info["labels"]
                }
                
                if "timestamp" in value_info:
                    metric_data["timestamp"] = value_info["timestamp"]
                    
                formatted = self.formatter.format_metric(metric_data)
                output.append(formatted)
                
        return "\n\n".join(output)
        
    def generate_latest(self) -> str:
        """Generate latest metrics in Prometheus format.
        
        Returns:
            Prometheus formatted metrics string
        """
        return self.collect()
        
    def add_collector(self, collector):
        """Add a custom collector.
        
        Args:
            collector: Collector instance with collect() method
        """
        self._collectors.append(collector)
        
    def _get_label_key(self, labels: Dict[str, str] = None) -> str:
        """Generate a unique key for label combination.
        
        Args:
            labels: Label dictionary
            
        Returns:
            Unique label key
        """
        if not labels:
            return ""
        return ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        
    async def start(self):
        """Start the HTTP server."""
        self.server.set_metrics_callback(self.collect)
        await self.server.start()
        
    async def shutdown(self):
        """Shutdown the HTTP server."""
        await self.server.shutdown()


class PrometheusMetricsExporter:
    """Main Prometheus metrics exporter."""
    
    def __init__(self, port: int = 9090, path: str = "/metrics", registry=None):
        """Initialize Prometheus metrics exporter.
        
        Args:
            port: Port for HTTP server
            path: Path for metrics endpoint
            registry: Optional prometheus_client CollectorRegistry for compatibility
        """
        self.formatter = PrometheusFormatter()
        self.sanitizer = LabelSanitizer()
        self.type_mapper = MetricTypeMapper()
        self.http_server = MetricsHTTPServer(port, path)
        
        # Store the registry for compatibility with prometheus_client
        self.registry = registry
        
        self._metrics_registry: Dict[str, Dict[str, Any]] = {}
        self._metric_families: Dict[str, str] = {}  # name -> type
        self._custom_collectors: List[callable] = []
        self._metrics: Dict[str, Any] = {}  # Store prometheus_client metric objects
        
        # Set up HTTP server callback
        self.http_server.set_metrics_callback(self.export)
        
    def register_metric(
        self,
        name: str,
        metric_type: str,
        help_text: str = "",
        labels: List[str] = None
    ):
        """Register a metric with the exporter.
        
        Args:
            name: Metric name
            metric_type: Type of metric (counter, gauge, histogram, summary)
            help_text: Help text for the metric
            labels: List of label names
        """
        sanitized_name = self.sanitizer.sanitize_metric_name(name)
        
        if not self.type_mapper.validate_type(metric_type, "prometheus"):
            raise ValueError(f"Invalid metric type: {metric_type}")
            
        self._metric_families[sanitized_name] = metric_type
        self._metrics_registry[sanitized_name] = {
            "type": metric_type,
            "help": help_text or f"{metric_type} {name}",
            "labels": labels or [],
            "values": defaultdict(lambda: {"value": 0})
        }
        
    def update_metric(
        self,
        name: str,
        value: float,
        labels: Dict[str, str] = None,
        operation: str = "set"
    ):
        """Update a metric value.
        
        Args:
            name: Metric name
            value: New value
            labels: Label values
            operation: Operation (set, inc, dec)
        """
        sanitized_name = self.sanitizer.sanitize_metric_name(name)
        
        if sanitized_name not in self._metrics_registry:
            # Auto-register if not exists
            self.register_metric(sanitized_name, "gauge")
            
        metric = self._metrics_registry[sanitized_name]
        sanitized_labels = self.sanitizer.sanitize_labels(labels or {})
        label_key = frozenset(sanitized_labels.items())
        
        if operation == "set":
            metric["values"][label_key]["value"] = value
        elif operation == "inc":
            metric["values"][label_key]["value"] += value
        elif operation == "dec":
            metric["values"][label_key]["value"] -= value
            
        metric["values"][label_key]["labels"] = sanitized_labels
        metric["values"][label_key]["timestamp"] = time.time()
        
    def bulk_update(self, updates: List[Dict[str, Any]]):
        """Bulk update multiple metrics.
        
        Args:
            updates: List of metric updates
        """
        for update in updates:
            name = update["name"]
            metric_type = update.get("type", "gauge")
            labels = update.get("labels", {})
            
            # Register the metric if not already registered
            if name not in self._metrics:
                if metric_type == "counter":
                    metric = self.register_counter(name, f"{name} metric", list(labels.keys()))
                elif metric_type == "gauge":
                    metric = self.register_gauge(name, f"{name} metric", list(labels.keys()))
                elif metric_type == "histogram":
                    metric = self.register_histogram(name, f"{name} metric", list(labels.keys()))
                else:
                    # Default to gauge
                    metric = self.register_gauge(name, f"{name} metric", list(labels.keys()))
                
                self._metrics[name] = metric
            else:
                metric = self._metrics[name]
            
            # Update the metric value
            if metric_type == "histogram":
                # Handle histogram with multiple values
                values = update.get("values", [])
                if hasattr(metric, 'labels'):
                    labeled_metric = metric.labels(**labels) if labels else metric
                else:
                    labeled_metric = metric
                    
                for value in values:
                    if hasattr(labeled_metric, 'observe'):
                        labeled_metric.observe(value)
            else:
                # Handle counter and gauge
                value = update.get("value", 0)
                if hasattr(metric, 'labels'):
                    labeled_metric = metric.labels(**labels) if labels else metric
                else:
                    labeled_metric = metric
                
                if metric_type == "counter":
                    if hasattr(labeled_metric, 'inc'):
                        labeled_metric.inc(value)
                else:  # gauge
                    if hasattr(labeled_metric, 'set'):
                        labeled_metric.set(value)
            
    def add_custom_collector(self, collector: callable):
        """Add a custom metrics collector.
        
        Args:
            collector: Function that returns metrics in dict format
        """
        self._custom_collectors.append(collector)
        
    def export(self) -> str:
        """Export all metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        # If we have a real prometheus_client registry, use it
        if self.registry and hasattr(self.registry, '__module__'):
            from prometheus_client import generate_latest
            return generate_latest(self.registry).decode('utf-8')
        
        # Otherwise use the manual export format
        output = []
        
        # Export registered metrics
        for name, metric in self._metrics_registry.items():
            metric_type = metric["type"]
            help_text = metric["help"]
            
            # Add HELP and TYPE lines once per metric family
            output.append(f"# HELP {name} {help_text}")
            output.append(f"# TYPE {name} {metric_type}")
            
            # Add metric values
            for label_set, value_data in metric["values"].items():
                value = value_data["value"]
                labels = value_data.get("labels", {})
                
                if labels:
                    label_str = self.formatter._format_labels(labels)
                    output.append(f"{name}{{{label_str}}} {value}")
                else:
                    output.append(f"{name} {value}")
                    
        # Collect from custom collectors
        for collector in self._custom_collectors:
            try:
                custom_metrics = collector()
                if custom_metrics:
                    output.append("")  # Empty line separator
                    output.append(custom_metrics)
            except Exception as e:
                logger.error(f"Error in custom collector: {e}")
                
        return "\n".join(output) + "\n"
        
    def start_http_server(self):
        """Start the HTTP server for metrics endpoint."""
        self.http_server.start()
        
    def stop_http_server(self):
        """Stop the HTTP server."""
        self.http_server.stop()
        
    def get_metric_families(self) -> Dict[str, str]:
        """Get all registered metric families.
        
        Returns:
            Dictionary of metric names to types
        """
        return self._metric_families.copy()

    def register_counter(self, name: str, description: str = "", labels: List[str] = None):
        """Register a counter metric with prometheus_client compatibility.
        
        Args:
            name: Metric name
            description: Metric description
            labels: List of label names
            
        Returns:
            Counter-like object from prometheus_client
        """
        # If we have a real prometheus_client registry, use it
        if self.registry and hasattr(self.registry, '__module__'):
            from prometheus_client import Counter
            return Counter(name, description, labels or [], registry=self.registry)
        
        # Otherwise, register with our internal registry
        self.register_metric(name, "counter", description, labels=labels or [])
        
        # Return a mock counter object for testing
        class MockCounter:
            def __init__(self, name):
                self.name = name
                self._labels = {}
                
            def labels(self, **kwargs):
                key = str(kwargs)
                if key not in self._labels:
                    self._labels[key] = MockMetric()
                return self._labels[key]
                
        class MockMetric:
            def __init__(self):
                self.value = 0
                
            def inc(self, amount=1):
                self.value += amount
                
        return MockCounter(name)
    
    def register_gauge(self, name: str, description: str = "", labels: List[str] = None):
        """Register a gauge metric with prometheus_client compatibility.
        
        Args:
            name: Metric name
            description: Metric description
            labels: List of label names
            
        Returns:
            Gauge-like object from prometheus_client
        """
        # If we have a real prometheus_client registry, use it
        if self.registry and hasattr(self.registry, '__module__'):
            from prometheus_client import Gauge
            return Gauge(name, description, labels or [], registry=self.registry)
        
        # Otherwise, register with our internal registry
        self.register_metric(name, "gauge", description, labels=labels or [])
        
        # Return a mock gauge object for testing
        class MockGauge:
            def __init__(self, name):
                self.name = name
                self._labels = {}
                
            def labels(self, **kwargs):
                key = str(kwargs)
                if key not in self._labels:
                    self._labels[key] = MockMetric()
                return self._labels[key]
                
        class MockMetric:
            def __init__(self):
                self.value = 0
                
            def set(self, value):
                self.value = value
                
            def inc(self, amount=1):
                self.value += amount
                
            def dec(self, amount=1):
                self.value -= amount
                
        return MockGauge(name)
    
    def register_histogram(self, name: str, description: str = "", labels: List[str] = None, buckets=None):
        """Register a histogram metric with prometheus_client compatibility."""
        if self.registry and hasattr(self.registry, '__module__'):
            # Using real prometheus_client
            from prometheus_client import Histogram
            # Use default buckets if none provided
            if buckets is None:
                return Histogram(name, description, labels or [], registry=self.registry)
            else:
                return Histogram(name, description, labels or [], registry=self.registry, buckets=buckets)
        else:
            # Mock implementation for testing
            class MockHistogram:
                def __init__(self, name, description, labels):
                    self.name = name
                    self.description = description
                    self.label_names = labels
                    self._metrics = {}
                
                def labels(self, **kwargs):
                    key = tuple(sorted(kwargs.items()))
                    if key not in self._metrics:
                        self._metrics[key] = MockHistogram(self.name, self.description, [])
                    return self._metrics[key]
                
                def observe(self, value):
                    pass
            
            return MockHistogram(name, description, labels or [])
    
    def update_metrics(self, metrics: Dict[str, Any]):
        """Update multiple metrics at once.
        
        Args:
            metrics: Dictionary of metric updates
        """
        self.bulk_update(metrics)
    
    async def start(self):
        """Start the HTTP server (async version)."""
        await self.http_server.start()
    
    async def shutdown(self):
        """Shutdown the exporter and HTTP server."""
        await self.http_server.shutdown()

    def push_metric(self, name: str, value: float, labels: Dict[str, str] = None, timestamp: int = None):
        """Push a metric with an optional timestamp (for push gateway).
        
        Args:
            name: Metric name
            value: Metric value
            labels: Optional labels
            timestamp: Optional timestamp in milliseconds
        """
        # Store metric with timestamp for push gateway use
        if not hasattr(self, '_timestamped_metrics'):
            self._timestamped_metrics = {}
        
        metric_key = (name, tuple(sorted((labels or {}).items())))
        self._timestamped_metrics[metric_key] = {
            'name': name,
            'value': value,
            'labels': labels or {},
            'timestamp': timestamp
        }
        
        # Also update the regular metric
        self.update_metric(name, value, labels)
    
    def get_metrics_with_timestamps(self) -> Dict[str, Any]:
        """Get metrics with timestamps for push gateway.
        
        Returns:
            Dictionary containing metrics with timestamps
        """
        if not hasattr(self, '_timestamped_metrics'):
            return {}
        
        result = {}
        for metric_key, metric_data in self._timestamped_metrics.items():
            name = metric_data['name']
            # Use name as key for easier access in tests
            result[name] = {
                'value': metric_data['value'],
                'labels': metric_data['labels'],
                'timestamp': metric_data.get('timestamp')
            }
        
        return result
    
    def start_http_server_sync(self):
        """Start the HTTP server synchronously."""
        import asyncio
        asyncio.run(self.start())
    
    async def start_http_server(self):
        """Start the HTTP server asynchronously."""
        await self.http_server.start()
