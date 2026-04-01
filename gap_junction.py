from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class GapJunctionSymmetric:
    adj: Dict[str, List[Tuple[str, float]]]
    deg: Dict[str, float]

    @classmethod
    def from_excel_connectome(cls, excel_connectome):
        pair_g = {}
        for a, lst in excel_connectome.edges.items():
            for b, g in lst:
                if a == b or g == 0:
                    continue
                x, y = (a, b) if a < b else (b, a)
                pair_g[(x, y)] = pair_g.get((x, y), 0.0) + float(g)

        adj = {}
        deg = {}
        for (x, y), g in pair_g.items():
            adj.setdefault(x, []).append((y, g))
            adj.setdefault(y, []).append((x, g))
            deg[x] = deg.get(x, 0.0) + g
            deg[y] = deg.get(y, 0.0) + g
        return cls(adj=adj, deg=deg)

    def apply_step(self, postsynaptic, this_idx, next_idx, gain=0.08, dt=1.0, normalize_by_degree=True):
        processed = set()
        delta = {}

        for a, neighbors in self.adj.items():
            if a not in postsynaptic:
                continue
            va = float(postsynaptic[a][this_idx])

            for b, g in neighbors:
                if b not in postsynaptic:
                    continue
                edge = tuple(sorted((a, b)))
                if edge in processed:
                    continue
                processed.add(edge)

                vb = float(postsynaptic[b][this_idx])
                local_gain = gain * dt * float(g)

                if normalize_by_degree:
                    da = max(self.deg.get(a, 1.0), 1.0)
                    db = max(self.deg.get(b, 1.0), 1.0)
                    local_gain *= 2.0 / (da + db)

                local_gain = min(local_gain, 0.45)
                flow = local_gain * (vb - va)

                delta[a] = delta.get(a, 0.0) + flow
                delta[b] = delta.get(b, 0.0) - flow

        for n, dv in delta.items():
            postsynaptic[n][next_idx] += dv
