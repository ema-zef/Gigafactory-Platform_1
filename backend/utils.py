
# ----------------------------------
# Fuseki test
# ----------------------------------

def fuseki_test_connection():
query = """
    SELECT ?s ?p ?o
    WHERE {
        ?s ?p ?o
    }
    LIMIT 10
    """

    try:

        response = requests.post(
            "https://gigafactory-fuseki.onrender.com/gigafactory/query",
            data={"query": query},
            headers={
                "Accept": "application/sparql-results+json"
            },
            timeout=30
        )