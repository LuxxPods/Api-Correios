# BotConversa Correios Integration

Este projeto é uma API Flask que realiza o cálculo de frete dos Correios e adiciona uma taxa de R$7,00 ao valor calculado.

### Endpoints:
- POST /calcular-frete

### Request Body:
```
{
    "cep": "01234567"
}
```

### Response:
```
{
    "valor": 27.00,
    "prazo": 5
}
```

### Deploy no Render:
1. Crie um repositório no GitHub e faça o upload dos arquivos.
2. Conecte o repositório ao Render e configure a porta padrão (5000).
