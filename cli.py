import os
import csv
import openpyxl
import argparse
import sys
import re

def parse_logs():
    """Parses the honeypot log file into structured data."""
    log_path = "/home/appuser/app/logs/honeypot.log"
    data = []
    
    if not os.path.exists(log_path):
        print(f"Error: Log file not found at {log_path}. Has the honeypot captured any traffic yet?")
        sys.exit(1)

    try:
        with open(log_path, 'r') as f:
            for line in f:
                # Matches: Timestamp - [TYPE] IP: 1.2.3.4 | Details...
                match = re.search(r'(\d{4}-\d{2}-\d{2} [\d:,]+) - \[(.*?)\] (.*)', line)
                if match:
                    timestamp, attack_type, details = match.groups()
                    # Split details by the pipe separator used in honeypot.py
                    detail_parts = [p.strip() for p in details.split('|')]
                    data.append([timestamp, attack_type] + detail_parts)
        return data
    except Exception as e:
        print(f"Error reading logs: {e}")
        sys.exit(1)

def export_csv(data, filename):
    headers = ["Timestamp", "Attack Type", "Client IP", "Path/Target", "Extra Info"]
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)
    print(f"Successfully exported {len(data)} entries to {filename}")

def export_excel(data, filename):
    headers = ["Timestamp", "Attack Type", "Client IP", "Path/Target", "Extra Info"]
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Honeypot Alerts"
    ws.append(headers)
    for row in data:
        ws.append(row)
    wb.save(filename)
    print(f"Successfully exported {len(data)} entries to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visitor Counter Export CLI")
    parser.add_argument(
        "--format", choices=["csv", "excel"], default="csv", 
        help="Format to export (default: csv)"
    )
    parser.add_argument(
        "--output", default="visitor_report", 
        help="Output filename without extension (default: visitor_report)"
    )
    
    args = parser.parse_args()
    log_data = parse_logs()
    
    extension = "xlsx" if args.format == "excel" else "csv"
    filename = f"{args.output}_{extension.replace('xlsx', 'excel')}.{extension}"

    if args.format == "csv":
        export_csv(log_data, filename)
    else:
        export_excel(log_data, filename)