"""
Latency Tracker - Track execution time for each module
"""

import time
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class LatencyTracker:
    """Track latency for each processing module"""
    
    def __init__(self):
        self.timings: Dict[str, float] = {}
        self.start_times: Dict[str, float] = {}
        self.total_start = None
        
    def start_total(self):
        """Start tracking total execution time"""
        self.total_start = time.time()
    
    def start(self, module_name: str):
        """Start timing a module"""
        self.start_times[module_name] = time.time()
    
    def end(self, module_name: str):
        """End timing a module"""
        if module_name in self.start_times:
            elapsed = time.time() - self.start_times[module_name]
            self.timings[module_name] = round(elapsed * 1000, 2)  # Convert to ms
            del self.start_times[module_name]
    
    def get_results(self) -> Dict[str, Any]:
        """Get all timing results"""
        total_time = round((time.time() - self.total_start) * 1000, 2) if self.total_start else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_time_ms": total_time,
            "modules": self.timings,
            "breakdown_percent": self._calculate_percentages()
        }
    
    def _calculate_percentages(self) -> Dict[str, float]:
        """Calculate percentage of total time for each module"""
        total = sum(self.timings.values())
        if total == 0:
            return {}
        return {
            module: round((time_ms / total) * 100, 1)
            for module, time_ms in self.timings.items()
        }
    
    def save_to_file(self, filepath: str = "data/latency_results.json"):
        """Save results to JSON file"""
        results = self.get_results()
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to existing results
        existing = []
        if path.exists():
            try:
                with open(path, 'r') as f:
                    loaded = json.load(f)
                    # Handle both list and dict formats for backward compatibility
                    if isinstance(loaded, list):
                        existing = loaded
                    elif isinstance(loaded, dict):
                        # If it's a dict, start fresh with a list
                        existing = []
                    else:
                        existing = []
            except:
                existing = []
        
        existing.append(results)
        
        # Keep only last 100 results
        if len(existing) > 100:
            existing = existing[-100:]
        
        with open(path, 'w') as f:
            json.dump(existing, f, indent=2)
        
        return results
    
    def print_summary(self):
        """Print formatted summary"""
        results = self.get_results()
        print("\n" + "="*60)
        print("LATENCY TRACKING RESULTS")
        print("="*60)
        print(f"Total Time: {results['total_time_ms']} ms")
        print("\nModule Breakdown:")
        print("-"*60)
        
        for module, time_ms in results['modules'].items():
            percent = results['breakdown_percent'].get(module, 0)
            bar = "#" * int(percent / 2)  # Visual bar
            print(f"{module:25} {time_ms:8.2f} ms  {percent:5.1f}%  {bar}")
        
        print("="*60 + "\n")


# Global tracker instance
_tracker = None


def get_tracker() -> LatencyTracker:
    """Get or create global tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = LatencyTracker()
    return _tracker


def reset_tracker():
    """Reset the global tracker"""
    global _tracker
    _tracker = LatencyTracker()
