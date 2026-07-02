import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# The preview sandbox denies os.getcwd(), so the served directory must be
# passed explicitly instead of running `python3 -m http.server`.
DIRECTORY = "/Users/uuto/Downloads/test/new-folder"

handler = functools.partial(SimpleHTTPRequestHandler, directory=DIRECTORY)
ThreadingHTTPServer(("127.0.0.1", 4173), handler).serve_forever()
