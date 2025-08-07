"""
"""

import time

import functools


def async_debug(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        print('Calling function:', f.__name__)
        result = await f(*args, **kwargs)
        print('Function', f.__name__, 'returned:', result)
        return result
    return wrapper


def async_chrono(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await f(*args, **kwargs)
        end = time.time()
        print(f"Function {f.__name__} took {end - start:.2f} seconds")
        return result
    return wrapper


def async_deco2(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        print("Avant deco2")
        result = await func(*args, **kwargs)
        print("Après deco2")
        return result
    return wrapper


@async_debug
@async_chrono
async def test():
    print("oui")
    await asyncio.sleep(1)


async def main():
    print("Starting main function")
    await test()
    print("Main function finished")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
