#!/usr/bin/env python3

import re
import sys


def parse_iqtree_log(log_file):
	"""Parse IQ-Tree search log file."""
	log_data = {
		"log_likelihood": None,
		"iterations": None,
		"runtime": None,
		"model": None,
	}
	try:
		with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
			content = f.read()
		m = re.search(r"Log-likelihood of the tree:\s*([\-\d\.]+)", content)
		if m:
			log_data["log_likelihood"] = float(m.group(1))
		m = re.search(r"Total number of iterations:\s*(\d+)", content)
		if m:
			log_data["iterations"] = int(m.group(1))
		m = re.search(r"Total time:\s*([\d\.]+) seconds", content)
		if m:
			log_data["runtime"] = float(m.group(1))
		m = re.search(r"Model of evolution:\s*(.+)", content)
		if m:
			log_data["model"] = m.group(1).strip()
	except Exception as e:
		print(f"Error parsing {log_file}: {e}", file=sys.stderr)
	return log_data


def parse_iqtree_eval_log(log_file):
	"""Parse IQ-Tree evaluation log file."""
	log_data = {
		"log_likelihood": None,
		"runtime": None,
	}
	try:
		with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
			content = f.read()
		m = re.search(r"Log-likelihood:\s*([\-\d\.]+)", content)
		if m:
			log_data["log_likelihood"] = float(m.group(1))
		m = re.search(r"Time:\s*([\d\.]+) seconds", content)
		if m:
			log_data["runtime"] = float(m.group(1))
	except Exception as e:
		print(f"Error parsing evaluation log {log_file}: {e}", file=sys.stderr)
	return log_data


def get_all_iqtree_llhs_from_aggregated(aggregated_log_file):
	"""Extract all log-likelihood values from a concatenated IQ-Tree logs file."""
	llhs = []
	try:
		with open(aggregated_log_file, "r", encoding="utf-8", errors="ignore") as f:
			content = f.read()
		# Match both possible patterns
		for m in re.finditer(r"Log-likelihood:\s*([\-\d\.]+)", content):
			llhs.append(float(m.group(1)))
		for m in re.finditer(r"Log-likelihood of the tree:\s*([\-\d\.]+)", content):
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

#!/usr/bin/env python3
"""
Parse IQ-Tree log files to extract log-likelihood scores and other information.
This script replaces the RAxML-NG log parsing functionality.
"""

import re
import sys
from pathlib import Path

def parse_iqtree_log(log_file):
    """
    Parse IQ-Tree log file to extract:
    - Log-likelihood score
    - Number of iterations
    - Runtime
    - Model parameters
    """
    log_data = {
        'log_likelihood': None,
        'iterations': 0,
        'runtime': None,
        'model': None
    }
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
            
        # Extract log-likelihood (final score)
        llh_match = re.search(r'Log-likelihood of the tree: ([-\d.]+)', content)
        if llh_match:
            log_data['log_likelihood'] = float(llh_match.group(1))
            
        # Extract number of iterations
        iter_match = re.search(r'Total number of iterations: (\d+)', content)
        if iter_match:
            log_data['iterations'] = int(iter_match.group(1))
            
        # Extract runtime
        runtime_match = re.search(r'Total time: ([\d.]+) seconds', content)
        if runtime_match:
            log_data['runtime'] = float(runtime_match.group(1))
            
        # Extract model
        model_match = re.search(r'Model of evolution: (.+)', content)
        if model_match:
            log_data['model'] = model_match.group(1).strip()
            
    except Exception as e:
        print(f"Error parsing {log_file}: {e}", file=sys.stderr)
        
    return log_data

def parse_iqtree_eval_log(log_file):
    """
    Parse IQ-Tree evaluation log file to extract:
    - Log-likelihood score
    - Runtime
    """
    log_data = {
        'log_likelihood': None,
        'runtime': None
    }
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
            
        # Extract log-likelihood from evaluation
        llh_match = re.search(r'Log-likelihood: ([-\d.]+)', content)
        if llh_match:
            log_data['log_likelihood'] = float(llh_match.group(1))
            
        # Extract runtime
        runtime_match = re.search(r'Time: ([\d.]+) seconds', content)
        if runtime_match:
            log_data['runtime'] = float(runtime_match.group(1))
            
    except Exception as e:
        print(f"Error parsing evaluation log {log_file}: {e}", file=sys.stderr)
        
    return log_data

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: parse_iqtree_logs.py <log_file>")
        sys.exit(1)
        
    log_file = sys.argv[1]
    if "eval" in log_file:
        result = parse_iqtree_eval_log(log_file)
    else:
        result = parse_iqtree_log(log_file)
        
    print(f"Log-likelihood: {result['log_likelihood']}")
    print(f"Iterations: {result['iterations']}")
    print(f"Runtime: {result['runtime']}")
    print(f"Model: {result['model']}")