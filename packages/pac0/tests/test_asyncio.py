import asyncio

async def tag_wait(tag: str, sleep: int):
    print(">", tag)
    #await asyncio.sleep(random.uniform(1, 3))
    await asyncio.sleep(sleep)
    print("<", tag)
    return tag


async def test_0010():
    '''async seq'''
    await tag_wait("a", 1)
    await tag_wait("b", 1)
    await tag_wait("c", 1)


async def test_0020():
    '''async gather'''
    await asyncio.gather(*[tag_wait(f"group {i}", 2) for i in range(3)])



async def test_0030():
    """async gather 3 tasks, wait on 2"""
    # Create tasks
    t1 = asyncio.create_task(tag_wait("a", 1))
    t2 = asyncio.create_task(tag_wait("b", 1))
    t3 = asyncio.create_task(tag_wait("c", 10))

    # Wait for first two tasks
    try:
        results = await asyncio.gather(t1, t2, return_exceptions=True)
        print(f"First two results: {results[:2]}")
    finally:
        # Cancel the third task
        t3.cancel()
        try:
            await t3
        except asyncio.CancelledError:
            pass
