# test_vespa_connection.py

from vespa.application import Vespa

# Replace with your Vespa instance URL and port
app = Vespa(url="http://localhost", port=19071)

# Simple test query
test_query = {
    "yql": "select * from sources * limit 5"
}

try:
    response = app.query(test_query)
    print("Test query response:", response)
except Exception as e:
    print("Error during query:", e)

