class Client:
    def __init__(self, *args, **kwargs): pass
    def create_product(self, *args, **kwargs): return {"ok": False, "reason": "shim"}
    def get_sales(self, *args, **kwargs): return {"sales": []}
    def ping(self): return "gumroad-shim"
# Optional helper-style functions some libs expect:
def ping(*args, **kwargs): return "gumroad-shim"
