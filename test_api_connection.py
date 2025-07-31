import requests

api_url = "https://landing-teste.supercacheta.com/supercacheta/sign-up?domain=cadastro.supercacheta.com"

try:
    response = requests.get(api_url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content: {response.text[:500]}") # Print first 500 chars of content
except requests.exceptions.RequestException as e:
    print(f"Erro de conexão: {e}")


