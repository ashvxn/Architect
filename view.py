import mysql.connector
import os
import trimesh
import re

def search_and_render_model(db_config, models_folder, keyword):
    """
    Searches the MySQL database for a keyword and renders the top matching model.
    """
    # Normalize the keyword for matching against the database
    normalized_keyword = keyword.lower().replace(" ", "_")

    conn = None
    try:
        # Establish connection to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Search for a matching keyword in the database
        query = "SELECT file_link, id FROM furniture_data WHERE keyword LIKE %s LIMIT 1;"
        
        # Use a wildcard search to find partial matches
        cursor.execute(query, (f'%{normalized_keyword}%',))
        
        result = cursor.fetchone()

        if result:
            file_link, model_uid = result
            
            # The original uid format "145407/model" means the file is in a folder named "145407"
            # and the file is named "model.obj"
            model_dir = os.path.join(models_folder, model_uid.split('/')[0])
            
            # We will search for common 3D model file extensions
            model_found = False
            full_model_path = ""
            for ext in ['.obj', '.dae', '.gltf', '.stl', '.ply']:
                # The file name can be either the part after the last slash or a standardized 'model' name.
                file_name_part = model_uid.split('/')[-1]
                
                # First, try the explicit name from the UID
                candidate_path_1 = os.path.join(model_dir, file_name_part + ext)
                if os.path.exists(candidate_path_1):
                    full_model_path = candidate_path_1
                    model_found = True
                    break
                
                # If that fails, try the common 'model' name
                candidate_path_2 = os.path.join(model_dir, 'model' + ext)
                if os.path.exists(candidate_path_2):
                    full_model_path = candidate_path_2
                    model_found = True
                    break

            if not model_found:
                print(f"Error: 3D model file not found in directory {model_dir}")
                return

            print(f"Found match: {model_uid} in {file_link}")
            print(f"Attempting to render model from: {full_model_path}")
            
            # Load the model using trimesh
            mesh = trimesh.load(full_model_path)
            
            # Show the model. This will open a new window.
            # Requires pyglet or PyVista to be installed
            mesh.show()
            
        else:
            print(f"No models found for keyword: '{keyword}'")

    except mysql.connector.Error as e:
        print(f"MySQL error: {e}")
    except trimesh.exceptions.FileTypeError as e:
        print(f"Error loading model: {e}")
        print("Please ensure the model file is a supported format (e.g., .obj, .stl).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    # >>>>> IMPORTANT: CONFIGURE THESE DATABASE SETTINGS <<<<<
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'ashvin2004',
        'database': 'threed_data'
    }
    
    # >>>>> IMPORTANT: CONFIGURE THIS PATH <<<<<
    # Path to your main 3D-Front models folder
    MODELS_FOLDER_PATH = r'C:\Users\ashvi\OneDrive\Documents\Architect\3D-FRONT' 

    try:
        # Check if we can connect to the database before proceeding
        conn = mysql.connector.connect(**DB_CONFIG)
        conn.close()

        user_keyword = input("Enter a keyword to search for (e.g., 'queen bed' or 'armchair'): ")
        search_and_render_model(DB_CONFIG, MODELS_FOLDER_PATH, user_keyword)

    except mysql.connector.Error as e:
        print(f"Error: Could not connect to the MySQL database.")
        print(f"Please check your DB_CONFIG settings and ensure the MySQL server is running.")
        print(f"MySQL error: {e}")
