import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite requisições externas, como do BOTCONVERSA

# Taxa fixa da empresa
ADDITIONAL_FEE = 7.00

# Dados fixos do envio
FIXED_DATA = {
    "cepOrigem": "03057-970",     # CEP da empresa
    "peso": 1,
    "formato": 1,
    "comprimento": 20,
    "altura": 10,
    "largura": 15,
    "diametro": 0,
    "servico": "04510",  # PAC
    "valorDeclarado": 0,
    "maoPropria": False,
    "avisoRecebimento": False
}

@app.route("/")
def index():
    return "API de frete está ativa para integração com BOTCONVERSA."

@app.route("/calcular-frete", methods=["POST"])
def calcular_frete():
    data = request.json
    cep_destino = data.get("cep")

    if not cep_destino:
        return jsonify({"erro": "Informe o CEP de destino."}), 400

    payload = FIXED_DATA.copy()
    payload["cepDestino"] = cep_destino

    try:
        response = requests.post("https://brasilapi.com.br/api/correios/calculo-pratico", json=payload)
        if response.status_code != 200:
            return jsonify({"erro": "Erro ao consultar a BrasilAPI."}), 500

        result = response.json()

        if "valor" not in result or "prazoEntrega" not in result:
            return jsonify({"erro": "Resposta inválida da BrasilAPI."}), 500

        valor = float(result["valor"].replace("R$", "").replace(",", ".").strip())
        valor_final = round(valor + ADDITIONAL_FEE, 2)
        prazo = result["prazoEntrega"]

        return jsonify({
            "frete": f"R$ {valor_final:.2f}",
            "prazo": f"{prazo} dias úteis"
        })

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
