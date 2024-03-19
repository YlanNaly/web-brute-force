import asyncio
import uuid
import aiohttp
import math
import multiprocessing
import random
import os
import aiofiles

TARGET_URL = "http://127.0.0.1:5000"


async def write_to_file(directory, filename, content):
    async with aiofiles.open(os.path.join(directory, filename), "w") as file:
        await file.write(content)


async def write_successful_response(directory, filename, response_content):
    async with aiofiles.open(os.path.join(directory, filename), "w") as file:
        await file.write(response_content)


def retrieve_file_content(file_path):
    data = None
    with open(file_path, 'r') as file:
        data = file.read()
    return data


async def find_existing_routes(routes, workers_count):
    available_routes = ""
    async with aiohttp.ClientSession() as session:
        for route in routes:
            print("processing... %s/%s" % (TARGET_URL, route))
            async with session.get(f"{TARGET_URL}/{route}") as res:
                if res.status != 404:
                    random_value = random.randint(0, 1000)
                    available_routes += route + "\n"
                    async with session.get(f"{TARGET_URL}/{route}/{random_value}") as path:
                        if path.status != 404:
                            available_routes += f"{route}/:id \n"
                            response_content = await path.text()
                            await write_successful_response("routes_availables", f"{route}_id_response.txt", response_content)
                    for r in routes:
                        async with session.get(f"{TARGET_URL}/{route}?{r}={random_value}") as query:
                            if query.status != 404:
                                available_routes += f"{route}?{r}=? \n"
                                response_content = await query.text()
                                filename = str(uuid.uuid4()) + "_success_response.txt"
                                await write_successful_response("routes_availables", filename, response_content)

    print("proc number: %s" % workers_count)
    filename = str(uuid.uuid4()) + "_success_url.txt"
    directory = "routes_availables"
    if not os.path.exists(directory):
        os.makedirs(directory)
    await write_to_file(directory, filename, available_routes)


async def main():
    random_routes = retrieve_file_content("dir_list.txt").split("\n")
    workers_count = multiprocessing.cpu_count()

    length = len(random_routes)
    quota = math.floor(length / workers_count)
    index_from = 0

    tasks = []
    for i in range(0, workers_count):
        batch = random_routes[index_from:index_from+quota]
        tasks.append(find_existing_routes(batch, workers_count))
        index_from = index_from + quota

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
