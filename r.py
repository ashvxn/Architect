import json
import os

def is_bed_by_dimensions(size):
    """
    Heuristic to determine if an object is a bed based on its dimensions.
    Assumes size is a list [x, y, z].
    """
    if not size or len(size) < 3:
        return False
    
    # Sort dimensions to get length, width, and height regardless of order
    dims = sorted(size)
    height, width, length = dims[0], dims[1], dims[2]

    # Typical dimensions for a bed in meters (approximate)
    min_length = 1.8
    min_width = 0.8
    max_height = 1.2

    # Check against the heuristic
    if length > min_length and width > min_width and height < max_height:
        return True
    
    return False

def generate_sql_from_data(datasets):
    """
    Generates SQL to create a table and insert data from a list of 3D front datasets.

    Args:
        datasets (list): A list of dictionaries, where each dictionary represents a JSON dataset
                         and its corresponding local file path.

    Returns:
        str: A string containing the complete SQL query.
    """
    sql_statements = []

    # SQL CREATE TABLE statement
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS threed_front_datasets (
        id VARCHAR(255) PRIMARY KEY,
        file_link VARCHAR(255),
        furniture_uid VARCHAR(255),
        furniture_title TEXT,
        furniture_type VARCHAR(255),
        size_x FLOAT,
        size_y FLOAT,
        size_z FLOAT,
        bbox TEXT,
        source_category_id VARCHAR(255),
        price FLOAT,
        style TEXT,
        color TEXT
    );
    """
    sql_statements.append(create_table_sql)

    # SQL INSERT statements
    insert_sql_template = """
    INSERT INTO threed_front_datasets (
        id, file_link, furniture_uid, furniture_title, furniture_type,
        size_x, size_y, size_z, bbox, source_category_id, price, style, color
    ) VALUES (
        '{id}', '{file_link}', '{furniture_uid}', '{furniture_title}', '{furniture_type}',
        {size_x}, {size_y}, {size_z}, '{bbox}', '{source_category_id}', {price}, '{style}', '{color}'
    );
    """

    for file_path, data in datasets:
        main_uid = data.get('uid', 'null_uid')
        
        # Use the local file path directly
        file_link = file_path.replace("\\", "/") # Ensure forward slashes for cross-platform compatibility
        
        furniture_items = data.get('furniture', [])

        for item in furniture_items:
            # Check for "bed" keyword OR use the dimensional heuristic
            is_bed = "bed" in item.get('title', '').lower() or is_bed_by_dimensions(item.get('size'))
            
            if is_bed:
                try:
                    # Extract attributes directly from the JSON model
                    furniture_uid = item.get('uid', 'null_uid').replace("'", "''")
                    furniture_title = item.get('title', '').replace("'", "''")
                    furniture_type = item.get('type', '').replace("'", "''")
                    source_category_id = item.get('sourceCategoryId', '').replace("'", "''")

                    # Handle keypoints: size and bounding box
                    size = item.get('size')
                    size_x = size[0] if size and len(size) > 0 else 'NULL'
                    size_y = size[1] if size and len(size) > 1 else 'NULL'
                    size_z = size[2] if size and len(size) > 2 else 'NULL'

                    # Properly escape the bbox JSON string for SQL
                    bbox_data = item.get('bbox', '[]')
                    bbox = str(bbox_data).replace("'", "''")

                    # Extract the new attributes from the model itself
                    price = item.get('price', 'NULL')
                    style = item.get('style', 'N/A').replace("'", "''")
                    color = item.get('color', 'N/A').replace("'", "''")

                    # Combine everything into an INSERT statement
                    insert_sql = insert_sql_template.format(
                        id=main_uid,
                        file_link=file_link,
                        furniture_uid=furniture_uid,
                        furniture_title=furniture_title,
                        furniture_type=furniture_type,
                        size_x=size_x,
                        size_y=size_y,
                        size_z=size_z,
                        bbox=bbox,
                        source_category_id=source_category_id,
                        price=price,
                        style=style,
                        color=color
                    ).strip()

                    sql_statements.append(insert_sql)
                except Exception as e:
                    print(f"Error processing item {furniture_uid} from file {file_link}: {e}")
                    continue

    return "\n\n".join(sql_statements)

def scan_files_for_beds(folder_path):
    """
    Scans a folder for files containing "bed" models and returns their data
    along with the local file path.
    """
    bed_datasets = []
    
    # Check if the folder path is valid
    if not os.path.isdir(folder_path):
        print(f"Error: The folder at '{folder_path}' does not exist.")
        return []

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    furniture_items = data.get('furniture', [])

                    # Use either title or dimensional heuristic to find a bed
                    if any("bed" in item.get('title', '').lower() or is_bed_by_dimensions(item.get('size')) for item in furniture_items):
                        bed_datasets.append((file_path, data))
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue
    return bed_datasets

if __name__ == '__main__':
    # You must provide the path to your folder containing the JSON models here.
    # Example:
    # folder_path = 'C:/Users/YourName/Documents/3d_models/'
    folder_path = r'C:\Users\ashvi\OneDrive\Documents\Architect\3D-FRONT'  # This is a placeholder

    # Create a mock folder and files for demonstration purposes in this environment
    os.makedirs(folder_path, exist_ok=True)
    mock_datasets = {
        "ffd7218c-06dc-4550-96ab-72705ec4f3aa.json": {"uid": "ffd7218c-06dc-4550-96ab-72705ec4f3aa", "furniture": [{"uid": "53138/model", "title": "kitchen cabinet/cbnt door", "type": "standard"}]},
        "ffb71fcf-a89a-4e88-a1f6-84033d3b2e13.json": {"uid": "ffb71fcf-a89a-4e88-a1f6-84033d3b2e13", "furniture": [{"uid": "56080/model", "title": "bed/single bed", "type": "standard", "size": [1.25, 1.88, 0.96], "sourceCategoryId": "8f58f84c-1424-4aaf-aef5-62ae1da722ab", "bbox": [1.25, 1.88, 0.96]}]},
        "ffbb5785-e27f-47f4-a4b9-479d74d4815f.json": {"uid": "ffbb5785-e27f-47f4-a4b9-479d74d4815f", "furniture": [{"uid": "145407/model1", "title": "bed/queen bed", "type": "standard", "size": [1.51, 2.28, 2.2], "price": 850.00, "style": "Contemporary", "color": "White"}]}
    }
    for filename, data in mock_datasets.items():
        with open(os.path.join(folder_path, filename), 'w') as f:
            json.dump(data, f)

    # Step 1: Scan the folder for "bed" files
    bed_datasets = scan_files_for_beds(folder_path)
    
    # Step 2: Generate the SQL query from the filtered datasets
    sql_query = generate_sql_from_data(bed_datasets)
    print(sql_query)
