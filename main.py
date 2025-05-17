import requests
from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET

app = Flask(__name__)

# URL da API dos Correios (GET)
CORREIOS_API_URL = "http://ws.correios.com.br/calculador/CalcPrecoPrazo.aspx"

# Configurações fixas do envio
FIXED_PARAMS = {
    "nCdEmpresa": "",
    "sDsSenha": "",
    "nCdServico": "04510",  # PAC
    "sCepOrigem": "01001-000",  # CEP fixo da empresa
    "nVlPeso": "1",
    "nCdFormato": "1",
    "nVlComprimento": "20",
    "nVlAltura": "10",
    "nVlLargura": "15",
    "nVlDiametro": "0",
    "sCdMaoPropria": "N",
    "nVlValorDeclarado": "0",
    "sCdAvisoRecebimento": "N",
    "StrRetorno": "xml"
}

# Taxa adicional fixa da empresa
ADDITIONAL_FEE = 7.0

@app.route('/')
def index():
    return "API de frete está ativa para integração com BOTCONVERSA."

@app.route('/calcular-frete', methods=['POST'])
def calcular_frete():
    data = request.json
    cep_destino = data.get("cep")

    if not cep_destino:
        return jsonify({"erro": "Por favor, informe o CEP de destino."}), 400

    params = FIXED_PARAMS.copy()
    params["sCepDestino"] = cep_destino

    try:
        response = requests.get(CORREIOS_API_URL, params=params)
        if response.status_code != 200:
            return jsonify({"erro": "Erro ao consultar os Correios. Tente novamente."}), 500

        root = ET.fromstring(response.content)
        servico = root.find("cServico")

        if servico.find("Erro").text != "0":
            return jsonify({"erro": "CEP inválido ou fora da área de cobertura."}), 400

        valor = float(servico.find("Valor").text.replace(",", "."))
        prazo = int(servico.find("PrazoEntrega").text)
        valor_final = round(valor + ADDITIONAL_FEE, 2)

        return jsonify({
            "frete": f"R$ {valor_final:.2f}",
            "prazo": f"{prazo} dias úteis"
        })

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
