import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# URL do serviço SOAP dos Correios
CORREIOS_API_URL = "http://ws.correios.com.br/calculador/CalcPrecoPrazo.asmx"
ADDITIONAL_FEE = 7.0

# Parâmetros padrão
SERVICE_CODE = "04510"  # PAC
SOURCE_ZIPCODE = "01001-000"  # CEP de origem padrão
WEIGHT = "1"
FORMAT = "1"  # Formato caixa/pacote
LENGTH = "20"
HEIGHT = "10"
WIDTH = "15"
DIAMETER = "0"
MAO_PROPRIA = "N"
VALOR_DECLARADO = "0"
AVISO_RECEBIMENTO = "N"

@app.route('/')
def index():
    return "API de cálculo de frete está ativa."

@app.route('/calcular-frete', methods=['POST'])
def calcular_frete():
    data = request.json
    cep_destino = data.get("cep")

    if not cep_destino:
        return jsonify({"error": "CEP é obrigatório."}), 400

    # Montando a requisição SOAP
    soap_envelope = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
      <soap12:Body>
        <CalcPrecoPrazo xmlns="http://tempuri.org/">
          <nCdEmpresa></nCdEmpresa>
          <sDsSenha></sDsSenha>
          <nCdServico>{SERVICE_CODE}</nCdServico>
          <sCepOrigem>{SOURCE_ZIPCODE}</sCepOrigem>
          <sCepDestino>{cep_destino}</sCepDestino>
          <nVlPeso>{WEIGHT}</nVlPeso>
          <nCdFormato>{FORMAT}</nCdFormato>
          <nVlComprimento>{LENGTH}</nVlComprimento>
          <nVlAltura>{HEIGHT}</nVlAltura>
          <nVlLargura>{WIDTH}</nVlLargura>
          <nVlDiametro>{DIAMETER}</nVlDiametro>
          <sCdMaoPropria>{MAO_PROPRIA}</sCdMaoPropria>
          <nVlValorDeclarado>{VALOR_DECLARADO}</nVlValorDeclarado>
          <sCdAvisoRecebimento>{AVISO_RECEBIMENTO}</sCdAvisoRecebimento>
        </CalcPrecoPrazo>
      </soap12:Body>
    </soap12:Envelope>"""

    headers = {
        "Content-Type": "application/soap+xml; charset=utf-8"
    }

    try:
        response = requests.post(CORREIOS_API_URL, data=soap_envelope, headers=headers)
        if response.status_code != 200:
            return jsonify({"error": "Erro na requisição aos Correios."}), 500

        # Processando a resposta
        response_text = response.text
        if "<Valor>" not in response_text or "<PrazoEntrega>" not in response_text:
            return jsonify({"error": "Erro ao calcular o frete."}), 500

        # Extraindo os valores
        valor = float(response_text.split("<Valor>")[1].split("</Valor>")[0].replace(",", "."))
        prazo = int(response_text.split("<PrazoEntrega>")[1].split("</PrazoEntrega>")[0])
        valor_final = valor + ADDITIONAL_FEE

        return jsonify({
            "valor": valor_final,
            "prazo": prazo
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0")
