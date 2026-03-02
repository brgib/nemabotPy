# excel_matrix_pylightxl.py
# Robust adjacency-matrix reader for SI7-like Excel sheets using pylightxl (vendored).
#
# Fixes common layout differences:
# - extra title rows
# - neuron names not necessarily starting at A2
# - avoids assuming fixed (row=2,col=1)

from __future__ import annotations

VERSION = 'autodetect-v1'

from typing import Dict, List, Tuple, Optional

_xl = None
_import_error = None

# --- Robust import handling (package vs module) ---
try:
    from third_party.pylightxl import pylightxl as _xl  # type: ignore
except Exception as e1:
    try:
        import third_party.pylightxl.pylightxl as _xl  # type: ignore
    except Exception as e2:
        try:
            from pylightxl import pylightxl as _xl  # type: ignore
        except Exception as e3:
            try:
                import pylightxl as _xl  # type: ignore
            except Exception as e4:
                _xl = None
                _import_error = e4

_readxl = None
if _xl is not None:
    if hasattr(_xl, "readxl"):
        _readxl = getattr(_xl, "readxl")
    else:
        sub = getattr(_xl, "pylightxl", None)
        if sub is not None and hasattr(sub, "readxl"):
            _readxl = getattr(sub, "readxl")


def pylightxl_available() -> bool:
    return _xl is not None and _readxl is not None


def pylightxl_error() -> str:
    if _xl is None:
        return f"pylightxl import failed: {_import_error}"
    if _readxl is None:
        return "pylightxl imported but readxl() not found (check vendoring layout)"
    return ""


def list_sheets(xlsx_path: str) -> List[str]:
    if not pylightxl_available():
        raise RuntimeError(pylightxl_error())
    db = _readxl(fn=xlsx_path)
    return list(db.ws_names)


def _is_text(v) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        return v.strip() != ""
    return False


def _norm_name(v) -> str:
    return str(v).strip()


def _scan_header_row(ws, *, max_r: int, max_c: int, min_run: int = 20) -> Optional[Tuple[int, int, List[str]]]:
    """
    Find a likely column-header row (neuron names across columns).
    Returns (row_index, start_col, names)
    """
    best = None  # (run_len, row, start_col, names)
    for r in range(1, max_r + 1):
        names: List[str] = []
        start = None
        gap = 0
        for c in range(1, max_c + 1):
            v = ws.index(row=r, col=c)
            if _is_text(v):
                if start is None:
                    start = c
                names.append(_norm_name(v))
                gap = 0
            else:
                if start is not None:
                    gap += 1
                    if gap >= 3:  # 3 consecutive empties => end of run
                        break
        if start is not None and len(names) >= min_run:
            cand = (len(names), r, start, names)
            if best is None or cand[0] > best[0]:
                best = cand
    if best is None:
        return None
    _, r, start, names = best
    return (r, start, names)


def _scan_header_col(ws, *, max_r: int, max_c: int, min_run: int = 20) -> Optional[Tuple[int, int, List[str]]]:
    """
    Find a likely row-header column (neuron names down rows).
    Returns (col_index, start_row, names)
    """
    best = None  # (run_len, col, start_row, names)
    for c in range(1, max_c + 1):
        names: List[str] = []
        start = None
        gap = 0
        for r in range(1, max_r + 1):
            v = ws.index(row=r, col=c)
            if _is_text(v):
                if start is None:
                    start = r
                names.append(_norm_name(v))
                gap = 0
            else:
                if start is not None:
                    gap += 1
                    if gap >= 3:
                        break
        if start is not None and len(names) >= min_run:
            cand = (len(names), c, start, names)
            if best is None or cand[0] > best[0]:
                best = cand
    if best is None:
        return None
    _, c, start, names = best
    return (c, start, names)


def _choose_matrix_anchor(ws) -> Optional[Tuple[int, int, List[str]]]:
    """
    Infer matrix layout:
      - header row: neuron names across columns
      - header col: neuron names down rows
    Returns (anchor_row, anchor_col, names) where:
      - column headers start at (anchor_row, anchor_col+1)
      - row headers start at (anchor_row+1, anchor_col)
      - values start at (anchor_row+1, anchor_col+1)
    """
    max_r = 80
    max_c = 150

    row_info = _scan_header_row(ws, max_r=max_r, max_c=max_c, min_run=20)
    col_info = _scan_header_col(ws, max_r=max_r, max_c=20, min_run=20)

    if row_info is None or col_info is None:
        return None

    header_row, row_start_col, col_names = row_info
    header_col, col_start_row, row_names = col_info

    # Overlap between the two lists should be high if they describe the same matrix
    set_cols = {n.lower() for n in col_names}
    set_rows = {n.lower() for n in row_names}
    overlap = len(set_cols & set_rows)
    denom = min(len(set_cols), len(set_rows))
    if denom == 0:
        return None
    if overlap / denom < 0.6:
        return None

    # Choose an anchor roughly at the corner just before headers:
    # For SI7 files, row headers are typically in the first column of the matrix,
    # and column headers in the first row of the matrix.
    # We use header_row as anchor row, and header_col as anchor col.
    anchor_row = header_row
    anchor_col = header_col

    # Keep names in column-header order, but only those also present in row headers
    names = [n for n in col_names if n.lower() in set_rows]
    if len(names) < 20:
        return None

    return (anchor_row, anchor_col, names)


def read_adjacency_matrix(
    xlsx_path: str,
    sheet_name: str,
    *,
    max_scan: int = 5000
) -> Tuple[List[str], Dict[str, Dict[str, float]]]:
    """
    Read an adjacency matrix from an Excel sheet.

    Supports:
    - Classic layout: neuron names in A2.., values from B2..
    - SI7 layout with title rows/cols: auto-detect anchor.
    """
    if not pylightxl_available():
        raise RuntimeError(pylightxl_error())

    db = _readxl(fn=xlsx_path)
    ws = db.ws(ws=sheet_name)

    # Auto-detect (handles SI7 title/legend offsets)
    anchor = _choose_matrix_anchor(ws)
    if anchor is not None:
        ar, ac, names = anchor
        neurons = names
        matrix: Dict[str, Dict[str, float]] = {}
        for i, src in enumerate(neurons):
            dsts: Dict[str, float] = {}
            for j, dst in enumerate(neurons):
                val = ws.index(row=ar + 1 + i, col=ac + 1 + j)
                if val in (None, ""):
                    continue
                try:
                    w = float(val)
                except (TypeError, ValueError):
                    continue
                if w != 0.0:
                    dsts[dst] = w
            matrix[src] = dsts
        return neurons, matrix

    # Fallback: original assumption (A2 names, B2 values)
    neurons: List[str] = []
    row = 2
    while row < max_scan:
        name = ws.index(row=row, col=1)
        if name is None or name == "":
            break
        neurons.append(str(name).strip())
        row += 1

    if not neurons:
        raise RuntimeError("No neuron names found (auto-detect failed; A2 fallback also empty). [excel_matrix_pylightxl VERSION=' + VERSION + '] ")

    matrix: Dict[str, Dict[str, float]] = {}
    for i, src in enumerate(neurons):
        dsts: Dict[str, float] = {}
        for j, dst in enumerate(neurons):
            val = ws.index(row=i + 2, col=j + 2)
            if val in (None, ""):
                continue
            try:
                w = float(val)
            except (TypeError, ValueError):
                continue
            if w != 0.0:
                dsts[dst] = w
        matrix[src] = dsts

    return neurons, matrix
