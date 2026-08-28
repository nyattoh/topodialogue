from dataclasses import dataclass, field

@dataclass(frozen=True)
class DetectorConfig:
    window_size: int = 5
    recurrence_threshold: float = .78
    loop_threshold: float = .40
    loop_exit_threshold: float = .38
    hysteresis_turns: int = 2
    cooldown_turns: int = 3
    escape_horizon: int = 5
    weights: dict[str, float] = field(default_factory=lambda: {"recurrence": .27, "graph_cycle": .16, "novelty_decay": .18, "semantic_progress_decay": .16, "motif_recurrence": .11, "constraint_persistence": .12})

    def __post_init__(self):
        if self.window_size < 2 or self.cooldown_turns < 0 or self.escape_horizon < 1:
            raise ValueError("window_size must be >=2 and horizons/cooldown must be non-negative")
        if abs(sum(self.weights.values()) - 1) > 1e-6:
            raise ValueError("weights must sum to 1")
