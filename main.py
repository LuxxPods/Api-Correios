import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import socket

app = Flask(__name__)
CORS(app)

# Token fornecido pelo Melhor Envio
MELHOR_ENVIO_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNWVjNWUwZGYzZmJiZDIwOTc1ZjljNTVkNzlhNWVlMDVmZGU2YjM5YTliZTU1NGNiYWI1YTNjMjYwNjBlMjRlZTMyOTFiMWEwYzZkYmRkMGIiLCJpYXQiOjE3NDc1MjIxODUuNzM5MjYsIm5iZiI6MTc0NzUyMjE4NS43MzkyNjIsImV4cCI6MTc3OTA1ODE4NS43Mjc2NDEsInN1YiI6IjllZWY5ODYwLTlhZGQtNDIyOS04NmQ1LWEzMTYzMmMzNzk0ZSIsInNjb3BlcyI6WyJjYXJ0LXJlYWQiLCJjYXJ0LXdyaXRlIiwiY29tcGFuaWVzLXJlYWQiLCJjb21wYW5pZXMtd3JpdGUiLCJjb3Vwb25zLXJlYWQiLCJjb3Vwb25zLXdyaXRlIiwibm90aWZpY2F0aW9ucy1yZWFkIiwib3JkZXJzLXJlYWQiLCJwcm9kdWN0cy1yZWFkIiwicHJvZHVjdHMtZGVzdHJveSIsInByb2R1Y3RzLXdyaXRlIiwicHVyY2hhc2VzLXJlYWQiLCJzaGlwcGluZy1jYWxjdWxhdGUiLCJzaGlwcGluZy1jYW5jZWwiLCJzaGlwcGluZy1jaGVja291dCIsInNoaXBwaW5nLWNvbXBhbmllcyIsInNoaXBwaW5nLWdlbmVyYXRlIiwic2hpcHBpbmctcHJldmlldyIsInNoaXBwaW5nLXByaW50Iiwic2hpcHBpbmctc2hhcmUiLCJzaGlwcGluZy10cmFja2luZyIsImVjb21tZXJjZS1zaGlwcGluZyIsInRyYW5zYWN0aW9ucy1yZWFkIiwidXNlcnMtcmVhZCIsInVzZXJzLXdyaXRlIiwid2ViaG9va3MtcmVhZCIsIndlYmhvb2tzLXdyaXRlIiwid2ViaG9va3MtZGVsZXRlIiwidGRlYWxlci13ZWJob29rIl19.RcxrcrNL7qlkxNZtldg3sDBSlx2pj8vHhFEf1tGA5ODzPYNMqyPcnsOPVigplwEiWxZ4y2B69IBvqJG_WYTpfH1_5CVVhKqgyyAmnmwv4qUMgsGoH5EedpYBB5IF3C18_mpCYFISX3LLWwi4m-4Nzy_fxxnSmDLulyG5KUzAIlv_trStkxoqwII_2xRUbPQ0Dc_Ly4kzY1C8nE85SABVytVR5GaTSrfMPzVSZJ9L9YKUUA7pi7DVAHwCkLc2ugYyctSKA2CJQ2zv0Oho2ndqTxiIgVzlJz8SWzmFSpXtYz0zWnpWgSIj74yZKI9W28xp0YYSXVuN6FydbPnLVjjfz296rW4OoB72csD5jRtCSlO2vBBuX5d3y5swJkUgWD2x4mFCnwL5Y62H-vcA6D9AkLidKSLdstY4hA0VNgRazwi535a3HktyQlf8HiBapDLKvzKEisc7yzrUB71SbEj6sArN-iL8WYs5QRWkkyPSQENykCgGLPTGX5b-G9pibVUgBCMbLaeZSRWTa2hfuu-zCEHqu6LBdX77yMG8Nszi7Hi0JhZiLB532f_M0geEYk9JVo4kmsKb1EeCoh-rjcZjyfZU8m1SCk_EDrefAg2jSkWfH-VGs7jBLw0ZbYz3L3sYb1GG-E2PieigPU3s25nc9T_xo1ZeoxJE_dl8BO2tJk4"  # Substitua aqui pelo seu token real

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
        # Verificar resolução de DNS
        ip = socket.gethostbyname("api.melhorenvio.com.br")
        return jsonify({"status": "Conectividade OK", "ip": ip})
    except Exception as e:
        return jsonify({"erro": f"Erro de DNS ou conectividade: {str(e)}"}), 500

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
            timeout=10  # Timeout de 10 segundos
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
