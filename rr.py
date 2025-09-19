import json
import os
import re

def generate_keyword(furniture_type, title):
    """
    Generates a single keyword string from the furniture type and title.
    """
    # Use the furniture type as the primary keyword
    keyword = furniture_type.replace("/", " ").strip()
    
    # If a title exists and is different from the type, add it
    if title and title.lower() not in keyword.lower():
        # Clean the title by removing common phrases like 'model' and '/model'
        clean_title = re.sub(r'(/model|model)', '', title, flags=re.IGNORECASE).strip()
        if clean_title:
            keyword += " " + clean_title
            
    # Normalize the keyword by replacing spaces with underscores and converting to lowercase
    return keyword.replace(" ", "_").lower()

def generate_sql_from_data(file_path, data):
    """
    Generates SQL INSERT queries for furniture items from a single JSON dataset.

    Args:
        file_path (str): The local file path of the JSON file.
        data (dict): The loaded JSON data.

    Returns:
        str: A string containing the SQL INSERT queries.
    """
    sql_statements = []
    main_uid = data.get('uid', 'null_uid')
    file_link = file_path.replace("\\", "/") # Ensure forward slashes

    furniture_items = data.get('furniture', [])

    # The SQL template now only includes the requested fields
    insert_sql_template = "INSERT INTO furniture_data (id, furniture_type, keyword, file_link) VALUES ('{id}', '{furniture_type}', '{keyword}', '{file_link}');"

    for item in furniture_items:
        try:
            furniture_uid = item.get('uid', 'null_uid')
            furniture_type = item.get('type', '').replace("'", "''")
            furniture_title = item.get('title', '').replace("'", "''")

            if furniture_type:
                keyword = generate_keyword(furniture_title, furniture_type)

                insert_sql = insert_sql_template.format(
                    id=furniture_uid.replace("'", "''"),
                    furniture_type=furniture_type,
                    keyword=keyword.replace("'", "''"),
                    file_link=file_link
                )
                sql_statements.append(insert_sql)
        except Exception as e:
            print(f"Error processing item from file {file_link}: {e}")
            continue

    return "\n".join(sql_statements)

def process_folder(folder_path):
    """
    Scans a folder for JSON files, processes each one, and prints the SQL.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: The folder at '{folder_path}' does not exist.")
        return

    # Print the CREATE TABLE statement once at the beginning
    create_table_sql = """
CREATE TABLE IF NOT EXISTS furniture_data (
    id VARCHAR(255) PRIMARY KEY,
    furniture_type VARCHAR(255),
    keyword TEXT,
    file_link VARCHAR(255)
);
"""
    print(create_table_sql)

    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                sql_query = generate_sql_from_data(file_path, data)
                if sql_query:
                    print(sql_query)
            except Exception as e:
                print(f"Error reading or processing file {file_path}: {e}")
                continue

if __name__ == '__main__':
    # >>>>> IMPORTANT: Change this path to the location of your 3D-Front folder <<<<<
    # For example, on Windows: r'C:\Users\YourName\Documents\3D-FRONT'
    # On macOS/Linux: '/Users/YourName/Documents/3D-FRONT'
    folder_path = r'C:\Users\ashvi\OneDrive\Documents\Architect\3D-FRONT' 

    process_folder(folder_path)