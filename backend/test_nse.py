import asyncio
from services.nse_service import nse

async def test():
    try:
        data = await nse.get_all_indices()
        if data and "data" in data:
            print(f"SUCCESS: {len(data['data'])} indices")
        else:
            print("FAILURE: No data")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await nse.close()

if __name__ == "__main__":
    asyncio.run(test())
