import requests
import json

api_url = "https://landing-teste.supercacheta.com/supercacheta/sign-up?domain=cadastro.supercacheta.com"

payload = {
    "nome": "Teste",
    "sobrenome": "",
    "username": "teste_user",
    "cpf": "12345678900",
    "email": "teste@example.com",
    "telefone": "11999999999",
    "genero_id": 0,
    "publicidades": 1,
    "data_nascimento": "",
    "senha": "Senha123",
    "action_recaptcha": "REGISTER",
    "latitude": 0,
    "longitude": 0,
    "os": "Linux x86_64",
    "platform": "Brazil",
    "afiliado_id": 1
}

try:
    response = requests.post(api_url, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    try:
        print(f"JSON Response: {json.dumps(response.json(), indent=2)}")
    except ValueError:
        print(f"Raw Response: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Erro de conexão ou requisição: {e}")


