import importlib
SOURCE_DEPENDENCIES = {'modules': ['dependency'], 'files': ['resource.json']}
def inspect(request):
    return importlib.import_module(request['module']).VALUE
