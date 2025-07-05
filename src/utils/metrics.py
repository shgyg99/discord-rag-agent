from collections import defaultdict
import threading

class MetricsCollector:
    def __init__(self):
        self._metrics = defaultdict(int)
        self._latencies = defaultdict(list)
        self._lock = threading.Lock()
        
    def increment(self, metric_name, value=1):
        with self._lock:
            self._metrics[metric_name] += value
            
    def record_latency(self, metric_name, latency_ms):
        with self._lock:
            self._latencies[metric_name].append(latency_ms)
            # Keep only last 1000 latencies to manage memory
            if len(self._latencies[metric_name]) > 1000:
                self._latencies[metric_name] = self._latencies[metric_name][-1000:]
                
    def get_metrics(self):
        with self._lock:
            metrics = dict(self._metrics)
            # Calculate average latencies
            for name, latencies in self._latencies.items():
                if latencies:
                    metrics[f"{name}_avg_latency"] = sum(latencies) / len(latencies)
                    metrics[f"{name}_max_latency"] = max(latencies)
            return metrics

# Global metrics collector instance
metrics = MetricsCollector()
