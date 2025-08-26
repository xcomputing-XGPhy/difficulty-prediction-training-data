#!/usr/bin/env python3
import re
import sys

_HMS_RE = re.compile(r"(?:(\d+)h:)?(?:(\d+)m:)?(?:(\d+)s)")

def _hms_to_seconds(h, m, s):
    return (int(h or 0) * 3600) + (int(m or 0) * 60) + int(s or 0)

def _get_wallclock_seconds_from_text(text):
    m = re.search(r"^Total wall-clock time used:\s*([0-9]*\.?[0-9]+)\s*sec", text, flags=re.M)
    if m:
        return float(m.group(1))
    m = re.search(r"/\s*Time:\s*([0-9hms:]+)", text)
    if m:
        hh, mm, ss = _HMS_RE.search(m.group(1)).groups()
        return float(_hms_to_seconds(hh, mm, ss))
    m = re.search(r"^Wall-clock time used for tree search:\s*([0-9]*\.?[0-9]+)\s*sec", text, flags=re.M)
    if m:
        return float(m.group(1))
    return None

def _extract_model(text):
    m = re.search(r"^Model of evolution:\s*(.+)$", text, flags=re.M)
    if m:
        return m.group(1).strip()
    m = re.search(r"^Best-fit model:\s*(.+)$", text, flags=re.M)
    if m:
        return m.group(1).strip()
    m = re.search(r"^Command:\s*(.+)$", text, flags=re.M)
    if m:
        cmd = m.group(1)
        m2 = re.search(r"\s-m\s+(\S+)", cmd)
        if m2:
            return m2.group(1).strip()
    return None

def _extract_iterations(text):
    m = re.search(r"^Total number of iterations:\s*(\d+)", text, flags=re.M)
    if m:
        return int(m.group(1))
    m = re.search(r"TREE SEARCH COMPLETED AFTER\s+(\d+)\s+ITERATIONS", text)
    if m:
        return int(m.group(1))
    m = re.search(r"^Number of iterations:\s*(\d+)", text, flags=re.M)
    if m:
        return int(m.group(1))
    return None

def _extract_final_llh(text):
    for pat in [
        r"^Optimal log-likelihood:\s*([\-0-9.]+)",
        r"^BEST SCORE FOUND\s*:\s*([\-0-9.]+)",
        r"^Log-likelihood of the tree:\s*([\-0-9.]+)",
        r"^Log-likelihood:\s*([\-0-9.]+)",
    ]:
        m = re.search(pat, text, flags=re.M)
        if m:
            return float(m.group(1))
    return None

def parse_iqtree_log(log_file):
    data = {"log_likelihood": None, "iterations": None, "runtime": None, "model": None}
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        data["log_likelihood"] = _extract_final_llh(txt)
        data["iterations"] = _extract_iterations(txt)
        data["runtime"] = _get_wallclock_seconds_from_text(txt)
        data["model"] = _extract_model(txt)
    except Exception as e:
        print(f"Error parsing {log_file}: {e}", file=sys.stderr)
    return data

def parse_iqtree_eval_log(log_file):
    data = {"log_likelihood": None, "runtime": None}
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        data["log_likelihood"] = _extract_final_llh(txt)
        data["runtime"] = _get_wallclock_seconds_from_text(txt)
    except Exception as e:
        print(f"Error parsing evaluation log {log_file}: {e}", file=sys.stderr)
    return data

def get_all_iqtree_llhs_from_aggregated(aggregated_log_file):
    llhs = []
    try:
        with open(aggregated_log_file, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        for pat in [
            r"^Optimal log-likelihood:\s*([\-0-9.]+)",
            r"^BEST SCORE FOUND\s*:\s*([\-0-9.]+)",
            r"^Log-likelihood of the tree:\s*([\-0-9.]+)",
            r"^Log-likelihood:\s*([\-0-9.]+)",
        ]:
            for m in re.finditer(pat, txt, flags=re.M):
                llhs.append(float(m.group(1)))
    except Exception as e:
        print(f"Error parsing aggregated IQ-Tree logs {aggregated_log_file}: {e}", file=sys.stderr)
    return llhs

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: parse_iqtree_logs.py <log_file>")
        sys.exit(1)
    log_file = sys.argv[1]
    if "eval" in log_file:
        res = parse_iqtree_eval_log(log_file)
    else:
        res = parse_iqtree_log(log_file)
    print(res)
