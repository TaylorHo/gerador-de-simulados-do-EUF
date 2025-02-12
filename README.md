# Gerador de Simulados do EUF

Gerador de Provas de Simulação para o Exame Unificado de Física, utilizando questões das provas de 2020 a 2023 (2024 está propositalmente de fora paara que sejam utilizadas como simulados à parte).

## Instalação

Crie um ambiente virtual com python:
```sh
python3 -m venv venv
source ./venv/bin/activate
```

E instale as dependências:
```sh
pip install -r requirements.txt
```

## Gerando os PDFs simulados
Gere os PDFs de simulação com:
```sh
python script.py
```

Os simulados exportados estarão na pasta `./simulations/`. Serão gerados exatamente 10 simulados.

## Conferindo os gabaritos
Para conferir a resposta dê uma olhada no acervo de provas anteriores do [Uai Física](https://www.youtube.com/channel/UCbfpYGPzXf1QjakNd-hpfcw) (excelente canal). [Link aqui para os gabaritos](https://www.uaifisica.com.br/euf).

