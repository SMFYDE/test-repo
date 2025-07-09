import asyncio
import time

from langchain_core.runnables import RunnableConfig, RunnableLambda


async def test_concurrency():
    # Track currently running tasks
    running_tasks = 0
    max_running_tasks = 0
    lock = asyncio.Lock()

    async def tracked_function(x):
        nonlocal running_tasks, max_running_tasks
        async with lock:
            running_tasks += 1
            max_running_tasks = max(max_running_tasks, running_tasks)
            print(f"Starting task. Current running: {running_tasks}")

        # Simulate some work
        await asyncio.sleep(1)

        async with lock:
            running_tasks -= 1
            print(f"Finishing task. Current running: {running_tasks}")

        return f"Completed {x}"

    # Create runnable
    runnable = RunnableLambda(tracked_function)

    # Test parameters
    num_tasks = 10
    max_concurrency = 3

    # Test abatch_as_completed
    print(f"\nTesting abatch_as_completed with max_concurrency={max_concurrency}...")
    start_time = time.time()
    config = RunnableConfig(max_concurrency=max_concurrency)
    results = []

    async for idx, result in runnable.abatch_as_completed(
        range(num_tasks), config=config
    ):
        print(f"Got result {idx}: {result}")
        results.append(result)

    end_time = time.time()

    print("\nResults for abatch_as_completed:")
    print(f"Max concurrent tasks observed: {max_running_tasks}")
    print(f"Expected max concurrent tasks: {max_concurrency}")
    print(f"Total time: {end_time - start_time:.2f} seconds")
    print(f"Number of results: {len(results)}")

    # Reset counters
    running_tasks = 0
    max_running_tasks = 0

    # Test abatch
    print(f"\nTesting abatch with max_concurrency={max_concurrency}...")
    start_time = time.time()
    results = await runnable.abatch(range(num_tasks), config=config)
    end_time = time.time()

    print("\nResults for abatch:")
    print(f"Max concurrent tasks observed: {max_running_tasks}")
    print(f"Expected max concurrent tasks: {max_concurrency}")
    print(f"Total time: {end_time - start_time:.2f} seconds")
    print(f"Number of results: {len(results)}")


# Run the test
if __name__ == "__main__":
    asyncio.run(test_concurrency())