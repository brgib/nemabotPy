"""excel_connectome_pylightxl.py

Excel connectome loader based on excel_matrix_pylightxl.read_adjacency_matrix (pylightxl).
Designed to integrate with Nemabot's simulator.py which expects:
- .apply(presynaptic, postsynaptic, nextState)
- .ensure_postsynaptic_entries(postsynaptic)
- .reset_postsynaptic(postsynaptic)
- .edges dict
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from excel_matrix_pylightxl import read_adjacency_matrix

Weight = float
EdgeList = List[Tuple[str, Weight]]

# Nemabot postsynaptic vector layout (per connectome.py conventions)
THIS_STATE = 0
NEXT_STATE = 1
PREV_VALUE = 2
ACTIVATED = 3
KIND = 4  # used by your code as a decay/type flag


@dataclass
class ExcelConnectomePylightxl:
    sheet_name: str
    neurons: List[str]
    edges: Dict[str, EdgeList]

    @classmethod
    def load(cls, xlsx_path: str, sheet_name: str) -> "ExcelConnectomePylightxl":
        neurons, mat = read_adjacency_matrix(xlsx_path, sheet_name)
        edges: Dict[str, EdgeList] = {
            src: [(dst, float(w)) for dst, w in dsts.items()]
            for src, dsts in mat.items()
        }
        return cls(sheet_name=sheet_name, neurons=list(neurons), edges=edges)

    def ensure_postsynaptic_entries(self, postsynaptic: Dict[str, list], default_kind: int = 0) -> None:
        """Ensure postsynaptic has entries for all neurons in this connectome."""
        for n in self.neurons:
            if n not in postsynaptic:
                postsynaptic[n] = [0.0, 0.0, 0.0, 0.0, default_kind]

    def reset_postsynaptic(self, postsynaptic: Dict[str, list]) -> None:
        """Reset (this/next/prev/activated) for neurons present in this connectome."""
        for n in self.neurons:
            if n in postsynaptic:
                postsynaptic[n][THIS_STATE] = 0.0
                postsynaptic[n][NEXT_STATE] = 0.0
                postsynaptic[n][PREV_VALUE] = 0.0
                postsynaptic[n][ACTIVATED] = 0.0

    def apply(self, presynaptic: str, postsynaptic: Dict[str, list], next_state_index: int) -> None:
        """Apply outgoing edges of presynaptic to postsynaptic[next_state_index]."""
        for target, w in self.edges.get(presynaptic, []):
            if target in postsynaptic:
                postsynaptic[target][next_state_index] = postsynaptic[target][next_state_index] + w
