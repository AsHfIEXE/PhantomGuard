"""
PhantomGuard Event Scorer (production-ready)
Rule-based event scoring for decoy interactions. Config-driven, robust, with docstrings and tests.
"""
import re
from typing import Dict, List, Tuple, Any, Optional

DEFAULT_RULES = [{"name": "open_sensitive_honeytoken",
                  "weight": 50,
                  "pattern": r"/\.ssh/|/\.env|backup\.sql|aws/credentials"},
                 {"name": "execute_fake_binary",
                  "weight": 40,
                  "pattern": r"/fakejob|/fake_cron"},
                 {"name": "write_hidden_dir",
                  "weight": 20,
                  "pattern": r"/\."},
                 {"name": "small_file_read",
                  "weight": 5,
                  "pattern": r"/tmp/"},
                 ]


class EventScorer:
    """
    Scores filesystem events based on a configurable set of rules.
    """

    def __init__(self, rules: Optional[List[Dict[str, Any]]] = None, threshold: int = 60):
        self.rules: List[Dict[str, Any]] = rules or DEFAULT_RULES
        self.threshold = threshold

    def score_event(self, event: Dict) -> Tuple[int, List[str]]:
        """
        Calculates a score for a given event.

        Args:
            event: A dictionary representing the filesystem event.

        Returns:
            A tuple containing the total score and a list of matched rule names.
        """
        path = event.get("path", "")
        score = 0
        matches: List[str] = []
        for rule in self.rules:
            if re.search(rule["pattern"], path):
                score += rule["weight"]
                matches.append(rule["name"])
        return score, matches

    def is_suspicious(self, event: Dict) -> bool:
        """
        Determines if an event's score exceeds the configured threshold.
        """
        score, _ = self.score_event(event)
        return score >= self.threshold
