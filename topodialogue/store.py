import json, sqlite3
from pathlib import Path
from .models import DialogueTurn, SemanticNode, SemanticEdge, StateSnapshot, LoopDecision, OperatorDecision, OutcomeWindow

class SQLiteStore:
    def __init__(self, path: str | Path = ":memory:"):
        self.db = sqlite3.connect(str(path)); self.db.executescript("""CREATE TABLE IF NOT EXISTS turns(id TEXT PRIMARY KEY, payload TEXT); CREATE TABLE IF NOT EXISTS nodes(id TEXT PRIMARY KEY, payload TEXT); CREATE TABLE IF NOT EXISTS edges(id TEXT PRIMARY KEY, payload TEXT); CREATE TABLE IF NOT EXISTS snapshots(id TEXT PRIMARY KEY, payload TEXT); CREATE TABLE IF NOT EXISTS loop_decisions(id TEXT PRIMARY KEY, payload TEXT); CREATE TABLE IF NOT EXISTS operator_decisions(id TEXT PRIMARY KEY, payload TEXT); CREATE TABLE IF NOT EXISTS outcomes(id TEXT PRIMARY KEY, payload TEXT);""")
    def put(self, item):
        table = {DialogueTurn:"turns", SemanticNode:"nodes", SemanticEdge:"edges", StateSnapshot:"snapshots", LoopDecision:"loop_decisions", OperatorDecision:"operator_decisions", OutcomeWindow:"outcomes"}[type(item)]
        key = getattr(item, "turn_id", getattr(item, "node_id", getattr(item, "edge_id", getattr(item, "snapshot_id", getattr(item, "intervention_decision_id", getattr(item, "decision_id", ""))))))
        self.db.execute(f"INSERT OR REPLACE INTO {table}(id,payload) VALUES (?,?)", (key, json.dumps(item.model_dump(mode="json"), ensure_ascii=False))); self.db.commit()
    def count(self, table: str) -> int: return self.db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
