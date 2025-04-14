import requests


class MscService:

    def get_tracking_info(self, tracking_number):
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
        
    def validate_container_existence(self, container_number):
        response = self.get_tracking_info(container_number)
        return response

def get_msc_service():
    return MscService()
