import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import socket

app = Flask(__name__)
CORS(app)

# Token fornecido pelo Melhor Envio
MELHOR_ENVIO_TOKEN = "SEU_TOKEN_AQUI"  # Substitua aqui pelo seu token real

# Dados fixos
SHIPMENT_DATA = {
    "from": {
        "postal_code": "03057-970"  # Origem fixa
    },
    "to": {
        "postal_code": ""  # Será preenchido dinamicamente
    },
    "products": [
        {
            "weight": 1,
            "width": 15,
            "height": 10,
            "length": 20,
            "insurance_value": 0,
            "quantity": 1
        }
    ],
    "services": ["1"]  # SEDEX
}

# Taxa adicional fixa
ADDITIONAL_FEE = 7.0

@app.route('/')
def index():
    return "API de frete com Melhor Envio está ativa."

# Rota para testar a conectividade
@app.route('/teste-conexao')
def teste_conexao():
    try:
        ip = socket.gethostbyname("api.melhorenvio.com.br")
        return jsonify({"status": "Conectividade OK", "ip": ip})
    except Exception as e:
        return jsonify({"erro": f"Erro de DNS ou conectividade: {str(e)}"}), 500

# Rota para testar a resolução DNS
@app.route('/dns-teste')
def dns_teste():
    resultados = {}
    dominios = ["api.melhorenvio.com.br", "google.com", "github.com"]

    for dominio in dominios:
        try:
            ip = socket.gethostbyname(dominio)
            resultados[dominio] = {"status": "OK", "ip": ip}
        except Exception as e:
            resultados[dominio] = {"status": "Erro", "erro": str(e)}

    return jsonify(resultados)

@app.route('/calcular-frete', methods=['POST'])
def calcular_frete():
    data = request.json
    cep_destino = data.get("cep")

    if not cep_destino:
        return jsonify({"erro": "Por favor, informe o CEP de destino."}), 400

    payload = SHIPMENT_DATA.copy()
    payload["to"]["postal_code"] = cep_destino

    headers = {
        "Authorization": f"Bearer {MELHOR_ENVIO_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(
            "https://api.melhorenvio.com.br/api/v2/me/shipment/calculate",
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            return jsonify({
                "erro": "Erro ao consultar o Melhor Envio.",
                "status": response.status_code,
                "resposta": response.text
            }), 500

        services = response.json()

        # Filtrar somente SEDEX
        sedex_service = next((s for s in services if s["name"].lower() == "sedex"), None)
        if not sedex_service:
            return jsonify({"erro": "SEDEX não disponível para esse CEP."}), 400

        valor = float(sedex_service["price"])
        prazo = sedex_service["delivery_time"]

        valor_final = round(valor + ADDITIONAL_FEE, 2)

        return jsonify({
            "servico": sedex_service["name"],
            "frete": f"R$ {valor_final:.2f}",
            "prazo": f"{prazo} dias úteis"
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"erro": f"Erro na requisição: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
