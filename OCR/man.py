from langgraph_sdk import get_client
client = get_client(url=<DEPLOYMENT_URL>, api_key=<API_KEY>)

# Using the graph deployed with the name "agent"
assistant_id = "agent"

# create a thread
thread = await client.threads.create()
thread_id = thread["thread_id"]

# create a streaming run
async for chunk in client.runs.stream(
    thread_id,
    assistant_id,
    input=inputs,
    stream_mode="updates"
):
    print(chunk.data)