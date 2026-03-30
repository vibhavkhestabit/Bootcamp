import csv
import random
import os
from collections import defaultdict

def run_processor():
    # 1. Configuration
    NUM_ROWS = 20
    CSV_FILE = 'user.csv'
    TXT_FILE = 'inference.txt'
    REGIONS = ['North', 'South', 'East', 'West']

    # 2. Data Generation
    try:
        data = [{'user': f'User_{i}', 'region': random.choice(REGIONS), 'salary': random.randint(40000, 120000)} for i in range(1, NUM_ROWS + 1)]
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['user', 'region', 'salary'])
            writer.writeheader()
            writer.writerows(data)
    except (IOError, PermissionError) as e:
        print(f"Write error: {e}")
        return

    # 3. Data Analysis
    stats = defaultdict(lambda: {'total_salary': 0, 'count': 0})
    try:
        with open(CSV_FILE, mode='r') as f:
            reader = list(csv.DictReader(f))
            
            # Row count verification (20 data rows, excluding header)
            assert len(reader) == NUM_ROWS, f"Data mismatch: Expected {NUM_ROWS}, got {len(reader)}"
            
            # Dynamic Region extraction
            regions_found = {row['region'] for row in reader}
            
            for row in reader:
                reg = row['region']
                stats[reg]['total_salary'] += float(row['salary'])
                stats[reg]['count'] += 1

        # 4. Reporting Phase
        with open(TXT_FILE, 'w') as out:
            for reg in sorted(regions_found):
                avg = stats[reg]['total_salary'] / stats[reg]['count'] if stats[reg]['count'] > 0 else 0
                out.write(f"Region: {reg}, Average Salary: {avg:.2f}\n")

    except (IOError, PermissionError) as e:
        print(f"Analysis/Write error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # 5. Persistence Assertion
    if os.path.exists(CSV_FILE) and os.path.exists(TXT_FILE):
        with open(CSV_FILE, 'r') as f:
            total_lines = sum(1 for _ in f)
        print(f"Verification Success: {CSV_FILE} found ({total_lines} total lines), {TXT_FILE} created.")

if __name__ == "__main__":
    run_processor()
