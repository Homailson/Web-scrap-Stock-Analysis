# Dash Homailson

O **Dash Homailson** é uma aplicação web desenvolvida utilizando o framework **Dash**, **Plotly**, **Pandas** e **BeautifulSoup** para visualização interativa de dados financeiros e notícias. O objetivo do aplicativo é fornecer gráficos financeiros e informações atualizadas sobre empresas brasileiras, integrando dados de ações com notícias relacionadas.

## Funcionalidades:

- **Visualização de Gráficos de Ações:**  
  Exibe gráficos interativos com dados históricos de ações de empresas selecionadas (PETR4, C&A, WEGE3), utilizando o **yFinance** para obter os dados financeiros, com indicadores como abertura, fechamento, alta e baixa.

- **Notícias Relevantes:**  
  Coleta e exibe notícias sobre as empresas selecionadas, extraindo links e metadados de uma página de notícias usando **Web Scraping** com **BeautifulSoup**. As notícias são atualizadas automaticamente com o uso de múltiplas threads para agilizar o processo de extração.

- **Interface Interativa:**  
  A interface é construída com **Dash** e **Plotly**, permitindo ao usuário selecionar empresas e visualizar os gráficos de ações e notícias relacionadas em tempo real.

## Tecnologias Utilizadas:

- **Dash:** Framework para criação de aplicações web interativas.
- **Plotly:** Biblioteca para criação de gráficos interativos.
- **Pandas:** Manipulação de dados financeiros.
- **yFinance:** Coleta de dados históricos de ações.
- **BeautifulSoup:** Web scraping para extrair notícias.
- **ThreadPoolExecutor:** Execução paralela para agilizar o processo de scraping de notícias.

## Como Rodar:

1. Clone o repositório:
    ```bash
    git clone https://github.com/SEU_USUARIO/Dash_Homailson.git
    ```

2. Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

3. Execute o aplicativo:
    ```bash
    python app.py
    ```

4. Acesse no navegador:
    ```bash
    http://127.0.0.1:8050/
    ```

---

Esse `README.md` serve como um guia básico de como usar e rodar a aplicação. Basta você adicionar o caminho correto do seu repositório no GitHub e o nome do arquivo de execução (`app.py` ou o que for o seu nome de arquivo principal).