import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configurações da API dos Correios
CORREIOS_API_URL = "https://api.correios.com.br/v1/calcular"
DEFAULT_WEIGHT = 1.0  # Peso padrão em kg
DEFAULT_LENGTH = 20  # Comprimento em cm
DEFAULT_HEIGHT = 10  # Altura em cm
DEFAULT_WIDTH = 15  # Largura em cm
DEFAULT_SERVICE = "04510"  # PAC
ADDITIONAL_FEE = 7.0

@app.route('/')
def index():
    return "API de cálculo de frete está ativa."


@app.route('/calcular-frete', methods=['POST'])
def calcular_frete():
    data = request.json
    cep_destino = data.get("cep")

    if not cep_destino:
        return jsonify({"error": "CEP é obrigatório."}), 400

    payload = {
        "peso": DEFAULT_WEIGHT,
        "comprimento": DEFAULT_LENGTH,
        "altura": DEFAULT_HEIGHT,
        "largura": DEFAULT_WIDTH,
        "servico": DEFAULT_SERVICE,
        "cep_destino": cep_destino
    }

    try:
        response = requests.post(CORREIOS_API_URL, json=payload)
        response_data = response.json()

        if response.status_code != 200 or "valor" not in response_data:
            return jsonify({"error": "Erro ao calcular o frete."}), 500

        valor_correios = float(response_data["valor"])
        prazo_correios = response_data["prazo"]
        valor_final = valor_correios + ADDITIONAL_FEE

        return jsonify({
            "valor": valor_final,
            "prazo": prazo_correios
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
