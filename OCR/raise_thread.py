import asyncio


async def raise_thread(n, raise_exception=False):
    await asyncio.sleep(n)
    if raise_exception:
        raise ValueError("An error occurred")
    return f"Thread {n} completed successfully"


async def main():
    my_list = []

    try:
        coro = [raise_thread(i, raise_exception=False) for i in range(5)]
        my_list.extend(await asyncio.gather(*coro))
    except ValueError as e:
        print(f"Caught an exception: {e}")

    for l in my_list:
        print(l)

if __name__ == "__main__":
    asyncio.run(main())
