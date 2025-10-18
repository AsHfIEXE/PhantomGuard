"""
PhantomGuard Anomaly Detection
Isolation Forest for event anomaly scoring.
"""
from typing import List, Dict
import numpy as np
import importlib

try:
    sklearn_ensemble = importlib.import_module('sklearn.ensemble')
    IsolationForest = getattr(sklearn_ensemble, 'IsolationForest')
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False
    IsolationForest = None


class AnomalyModel:
    def __init__(self):
        self.trained = False
        if SKLEARN_AVAILABLE:
            self.model = IsolationForest(n_estimators=50, contamination=0.05)
        else:
            self.model = None

    def fit(self, events: List[Dict]):
        if not SKLEARN_AVAILABLE:
            raise RuntimeError(
                'scikit-learn not installed; cannot train AnomalyModel')
        X = self._extract_features(events)
        self.model.fit(X)
        self.trained = True

    def score(self, event: Dict) -> float:
        X = self._extract_features([event])
        if not self.trained:
            return 0.0
        return -self.model.decision_function(X)[0]

    def _extract_features(self, events: List[Dict]) -> np.ndarray:
        # Example: use event_type, path length, method, score
        features = []
        for e in events:
            features.append([
                hash(e.get('event_type', '')) % 1000,
                len(e.get('path', '')),
                hash(e.get('method', '')) % 100 if 'method' in e else 0,
                e.get('score', 0)
            ])
        return np.array(features)
