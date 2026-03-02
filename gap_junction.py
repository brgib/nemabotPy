"""gap_junction.py

Electrical coupling model for symmetric gap junction connectomes.

In Nemabot's current architecture, neurons are stored in the global `postsynaptic` dict
(from connectome.py) where each neuron has multiple slots:
  [thisState, nextState, PreviousValue, activated, decroissance]

Chemical synapses in `connectome.py` are event-like (fire -> add weight).

Gap junctions are better modeled as a continuous bidirectional coupling:
  dVi/dt += sum_j g_ij * (Vj - Vi)

This module implements a stable discrete step that can be added to `nextState`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass
class GapJunctionSymmetric:
    """Symmetric gap-junction network as weighted undirected edges.

    Parameters
    ----------
    edges : Iterable[Tuple[str, str, float]]
        Undirected edges (a, b, g). (a,b) order doesn't matter.
    """

    # adjacency list: node -> list[(other, g)]
    adj: Dict[str, List[Tuple[str, float]]]
    # total conductance per node (sum g)
    deg: Dict[str, float]

    @classmethod
    def from_excel_connectome(cls, excel_connectome) -> "GapJunctionSymmetric":
        """Build an undirected network from an ExcelConnectome-like object.

        Expected attributes:
          - excel_connectome.edges: Dict[str, List[Tuple[str, float]]]
        The sheet '... symmetric' usually contains both directions already,
        but we defensively symmetrize and aggregate duplicates.
        """
        pair_g: Dict[Tuple[str, str], float] = {}

        for a, lst in excel_connectome.edges.items():
            for b, g in lst:
                if a == b:
                    continue
                if g == 0:
                    continue
                x, y = (a, b) if a < b else (b, a)
                pair_g[(x, y)] = pair_g.get((x, y), 0.0) + float(g)

        adj: Dict[str, List[Tuple[str, float]]] = {}
        deg: Dict[str, float] = {}

        for (x, y), g in pair_g.items():
            adj.setdefault(x, []).append((y, g))
            adj.setdefault(y, []).append((x, g))
            deg[x] = deg.get(x, 0.0) + g
            deg[y] = deg.get(y, 0.0) + g

        return cls(adj=adj, deg=deg)

    def apply_step(
        self,
        postsynaptic: Dict[str, list],
        this_idx: int,
        next_idx: int,
        *,
        gain: float = 0.01,
        dt: float = 1.0,
        normalize_by_degree: bool = True,
    ) -> None:
        """Apply one discrete coupling step into nextState.

        We compute an Euler-like update:
            next[i] += dt * gain * sum_j g_ij * (Vj - Vi)

        where Vi and Vj are taken from `thisState`.

        Notes
        -----
        - `gain` is a global scaling factor because Excel weights (synapse counts)
          are not physical conductances.
        - When `normalize_by_degree` is True, each node's accumulated coupling is
          divided by max(deg[i], 1) to keep the step stable across high-degree nodes.
        """
        # accumulate deltas per node to avoid order-dependence
        delta: Dict[str, float] = {}

        for i, neigh in self.adj.items():
            if i not in postsynaptic:
                continue
            Vi = float(postsynaptic[i][this_idx])
            acc = 0.0
            for j, g in neigh:
                if j not in postsynaptic:
                    continue
                Vj = float(postsynaptic[j][this_idx])
                acc += g * (Vj - Vi)
            if normalize_by_degree:
                di = self.deg.get(i, 0.0)
                if di > 1e-9:
                    acc /= di
            delta[i] = dt * gain * acc

        for i, d in delta.items():
            postsynaptic[i][next_idx] = float(postsynaptic[i][next_idx]) + d
 