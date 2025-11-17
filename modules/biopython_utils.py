"""
Helpers for simple protein/sequence tasks using Biopython.
Provides safe imports so tests and environments without Biopython still work.
"""
from typing import List, Tuple, Optional


def _safe_import_biopython():
    try:
        from Bio import SeqIO
        from Bio.SeqUtils import molecular_weight
        return SeqIO, molecular_weight
    except Exception:
        return None, None


def parse_fasta_string(fasta_str: str) -> List[Tuple[str, str]]:
    """Parse a FASTA-formatted string and return list of (id, seq).
    Falls back to a simple parser if Biopython is not installed.
    """
    SeqIO, _ = _safe_import_biopython()
    if SeqIO is not None:
        from io import StringIO
        records = list(SeqIO.parse(StringIO(fasta_str), "fasta"))
        return [(r.id, str(r.seq)) for r in records]

    # Simple fallback parser
    entries = []
    cur_id = None
    cur_seq = []
    for line in fasta_str.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if cur_id is not None:
                entries.append((cur_id, "".join(cur_seq)))
            cur_id = line[1:]
            cur_seq = []
        else:
            cur_seq.append(line)
    if cur_id is not None:
        entries.append((cur_id, "".join(cur_seq)))
    return entries


def estimate_molecular_weight(seq: str) -> Optional[float]:
    """Estimate molecular weight using Biopython if available, otherwise return None."""
    _, molecular_weight = _safe_import_biopython()
    if molecular_weight is None:
        return None
    return molecular_weight(seq, "protein")
