"""
PhantomGuard Ensemble Anomaly Detection
Combines Isolation Forest and One-Class SVM for robust event anomaly scoring.
"""
from typing import List, Dict
import numpy as np
import importlib

try:
    sklearn_ensemble = importlib.import_module('sklearn.ensemble')
    IsolationForest = getattr(sklearn_ensemble, 'IsolationForest')
    sklearn_svm = importlib.import_module('sklearn.svm')
    OneClassSVM = getattr(sklearn_svm, 'OneClassSVM')
    SKLEARN_AVAILABLE = True
except Exception:
    SKLEARN_AVAILABLE = False
    IsolationForest = None
    OneClassSVM = None


class EnsembleAnomalyModel:
    def __init__(self):
        self.trained = False
        if SKLEARN_AVAILABLE:
            self.iso = IsolationForest(n_estimators=100, contamination=0.05)
            self.svm = OneClassSVM(gamma='auto')
        else:
            self.iso = None
            self.svm = None

    def fit(self, events: List[Dict]):
        if not SKLEARN_AVAILABLE:
            raise RuntimeError(
                'scikit-learn not installed; cannot train EnsembleAnomalyModel')
        X = self._extract_features(events)
        self.iso.fit(X)
        self.svm.fit(X)
        self.trained = True

    def score(self, event: Dict) -> float:
        X = self._extract_features([event])
        if not self.trained:
            return 0.0
        score_iso = -self.iso.decision_function(X)[0]
        score_svm = -self.svm.decision_function(X)[0]
        return (score_iso + score_svm) / 2

    def _extract_features(self, events: List[Dict]) -> np.ndarray:
        features = []
        for e in events:
            features.append([
                hash(e.get('event_type', '')) % 1000,
                len(e.get('path', '')),
                e.get('size', 0),
                e.get('hour', 0),
                hash(e.get('user', '')) % 1000
            ])
        return np.array(features)
