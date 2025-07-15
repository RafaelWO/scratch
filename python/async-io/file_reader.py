# /// script
# dependencies = [
#   "aiohttp",
#   "numpy",
# ]
# ///

"""
This script is for simulating API requests to the Entity service to fetch RGB images.
Feel free to adjust the code and experiment how much memory the program needs depending on:
 * pre-filled cache
 * empty cache
 * sleeping within the `get_file` coroutine
 * etc.

Please start the file server before running this script!
    $ uv run __development__/file_server.py

To profile the memory, we recommend using Memray (https://bloomberg.github.io/memray/).
It is also useful to dump the logs when running memray to be able to compare the data later.

Usage:
    $ PYTHONPATH=. uv run --no-project --with memray python -m memray run __development__/file_reader.py &> __development__/empty-cache_1000-request.log

---

The script was created to investigate why the `ScanFramePointCloudProvider` needs more memory when the RGB data was already
in the amrax-storage cache compared to when loading it from the entity service.
"""

import asyncio
import contextlib
import datetime
from multiprocessing import context
from aiohttp import ClientSession
import numpy as np
import shelve


cache = {}
fill_cache = False
# sem = asyncio.Semaphore(5)
sem = contextlib.nullcontext()

async def get_file(i, session: ClientSession):
    if i in cache:
        img = cache[i]
        image = np.frombuffer(img).reshape(1000,1000,3)
        image2 = np.array(image)
        return i, image2[::4, ::4]


    async with session.get('http://localhost:8080/file') as resp:
        print(i, resp.status)
        # return counter, await resp.read()
        # await asyncio.sleep(random.randint(1,5))
        # gc.collect()
        binary = await resp.read()
        # cache[i] = binary
        image = np.frombuffer(binary).reshape(1000,1000,3)
        image2 = np.array(image)
        return i, image2[::4, ::4]


async def with_sem(i, session: ClientSession):
    async with sem:
        return await get_file(i, session)


async def main():
    async with ClientSession() as session:
        # for batch in itertools.batched(range(100), 20):
        task_gen = (asyncio.create_task(with_sem(i+1, session)) for i in range(100))

        for fut in asyncio.as_completed(task_gen):
            cnt, img_small = await fut
            # cnt, binary = await fut

            # image = np.frombuffer(binary).reshape(1000,1000,3)
            # img_small = image[::4, ::4]

        # results = await asyncio.gather(*(get_file(session) for _ in range(100)))
        # for cnt, img_small in results:
            with shelve.open("myshelve") as db:
                print(cnt, f"{datetime.datetime.now()}: Writing into shelve")
                db[str(cnt)] = img_small



if __name__ == "__main__":
    if fill_cache:
        for i in range(100):
            with open("__development__/random_image.bytes", "rb") as file:
                cache[i+1] = file.read()

    asyncio.run(main())
