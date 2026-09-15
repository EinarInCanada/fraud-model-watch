"""Pure, dependency-free timing, ranking, and evidence-gate primitives."""

from dataclasses import dataclass
import math


def _integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


def label_available_at(event_month, delay=1):
    _integer(event_month, "event_month")
    _integer(delay, "delay")
    return event_month + 1 + delay


def available_training_months(decision_month, delay=1):
    _integer(decision_month, "decision_month")
    _integer(delay, "delay")
    return tuple(range(max(0, decision_month - delay)))


def capacity_metrics(labels, scores, fraction=0.01):
    """Inputs must follow source row order; labels never determine rank."""
    labels, scores = tuple(labels), tuple(scores)
    if len(labels) != len(scores):
        raise ValueError("labels and scores must have the same length")
    if any(type(y) is not int or y not in (0, 1) for y in labels):
        raise ValueError("labels must be integer 0 or 1")
    if not isinstance(fraction, (int, float)) or isinstance(fraction, bool):
        raise ValueError("fraction must be numeric")
    if not math.isfinite(fraction) or not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    if any(isinstance(s, bool) or not isinstance(s, (int, float))
           or not math.isfinite(s) or not 0 <= s <= 1 for s in scores):
        raise ValueError("scores must be finite probabilities")
    n = len(labels)
    k = math.floor(fraction * n)
    selected = sorted(range(n), key=lambda i: (-scores[i], i))[:k]
    positives = sum(labels)
    captured = sum(labels[i] for i in selected)
    return {
        "n": n, "positives": positives, "k": k,
        "captured": captured, "false_positives": k - captured,
        "precision_at_k": captured / k if k else None,
        "recall_at_k": captured / positives if positives else None,
        "selected_positions": selected,
    }


@dataclass(frozen=True)
class Evidence:
    """Aggregate from already stored frozen-sentinel predictions."""
    month: int
    positives: int
    captured: int

    def __post_init__(self):
        _integer(self.month, "month")
        _integer(self.positives, "positives")
        _integer(self.captured, "captured")
        if self.captured > self.positives:
            raise ValueError("captured cannot exceed positives")

    @property
    def recall(self):
        return self.captured / self.positives if self.positives else None


def evidence_gate(decision_month, reference, history, last_refit=None, delay=1):
    """Protocol-v1 heuristic, not a significance test or causal diagnosis.

    Reject future feedback rather than silently using or filtering it.
    The caller must supply metrics from stored sentinel scores; this function
    cannot independently verify their origin.
    """
    available = available_training_months(decision_month, delay)
    history = tuple(history)
    if reference.month != 2:
        raise ValueError("protocol v1 requires month 2 reference")
    if any(e.month not in available for e in (reference,) + history):
        raise ValueError("unavailable feedback: possible future-label leakage")
    if len({e.month for e in history}) != len(history):
        raise ValueError("duplicate evidence month")
    if last_refit is not None:
        _integer(last_refit, "last_refit")
        if last_refit >= decision_month:
            raise ValueError("last_refit must precede decision_month")
        if decision_month - last_refit < 2:
            return False, "cooldown"
    latest = available[-1]
    by_month = {e.month: e for e in history}
    wanted = (latest - 1, latest)
    if wanted[0] <= reference.month or any(m not in by_month for m in wanted):
        return False, "insufficient_consecutive_post_reference_evidence"
    recent = tuple(by_month[m] for m in wanted)
    if any(e.positives < 30 for e in (reference,) + recent):
        return False, "insufficient_positive_labels"
    # Integer cross-multiplication implements an exact 5-percentage-point drop.
    degraded = all(
        20 * (reference.captured * e.positives - e.captured * reference.positives)
        >= reference.positives * e.positives
        for e in recent
    )
    return (True, "persistent_recall_drop") if degraded else (False, "hold")
