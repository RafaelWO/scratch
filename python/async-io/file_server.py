# /// script
# dependencies = [
#   "aiohttp",
#   "numpy",
# ]
# ///

"""
This script runs a web server that return a random numpy array (RGB image).

Usage:
    $ uv run file_server.py

After that, you can run the `file_reader.py` script (see corresponding docstring in file).
"""

import logging
import numpy as np
from aiohttp import web

async def file(request):
    image = np.random.rand(1000,1000,3)
    return web.Response(body=image.tobytes())

logging.basicConfig(level=logging.DEBUG)
app = web.Application()
app.add_routes([web.get('/file', file)])
web.run_app(app)
