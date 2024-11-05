import pandas as pd
import json

def collapse_genres(j):
    genres = []
    ar = json.loads(j)
    for a in ar:
        genres.append(a.get("name"))
    return " ".join(sorted(genres))

def combine_features(row):
    try:
        return row['overview'] + " " + row["genres_name"]
    except Exception as e:
        print("Error:", e)

def process_tmdb_csv(input_file, output_file):
    """
    Processes a TMDB movies CSV file to create a Vespa-compatible JSON format.
    This function reads a CSV file containing TMDB movie data, processes the data to
    generate new columns for text search, and outputs a JSON file with the necessary
    fields (`put` and `fields`) for indexing documents in Vespa.

    Args:
        input_file (str): The path to the input CSV file containing the TMDB movies data.
                          Expected columns are 'id', 'original_title', 'overview', and 'genres'.
        output_file (str): The path to the output JSON file to save the processed data in
                           Vespa-compatible format.

    Returns:
        None. Writes the processed DataFrame to `output_file` as a JSON file.
    """
    # Read the CSV file into a Pandas DataFrame
    movies = pd.read_csv(input_file)
    
    # Process the 'genres' column
    movies['genres_name'] = movies.apply(lambda x: collapse_genres(x.genres), axis=1)
    
    # Fill missing values in 'original_title', 'overview', and 'genres_name' columns with empty strings
    for f in ['original_title', 'overview', 'genres_name']:
        movies[f] = movies[f].fillna('')
    
    # Create the "text" column by combining specified features
    movies["text"] = movies.apply(combine_features, axis=1)
    
    # Select and rename columns to match required Vespa format
    movies = movies[['id', 'original_title', 'text']]
    movies.rename(columns={'original_title': 'title', 'id': 'doc_id'}, inplace=True)
    
    # Create 'fields' column as a JSON-like structure of each record
    movies['fields'] = movies.apply(lambda row: row.to_dict(), axis=1)
    
    # Create 'put' column based on 'doc_id'
    movies['put'] = movies['doc_id'].apply(lambda x: f"id:hybrid-search:doc::{x}")
    
    # Select only 'put' and 'fields' columns for output
    df_result = movies[['put', 'fields']]
    
    # Output the processed data to a JSON file
    df_result.to_json(output_file, orient='records', lines=True)
    
    # Print sample output for verification
    print(df_result.head())

# File paths
input_file = "tmdb_5000_movies.csv"  # Adjusted path
output_file = "clean_tmdb.jsonl"      # Adjusted path

# Run the function
process_tmdb_csv(input_file, output_file)

