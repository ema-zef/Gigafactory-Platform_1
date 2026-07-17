
# ----------------------------------
# Fuseki test
# ----------------------------------

@router.get("/fuseki-test")
def fuseki_test():

    return fuseki_test_connection()
    
