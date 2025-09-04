from config import API_VERSION

@app.get(f"/api/{API_VERSION}/dns")
def get_dns():
    ...
