from logic.requets_Methods import HTTPClient

client = HTTPClient()
API_BASE_URL = "http://localhost:3000"

async def login(username, password):
    try:
        response = await client.post(f"{API_BASE_URL}/usuario/login", json={"username": username, "password": password})
        data = response.json()
        return data   # ✅ siempre devuelve diccionario
    except Exception as e:
        return {"message": f"Error: {str(e)}"}


async def send_data(data: dict):
    url = f"{API_BASE_URL}/respuesta/add"
    try:
        response = await client.post(url, json=data)
        if response and response.status_code == 201:
            return response.json()
    except Exception as e:
        return {"message": f"Error: {str(e)}"}


async def fetch_questions():
    url = f"{API_BASE_URL}/pregunta/get"
    try:
        response = await client.get(url)
        if response and response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"message": f"Error: {str(e)}"}
    return None

