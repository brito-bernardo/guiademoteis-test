import requests

class ClientOpenAI:

    def __init__(self, api_key:str, api_url:str):
        self._api_key = api_key
        self._api_url = api_url

    def invoke(self, prompt : str):
        # Call OpenAI API
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": prompt}],
            "temperature": 0.7
        }

        response = requests.post(self._api_url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Erro na requisicao: {response.text}")



