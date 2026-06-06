import asyncio
from orchestration.langgraph_workflow import run_workflow

async def debug_test():
    test_cases = [
        ("Tell me about your return policy", "Product Question"),
        ("I was charged twice for my order", "Billing Issue"),
    ]
    
    for input_text, name in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {name}")
        print(f"Input: {input_text}")
        print(f"{'='*60}")
        
        result = await run_workflow(input_text, "TEST_001")
        
        response = result.get("response", "")
        print(f"Response length: {len(response)}")
        print(f"Response type: {type(response)}")
        print(f"Contains 'error': {'error' in response.lower()}")
        print(f"Response preview: {response[:200]}")
        print(f"Full response: {response}")

asyncio.run(debug_test())
