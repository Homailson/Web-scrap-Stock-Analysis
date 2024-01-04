import requests
import pandas as pd
from bs4 import BeautifulSoup
import concurrent.futures
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import yfinance as yf 
from datetime import datetime, timedelta

app=Dash(__name__,title='Dash Homailson')

# Web Scrapping Start
def get_company_hrefs_from_search(url_string, search_list):
    all_news_hrefs_companies_dict = []
    for search_parameter in search_list:
        response=requests.get(url_string+search_parameter)
        content=response.content
        site=BeautifulSoup(content, 'html.parser')
        h2_element=site.findAll('h2', attrs={'class':'boxarticle-infos-title'})        
        hrefs=list(map(lambda e: {"company":"PETR4" if search_parameter=="petrobras" else search_parameter,
                                  "href":e.find('a')['href']},
                                  [element for element in h2_element]))
        all_news_hrefs_companies_dict.extend(hrefs)

    return all_news_hrefs_companies_dict


def find_meta_content(news_element, attr_key, attr_value):
    meta_data=news_element.find('meta', attrs={attr_key:attr_value})
    return meta_data['content'] if meta_data else "null"


def get_news_data_from_hrefs(hrefs_companies_dict):
    all_news_data = []
    for item in hrefs_companies_dict:
        response=requests.get(item["href"])
        content=response.content
        full_news=BeautifulSoup(content,'html.parser')
        news_head=full_news.find('head')        
        tags_meta=news_head.find_all('meta', {'property': 'article:tag'})
        news_data = {            
            "company":item["company"],
            "href":item["href"],            
            "title":find_meta_content(news_head,'property','og:title'),
            "author":find_meta_content(news_head,'name','twitter:data1'),
            "section":find_meta_content(news_head, 'property','article:section'),
            "tags":[tag.get('content') for tag in tags_meta if len(tags_meta)!=0],
            "published_time":find_meta_content(news_head,'property','article:published_time'),
            "description":find_meta_content(news_head, 'name','twitter:description'),
            "lecture_time":find_meta_content(news_head, 'name','twitter:data2')
        }
        all_news_data.append(news_data)
    return all_news_data

def get_news_data_parallel(hrefs_companies_dict):
    s_batch=8
    all_batches=[hrefs_companies_dict[i:i + s_batch] for i in range(0, len(hrefs_companies_dict), s_batch)]
    all_news_data = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(get_news_data_from_hrefs, all_batches))
    for result in results:
        all_news_data.extend(result)
    return all_news_data

companies_and_symbols = {
    "petrobras":"PETR4.SA",
    "C%26A":"CEAB3.SA",
    "WEG":"WEGE3.SA"
}

hrefs_dict = get_company_hrefs_from_search("https://braziljournal.com/?s=",companies_and_symbols.keys())
all_news_info = get_news_data_parallel(hrefs_dict)
all_news_info_DF = pd.DataFrame.from_dict(all_news_info, orient='columns')
print(all_news_info_DF)
# Web Scrapping End


#Stock Data Getting Start
start_date=(datetime.now() - timedelta(days=365))
end_date=datetime.now()


def get_stock_data(company_symbol_dict):
    all_data=pd.DataFrame()
    for name, symbol in company_symbol_dict.items():
        data = yf.download(symbol, start=start_date, end=end_date, progress=False)        
        data["company"]="PETR4" if name=="petrobras" else name
        all_data = pd.concat([all_data, data])
    return all_data

all_companies_stock_data = get_stock_data(companies_and_symbols)
all_companies_stock_data.reset_index(inplace=True)
all_companies_stock_data.columns = [col.lower() for col in all_companies_stock_data.columns]
print(all_companies_stock_data)
#Stock Data Getting End

#Dash Construction Start
app.layout = html.Div(className="app_container", children=[  
    html.Div(className="graph_container", children=[
        dcc.Dropdown(
            className="dropdown_menu",
            id="ticker",
            options=["PETR4", "C%26A", "WEG"],
            value="PETR4",            
        ),       
        dcc.Graph(id="stock_graphs")]),        
    html.Div(className="news_container", children=[
        html.H1("News"),
        html.Div(id='news_container')])       
])

@app.callback(
    Output("stock_graphs", "figure"), 
    Input("ticker", "value")
)

def update_graph_output(value):
    all_companies_filtered = all_companies_stock_data.loc[all_companies_stock_data["company"]==value,:]
    graph=px.line(all_companies_filtered, x="date", y="open",
                  hover_data={"high": ":.2f", "low": ":.2f", "close": ":.2f"},
                  labels={"date": "", "high": "high:", "low": "low:", "open": "open:", "close": "close:"})    
    graph.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(189, 194, 191)',
            paper_bgcolor='rgba(189, 194, 191)',
        )
    graph.update_yaxes(title_text='')
    for trace in graph.data:
        trace.hovertemplate = trace.hovertemplate.replace("=", "")
    return graph


@app.callback(
    Output("news_container", "children"), 
    Input("ticker", "value")
)

def update_news(value):
    filtered_news = all_news_info_DF[all_news_info_DF['company'] == value].head(3)   
    
    news_elements = [
        html.Div([            
            html.P(section),
            html.H2(children=html.A(href=href, children=title, target='_blank'))            
        ]) for href, title, section in zip(filtered_news['href'], filtered_news['title'], filtered_news['section'])
    ]
    return news_elements
#Dash Construction End

if __name__=='__main__':
    app.run_server(debug=True)