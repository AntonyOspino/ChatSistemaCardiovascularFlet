import httpx

class HTTPClient:
    @staticmethod
    async def get(url: str, params: dict = None):
        """Realiza una petición GET asíncrona"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10)
                return response
        except Exception as e:
            print(f"Error en GET: {e}")
            return None

    @staticmethod
    async def post(url: str, data: dict = None, json: dict = None):
        """Realiza una petición POST asíncrona"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data, json=json, timeout=10)
                return response
        except Exception as e:
            print(f"Error en POST: {e}")
            return None