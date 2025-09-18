from typing import Optional, Dict, Any
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
    
async def send_data_progress(data: dict):
    url = f"{API_BASE_URL}/respuesta/addProgress"
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

async def send_data_fetch(data: dict):
    url = f"{API_BASE_URL}/respuesta/addWithoutSaving"
    try:
        response = await client.post(url, json=data)
        if response and response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"message": f"Error: {str(e)}"}


async def fetch_historial_data(identificacion: Optional[int] = None, last: Optional[bool] = None) -> Dict[str, Any]:
    url = f"http://localhost:3000/historial/get"
    
    # Construir parámetros según si hay identificación o no
    params = {}
    if identificacion:
        params["identificacion"] = identificacion
    if last:
        params["last"] = "last"
    try:
        # Usar la clase HTTPClient en lugar de client directamente
        response = await HTTPClient.get(url, params=params)
        
        if response and response.status_code == 200:
            return response.json()
        else:
            return {
                "message": f"Error en la petición: {response.status_code if response else 'No response'}"
            }
            
    except Exception as e:
        return {"message": f"Error: {str(e)}"}
    

async def fetch_pacients_progress(identificacion: int, progreso: bool = True, last: Optional[bool] = None) -> Dict[str, Any]:
    base_url = "http://localhost:3000/historial/get"
    if progreso:
        url = f"{base_url}/{identificacion}/progreso"
    elif last and progreso:
        url = f"{base_url}/{identificacion}/progreso/last"
    else:
        url = f"{base_url}/{identificacion}"
    try:
        response = await HTTPClient.get(url)
        if response and response.status_code == 200:
            return response.json()
        else:
            return {
                "message": f"Error en la petición: {response.status_code if response else 'No response'}"
            }
    except Exception as e:
        return {"message": f"Error: {str(e)}"}