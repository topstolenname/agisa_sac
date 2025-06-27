from importlib import import_module

def test_gcp_modules_importable():
    modules = [
        'agisa_sac.gcp.gcs_io',
        'agisa_sac.gcp.bigquery_client',
        'agisa_sac.gcp.vertex_agent'
    ]
    for mod in modules:
        import_module(mod)
