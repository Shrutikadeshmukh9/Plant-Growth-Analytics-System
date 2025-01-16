# Generates data from a json file into a sql batch script splitting every 1000 records
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any

def create_batch_inserts(data: List[Dict[str, Any]], table_name: str, batch_size: int = 1000) -> str:
    """
    Convert JSON data into PostgreSQL batch INSERT statements.
    
    Args:
        data: List of dictionaries containing the data
        table_name: Name of the target table
        batch_size: Number of records per batch insert
    
    Returns:
        String containing SQL batch insert statements
    """
    if not data:
        return ""

    # Get columns from the first record
    columns = list(data[0].keys())
    
    # Start building SQL
    sql_parts = []
    
    # Process data in batches
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        values_strings = []
        
        for record in batch:
            # Format each value based on its type
            formatted_values = []
            for col in columns:
                value = record.get(col)
                if value is None:
                    formatted_values.append('NULL')
                elif isinstance(value, (int, float)):
                    formatted_values.append(str(value))
                elif isinstance(value, bool):
                    formatted_values.append('true' if value else 'false')
                elif isinstance(value, (datetime, str)):
                    formatted_values.append(f"'{str(value)}'")
                else:
                    formatted_values.append(f"'{str(value)}'")
            
            values_strings.append(f"({', '.join(formatted_values)})")
        
        # Create the batch insert statement using normal string join
        insert_statement = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES {','.join(values_strings)};"
        sql_parts.append(insert_statement)
    
    return "\n".join(sql_parts)

def main():
    parser = argparse.ArgumentParser(description='Convert JSON data to PostgreSQL batch inserts')
    parser.add_argument('input_file', help='Input JSON file path')
    parser.add_argument('table_name', help='Target table name')
    parser.add_argument('--output', help='Output SQL file path (optional)')
    parser.add_argument('--batch-size', type=int, default=1000, help='Number of records per batch (default: 1000)')
    
    args = parser.parse_args()
    
    # Read JSON data
    with open(args.input_file, 'r') as f:
        data = json.load(f)
    
    # Generate SQL
    sql = create_batch_inserts(data, args.table_name, args.batch_size)
    
    # Write or print output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(sql)
        print(f"SQL written to {args.output}")
    else:
        print(sql)

if __name__ == '__main__':
    main()