import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta

# === CONFIGURAÇÕES ===
app = Dash(__name__, title='Dash Homailson')

SEARCH_TERMS = ["petrobras", "C%26A", "WEG"]
COMPANY_SYMBOLS = {
    "PETR4": "PETR4.SA",
    "C%26A": "CEAB3.SA",
    "WEG": "WEGE3.SA"
}
BASE_URL = "https://braziljournal.com/?s="
START_DATE = datetime.now() - timedelta(days=365)
END_DATE = datetime.now()

# === WEB SCRAPING ===
def buscar_links_de_noticias(termos):
    hrefs = []
    for termo in termos:
        soup = BeautifulSoup(requests.get(BASE_URL + termo).content, 'html.parser')
        links = soup.find_all('h2', class_='boxarticle-infos-title')
        empresa = "PETR4" if termo == "petrobras" else termo
        hrefs.extend({"company": empresa, "href": tag.find('a')['href']} for tag in links)
    return hrefs

def extrair_conteudo(head, atributo, valor):
    meta = head.find('meta', attrs={atributo: valor})
    return meta['content'] if meta else None

def extrair_dados_da_pagina(info):
    soup = BeautifulSoup(requests.get(info["href"]).content, 'html.parser')
    head = soup.head
    tags = [tag['content'] for tag in head.find_all('meta', {'property': 'article:tag'})]
    return {
        "company": info["company"],
        "href": info["href"],
        "title": extrair_conteudo(head, 'property', 'og:title'),
        "author": extrair_conteudo(head, 'name', 'twitter:data1'),
        "section": extrair_conteudo(head, 'property', 'article:section'),
        "tags": tags,
        "published_time": extrair_conteudo(head, 'property', 'article:published_time'),
        "description": extrair_conteudo(head, 'name', 'twitter:description'),
        "lecture_time": extrair_conteudo(head, 'name', 'twitter:data2')
    }

def extrair_noticias_em_paralelo(hrefs):
    with ThreadPoolExecutor() as executor:
        return list(executor.map(extrair_dados_da_pagina, hrefs))

def coletar_noticias():
    try:
        hrefs = buscar_links_de_noticias(SEARCH_TERMS)
        noticias = extrair_noticias_em_paralelo(hrefs)
        df = pd.DataFrame(noticias)
        df.to_csv("noticias.csv", index=False)
        return df
    except Exception as e:
        print(f"[AVISO] Falha ao coletar notícias: {e}")
        if os.path.exists("noticias.csv"):
            return pd.read_csv("noticias.csv")
        return pd.DataFrame()

# === YFINANCE ===
def obter_dados_acoes(simbolos):
    dados = []
    try:
        for nome, simbolo in simbolos.items():
            df = yf.download(simbolo, start=START_DATE, end=END_DATE, progress=False)
            if df.empty:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = ['_'.join(col).strip() for col in df.columns]
            df = df.filter(regex=f'{simbolo}$')
            df.rename(columns={
                f'Open_{simbolo}': 'Open',
                f'Close_{simbolo}': 'Close',
                f'High_{simbolo}': 'High',
                f'Low_{simbolo}': 'Low',
                f'Volume_{simbolo}': 'Volume'
            }, inplace=True)
            df['Date'] = df.index
            df['company'] = nome
            dados.append(df.reset_index(drop=True))
        df_final = pd.concat(dados)
        df_final.to_csv("acoes.csv", index=False)
        return df_final
    except Exception as e:
        print(f"[AVISO] Falha ao obter dados de ações: {e}")
        if os.path.exists("acoes.csv"):
            return pd.read_csv("acoes.csv", parse_dates=['Date'])
        return pd.DataFrame()

# === COLETA DE DADOS ===
df_noticias = coletar_noticias()
dados_acoes = obter_dados_acoes(COMPANY_SYMBOLS)

# === LAYOUT DASH ===
app.layout = html.Div(className="app_container", children=[
    html.Div(className="graph_container", children=[
        dcc.Dropdown(
            className="dropdown_menu",
            id="ticker",
            options=[{"label": name, "value": name} for name in COMPANY_SYMBOLS],
            value="PETR4"
        ),
        dcc.Graph(id="stock_graphs")
    ]),
    html.Div(className="news_container", children=[
        html.H1("Notícias"),
        html.Div(id='news_container')
    ])
])

# === CALLBACKS ===
@app.callback(Output("stock_graphs", "figure"), Input("ticker", "value"))
def atualizar_grafico(empresa):
    df = dados_acoes[dados_acoes["company"] == empresa]
    fig = px.line(
        df, x="Date", y="Open",
        hover_data=["High", "Low", "Close"],
        labels={"Open": "Abertura", "High": "Alta", "Low": "Baixa", "Close": "Fechamento"}
    )
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(189, 194, 191)',
        paper_bgcolor='rgba(189, 194, 191)',
        yaxis_title=''
    )
    return fig

@app.callback(Output("news_container", "children"), Input("ticker", "value"))
def atualizar_noticias(empresa):
    noticias = df_noticias[df_noticias['company'] == empresa].head(3)
    return [
        html.Div([
            html.P(noticia['section']),
            html.H2(html.A(noticia['title'], href=noticia['href'], target='_blank'))
        ]) for _, noticia in noticias.iterrows()
    ]

# === RUN ===
server = app.server

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))  # Render define PORT
    app.run(host='0.0.0.0', port=port, debug=False)
