#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to create test data files in multiple formats
"""
import pandas as pd
import os

# Create test_data directory if it doesn't exist
os.makedirs('test_data', exist_ok=True)

# Read CSV file
df = pd.read_csv('test_data/sample_employees.csv')

# Save as Excel
df.to_excel('test_data/sample_employees.xlsx', index=False, engine='openpyxl')
print('Created: test_data/sample_employees.xlsx')

# Save as TSV
df.to_csv('test_data/sample_employees.tsv', sep='\t', index=False)
print('Created: test_data/sample_employees.tsv')

# Save as JSON
df.to_json('test_data/sample_employees.json', orient='records', force_ascii=False, indent=2)
print('Created: test_data/sample_employees.json')

print(f'\nTotal rows: {len(df)}')
print(f'Total columns: {len(df.columns)}')
print('Formats: CSV, XLSX, TSV, JSON')
print('All test files created successfully!')

