import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Token fornecido pelo Melhor Envio
MELHOR_ENVIO_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiMDgyM2ZlZDYzNzNlODEyMzlhODcyZmNhMmQ4NDU3NjVlNDdiZjg4ZmE0OWY3NDUzMmJiYmY4OTM1ZjUwZTBhZDFmY2Q1ZDA4ODAzMzM2N2QiLCJpYXQiOjE3NDc1MjAwNzUuMzg4Mzg5LCJuYmYiOjE3NDc1MjAwNzUuMzg4MzkxLCJleHAiOjE3NzkwNTYwNzUuMzgxODcsInN1YiI6IjllZWY5ODYwLTlhZGQtNDIyOS04NmQ1LWEzMTYzMmMzNzk0ZSIsInNjb3BlcyI6WyJjYXJ0LXJlYWQiLCJjYXJ0LXdyaXRlIiwiY29tcGFuaWVzLXJlYWQiLCJjb21wYW5pZXMtd3JpdGUiLCJjb3Vwb25zLXJlYWQiLCJjb3Vwb25zLXdyaXRlIiwibm90aWZpY2F0aW9ucy1yZWFkIiwib3JkZXJzLXJlYWQiLCJwcm9kdWN0cy1yZWFkIiwicHJvZHVjdHMtZGVzdHJveSIsInByb2R1Y3RzLXdyaXRlIiwicHVyY2hhc2VzLXJlYWQiLCJzaGlwcGluZy1jYWxjdWxhdGUiLCJzaGlwcGluZy1jYW5jZWwiLCJzaGlwcGluZy1jaGVja291dCIsInNoaXBwaW5nLWNvbXBhbmllcyIsInNoaXBwaW5nLWdlbmVyYXRlIiwic2hpcHBpbmctcHJldmlldyIsInNoaXBwaW5nLXByaW50Iiwic2hpcHBpbmctc2hhcmUiLCJzaGlwcGluZy10cmFja2luZyIsImVjb21tZXJjZS1zaGlwcGluZyIsInRyYW5zYWN0aW9ucy1yZWFkIiwidXNlcnMtcmVhZCIsInVzZXJzLXdyaXRlIiwid2ViaG9va3MtcmVhZCIsIndlYmhvb2tzLXdyaXRlIiwid2ViaG9va3MtZGVsZXRlIiwidGRlYWxlci13ZWJob29rIl19.Owhl-VluX6MBjLLsXfonMrPvxRWj8RK4xCmX_NOiQtgfE3QJb1SSVZ8w_KlLL8PcDjhD-Ko4MHfExUMXe5MY0Na-3GLzFjaNVGrCnXROoRozinPWKNbccnL1zSdfJ_DdqnkwKhQqRqEEj4p64FDdoxovuedzqjz7f9woEaf6BX53lQBYOxW7CmYap9y6Nb1K2IrasAunA5ddc0hB9vWfLJKXcAMCJ6HZBfiz1MOkQ7MUA1ax5PrEzNeqs907K30AiTBlERe5C4Ty0fDFsE0MvK3N8HcJZXXFYsjKYFULHKhtcl_eMADO1smkPB6e1pnRnmc86t8epcag1auMmBzh2KfKTURw4Cx3X_TxtNTp5flOgTaqZd8RsVfI6iko0iZZQRPk6zDT0Fa3VthjnoeAxUFxhS7humPLZ5VzrtL7QTCHW2AWC6oMPBQ-YDJj8_tY485KaRB-gG28ELZb-uPaXNhgaweRLNLa1OCi0yeCMBu1ViCcsAyfqrs2s7aRgvUfEi5nQQ42H54LF5G3BLTOOcKhg0pbVKG16lWtuZCY77dn6nirAcdXJLVpPahEJnNkKn1jDJIwxMBO7lO1mQDyPOq21U4cZ_YcW5W35jqxiS5PWHtpicEh7KaWBMrsXzDEeQXyIJTDkCiowhd8flTSpMPOwMTr9mmXlkAynXuvz1U"  # Substitua aqui pelo seu token real

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
            headers=headers
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

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
