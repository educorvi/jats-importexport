from api.services.common import get_adapter_instance


async def list_articles() -> list[str]:
    try:
        adapter_instance = get_adapter_instance()
        return adapter_instance.list_articles()
    except Exception as e:
        # Handle or log the exception as needed
        raise e