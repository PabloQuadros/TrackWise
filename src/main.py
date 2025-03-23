import requests
from src.models.container import Container 

def get_tracking_info(tracking_number):
    url = "https://www.msc.com/api/feature/tools/TrackingInfo"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "x-requested-with": "XMLHttpRequest"
    }
    
    payload = {
        "trackingNumber": tracking_number,
        "trackingMode": "0"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Retorna os dados em formato JSON
    else:
        print(f"Erro {response.status_code}: {response.text}")
        return None

if __name__ == "__main__":
    tracking_number = input("Digite o número do container ou BL: ")
    result = get_tracking_info(tracking_number)
    container = Container.from_api_response(result)
    if result:
        print("Dados do rastreamento:", container )