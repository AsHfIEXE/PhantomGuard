"""
PhantomGuard Playbook (production-ready)
Executes response actions (alert, block, quarantine) based on event score and config.
"""
from typing import Dict, Any, Callable, Optional


class Playbook:
    """
    Executes response actions based on event scores.
    """

    def __init__(self, alert_func: Callable, block_func: Callable,
                 quarantine_func: Optional[Callable] = None):
        self.alert = alert_func
        self.block = block_func
        self.quarantine = quarantine_func

    def handle_event(self, event: Dict[str, Any], score: int, matches: list):
        """
        Orchestrates response actions based on the event's score.

        Args:
            event: The event dictionary.
            score: The calculated score for the event.
            matches: A list of rule names that were matched.
        """
        print(
            f"[Playbook] Handling event for {
                event['path']} with score {score}")
        if score >= 80:
            # Assumes event enrichment
            self.block(event.get("source_ip", "unknown"))
            self.alert(event, urgent=True)
        elif score >= 60:
            self.alert(event)
        elif score >= 40 and self.quarantine:
            self.quarantine(event)
