"""
"""

import time
import random
import asyncio

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class ProcessedState(TypedDict):
    file_name: str
    cooking_time: int


class BlueAxelGraph:
    def __init__(
        self
    ) -> None:
        self.workflow = None
        self.app = None

    def build_graph(
        self
    ) -> None:
        self.workflow = StateGraph(ProcessedState)

        self.workflow.add_node("preprocessing", self._preprocessing)
        self.workflow.add_node("classification", self._classification)
        self.workflow.add_node("finalize", self._finalize)

        self.workflow.add_edge(START, "preprocessing")
        self.workflow.add_edge("preprocessing", "classification")
        self.workflow.add_edge("classification", "finalize")
        self.workflow.add_edge("finalize", END)

        self.app = self.workflow.compile()

    async def _preprocessing(
        self,
        state: ProcessedState
    ) -> ProcessedState:

        print(f'_preprocessing: {state["file_name"]}')

        await asyncio.sleep(state['cooking_time'])

        return state

    async def _classification(
        self,
        state: ProcessedState
    ) -> ProcessedState:
        print(f'_classification: {state["file_name"]}')
        await asyncio.sleep(0.5)
        return state

    async def _finalize(
        self,
        state: ProcessedState
    ) -> ProcessedState:
        print(f'_finalize: {state["file_name"]}')

        print(f'Result for file {state["file_name"]} is ready. {state["cooking_time"] + 0.5} seconds elapsed.')
        return state


state_graph = BlueAxelGraph()
state_graph.build_graph()

initial_state = [
    ProcessedState(
        file_name=f"file_{i}.txt",
        cooking_time=(i + 5) * random.uniform(0.5, 1.5),
    )
    for i in range(5)
]

print("Initial states:")
for state in initial_state:
    print(f"  {state['file_name']} | {state['cooking_time']:.2f} seconds")
print()


async def run(initial_state) -> None:
    start = time.time()

    async def run_one(state):
        g = BlueAxelGraph()
        g.build_graph()
        return await g.app.ainvoke(state)

    for state in initial_state:
        await run_one(state)

    print(f"------> run: {time.time() - start:.2f} seconds.")


async def arun(initial_state) -> None:
    start = time.time()

    async def run_one(state):
        g = BlueAxelGraph()
        g.build_graph()
        return await g.app.ainvoke(state)

    await asyncio.gather(*[run_one(state) for state in initial_state])
    print(f"------> arun: {time.time() - start:.2f} seconds.")


async def abatch(initial_state) -> None:
    start = time.time()

    await state_graph.app.abatch(initial_state)

    print(f"------> abatch: {time.time() - start:.2f} seconds.")


async def thread(initial_state) -> None:
    start = time.time()

    async with asyncio.Semaphore(2):
        await asyncio.gather(
            *[state_graph.app.ainvoke(state) for state in initial_state]
        )

    print(f"------> thread: {time.time() - start:.2f} seconds.")

if __name__ == "__main__":
    # Ca c'est sur c'est un par un donc c'est beaucoup plus long
    # asyncio.run(run(initial_state))
    # print()
    # print()
    asyncio.run(arun(initial_state))
    print()
    print()
    asyncio.run(abatch(initial_state))
    print()
    print()
    asyncio.run(thread(initial_state))
