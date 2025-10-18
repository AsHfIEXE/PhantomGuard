"""
PhantomGuard Hybrid Anomaly Detection
Combines Isolation Forest, One-Class SVM, and a deep autoencoder for best-in-class event anomaly scoring.
"""
from typing import List, Dict, Any, Optional, Protocol, Union, Callable, Type
import numpy as np
import importlib

# Optional dependencies loaded dynamically with type hints
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

try:
    torch = importlib.import_module('torch')
    nn = importlib.import_module('torch.nn')
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False
    torch = None
    nn = None

# Type for tensor-like objects (numpy arrays or torch tensors)
TensorLike = Union[np.ndarray, Any]  # Any covers torch.Tensor when available

class AutoencoderBase(Protocol):
    """Protocol for autoencoder interface."""
    def __call__(self, x: TensorLike) -> TensorLike: ...

# Define autoencoder implementation based on torch availability
if TORCH_AVAILABLE and nn is not None:
    class EventAutoencoder(nn.Module):  # type: ignore
        """PyTorch-based autoencoder implementation."""
        def __init__(self, input_dim: int) -> None:
            super().__init__()
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, 32), nn.ReLU(),
                nn.Linear(32, 8), nn.ReLU()
            )
            self.decoder = nn.Sequential(
                nn.Linear(8, 32), nn.ReLU(),
                nn.Linear(32, input_dim)
            )

        def forward(self, x: Any) -> Any:  # type: ignore # PyTorch types
            z = self.encoder(x)
            return self.decoder(z)
else:
    class EventAutoencoder:
        """Fallback autoencoder when PyTorch is not available."""
        def __init__(self, input_dim: int) -> None:
            pass

        def __call__(self, x: TensorLike) -> TensorLike:
            return x

import pickle
from pathlib import Path


class HybridAnomalyModel:
    """Hybrid model that gracefully degrades if optional libs are missing."""

    def __init__(self, input_dim: int) -> None:
        self.input_dim = input_dim
        self.trained = False
        
        # Initialize with proper typing
        self.iso: Optional[Any] = None  # IsolationForest when available
        self.svm: Optional[Any] = None  # OneClassSVM when available
        self.autoencoder: Optional[AutoencoderBase] = None
        
        # Create instances if dependencies available
        if SKLEARN_AVAILABLE and IsolationForest is not None and OneClassSVM is not None:
            self.iso = IsolationForest(n_estimators=100, contamination=0.05)
            self.svm = OneClassSVM(gamma='auto')
            
        if TORCH_AVAILABLE:
            self.autoencoder = EventAutoencoder(input_dim)

    @staticmethod
    def extract_features(event: Dict[str, Any]) -> List[float]:
        """Public helper: extract numeric features from an event dict."""
        return [
            hash(event.get('event_type', '')) % 1000,
            len(event.get('path', '')),
            event.get('size', 0) or 0,
            event.get('hour', 0) or 0,
            hash(event.get('user', '')) % 1000
        ]

    def fit(self, events: List[Dict[str, Any]]) -> None:
        """Train the hybrid model on a list of events."""
        if not SKLEARN_AVAILABLE:
            raise RuntimeError(
                'scikit-learn not installed; cannot train HybridAnomalyModel')
        X = np.array([self.extract_features(e) for e in events])
        
        if self.iso is not None:
            self.iso.fit(X)
        if self.svm is not None:
            self.svm.fit(X)
            
        if TORCH_AVAILABLE and self.autoencoder is not None and torch is not None and nn is not None:
            X_tensor = torch.tensor(X, dtype=torch.float32)
            optimizer = torch.optim.Adam(
                self.autoencoder.parameters(), lr=1e-3)  # type: ignore
            loss_fn = nn.MSELoss()
            for epoch in range(10):
                optimizer.zero_grad()
                recon = self.autoencoder(X_tensor)
                loss = loss_fn(recon, X_tensor)
                loss.backward()
                optimizer.step()
        self.trained = True

    def score(self, event: Dict[str, Any]) -> float:
        """Score an event for anomaly detection."""
        X = np.array([self.extract_features(event)])
        if not self.trained:
            return 0.0
        
        scores: List[float] = []
        
        if SKLEARN_AVAILABLE:
            if self.iso is not None:
                scores.append(-float(self.iso.decision_function(X)[0]))
            if self.svm is not None:
                scores.append(-float(self.svm.decision_function(X)[0]))
                
        if TORCH_AVAILABLE and self.autoencoder is not None and torch is not None:
            x_tensor = torch.tensor(X, dtype=torch.float32)
            recon = self.autoencoder(x_tensor)
            s_ae = float(torch.mean((x_tensor - recon) ** 2).item())
            scores.append(s_ae)
            
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    # Backwards compatibility
    def _extract_features(self, events: List[Dict[str, Any]]) -> np.ndarray:
        """Legacy method for backward compatibility."""
        return np.array([self.extract_features(e) for e in events])

    def save(self, path: str) -> bool:
        """Save model to disk. Uses joblib/torch where available, falls back to pickle."""
        p = Path(path)
        # Try sklearn joblib for iso/svm
        try:
            if SKLEARN_AVAILABLE:
                try:
                    joblib = importlib.import_module('joblib')
                    if joblib is not None:
                        joblib.dump({'iso': self.iso, 'svm': self.svm},
                                str(p) + '.skl.joblib')
                except ImportError:
                    # fallback to pickle for sklearn parts
                    with open(str(p) + '.skl.pkl', 'wb') as f:
                        pickle.dump({'iso': self.iso, 'svm': self.svm}, f)
                        
            if TORCH_AVAILABLE and self.autoencoder is not None and torch is not None:
                try:
                    torch.save(
                        self.autoencoder.state_dict(),  # type: ignore
                        str(p) + '.ae.pt')
                except Exception:
                    # ignore torch save errors - will fall back to pickle
                    pass
                    
            # Finally pickle whole object as a robust fallback
            with open(str(p) + '.pkl', 'wb') as f:
                pickle.dump(self, f)
            return True
        except Exception:
            return False

    @classmethod
    def load(cls, path: str) -> 'HybridAnomalyModel':
        """Load model from disk. Attempts to reconstruct from saved artifacts or pickle."""
        p = Path(path)
        # Try pickle first
        try:
            with open(str(p) + '.pkl', 'rb') as f:
                obj = pickle.load(f)
                if not isinstance(obj, cls):
                    raise TypeError(f"Loaded object is not a {cls.__name__}")
                return obj
        except Exception:
            pass
            
        # Build empty model and load pieces if available
        try:
            # Create placeholder model (input_dim unknown; user should manage)
            m = cls(input_dim=5)
            if SKLEARN_AVAILABLE and (
                    p.with_suffix('.skl.joblib').exists() or p.with_suffix('.skl.pkl').exists()):
                try:
                    joblib = importlib.import_module('joblib')
                    if joblib is not None:
                        data = joblib.load(str(p) + '.skl.joblib')
                except Exception:
                    with open(str(p) + '.skl.pkl', 'rb') as f:
                        data = pickle.load(f)
                m.iso = data.get('iso')
                m.svm = data.get('svm')
                m.trained = True
                
            if TORCH_AVAILABLE and p.with_suffix(
                    '.ae.pt').exists() and m.autoencoder is not None and torch is not None:
                try:
                    state = torch.load(str(p) + '.ae.pt')
                    m.autoencoder.load_state_dict(state)  # type: ignore
                except Exception:
                    pass
            return m
        except Exception as e:
            raise RuntimeError(
                f'Failed to load HybridAnomalyModel from path: {path}') from e
