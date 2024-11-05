import pandas as pd
from vespa.application import Vespa
from vespa.io import VespaResponse, VespaQueryResponse

def display_hits_as_df(response: VespaQueryResponse, fields) -> pd.DataFrame:
    records = []
    for hit in response.hits:
        record = {field: hit["fields"].get(field) for field in fields}
        records.append(record)
    return pd.DataFrame(records)

def keyword_search(app, search_query):
    query = {
        "yql": "select * from sources * where userQuery() limit 5",
        "query": search_query,
        "ranking": "bm25",
    }
    response = app.query(query)
    return display_hits_as_df(response, ["doc_id", "title"])

def semantic_search(app, search_query):
    query = {
        "yql": "select * from sources * where ({targetHits:100} nearestNeighbor(embedding, e)) limit 5",
        "query": search_query,
        "ranking": "semantic",
        "input.query(e)": "embed(@query)"
    }
    response = app.query(query)
    return display_hits_as_df(response, ["doc_id", "title"])

def get_embedding(app, doc_id):
    query = {
        "yql": f"select doc_id, title, text, embedding from content.doc where doc_id contains '{doc_id}'",
        "hits": 1
    }
    result = app.query(query)
    
    if result.hits:
        return result.hits[0]
    return None

def query_movies_by_embedding(app, embedding_vector):
    query = {
        'hits': 5,
        'yql': 'select * from content.doc where ({targetHits:5} nearestNeighbor(embedding, user_embedding))',
        'ranking.features.query(user_embedding)': str(embedding_vector),
        'ranking.profile': 'recommendation'
    }
    return app.query(query)

# Replace with the host and port of your local Vespa instance
app = Vespa(url="http://localhost", port=8082)  # Changed port to 8082

# Define the search query
query = "Harry Potter and the Half-Blood Prince"

# Perform keyword search
df_keyword = keyword_search(app, query)
print("Keyword Search Results:")
print(df_keyword.head())

# Perform semantic search
df_semantic = semantic_search(app, query)
print("\nSemantic Search Results:")
print(df_semantic.head())

# Get embedding for a specific document ID (replace "767" with an appropriate ID)
emb = get_embedding(app, "767")  # Added app parameter to the function call
if emb:
    results = query_movies_by_embedding(app, emb["fields"]["embedding"])  # Added app parameter to the function call
    df_recommendations = display_hits_as_df(results, ["doc_id", "title", "text"])
    print("\nRecommendation Search Results:")
    print(df_recommendations.head())
else:
    print("\nNo embedding found for the specified document ID.")
