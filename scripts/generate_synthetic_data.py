#!/usr/bin/env python3
"""
Generate synthetic test datasets of varying sizes for performance testing.
Creates datasets with realistic value ranges for Tenure, Late_Payments, and Revenue.
"""

import csv
import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_dataset(num_rows: int, output_path: str):
    """
    Generate a synthetic dataset with the required columns.
    
    Args:
        num_rows: Number of records to generate
        output_path: Path to save the CSV file
    """
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Record_ID', 'Tenure', 'Late_Payments', 'Revenue'])
        
        for i in range(1, num_rows + 1):
            record_id = f'R{i:06d}'
            tenure = random.randint(1, 60)  # 1-60 months
            late_payments = random.choices(
                [0, 1, 2, 3, 4, 5, 6, 7, 8],
                weights=[40, 20, 15, 10, 5, 4, 3, 2, 1]  # Weighted toward lower values
            )[0]
            revenue = round(random.uniform(100, 15000), 2)  # $100 - $15,000
            
            writer.writerow([record_id, tenure, late_payments, revenue])
    
    print(f"Generated {num_rows} records -> {output_path}")


def main():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    datasets = [
        (100, 'synthetic_100.csv'),
        (1000, 'synthetic_1000.csv'),
        (10000, 'synthetic_10000.csv'),
    ]
    
    for num_rows, filename in datasets:
        output_path = os.path.join(data_dir, filename)
        generate_dataset(num_rows, output_path)
    
    print("\nAll synthetic datasets generated successfully!")
    print(f"Location: {data_dir}")


if __name__ == '__main__':
    main()
