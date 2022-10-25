
from importlib.resources import path
from dash import Dash, html, dcc, Input, Output, callback, ctx
import dash
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = Dash(__name__,suppress_callback_exceptions=True)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

cities=["광진구","강동구","성동구","강남구","강서구","강북구","관악구","구로구","금천구","노원구","동대문구","도봉구","동작구","마포구","서대문구","성북구","서초구","송파구","영등포구","용산구","양천구","은평구","종로구","중구","중랑구"]


#임시데이터
df = pd.DataFrame({
    "SIG_KOR_NM": ["광진구","강동구","성동구","강남구","강서구","강북구","관악구","구로구","금천구","노원구","동대문구","도봉구","동작구","마포구","서대문구","성북구","서초구","송파구","영등포구","용산구","양천구","은평구","종로구","중구","중랑구"],
    "Amount": [1000,500,100,0,234,764,2436,764,34,87,12,76,235,764,124,7853,14,564,236,764,1348,536,234,546,5271]
})


#서울시 구 데이터 로드
geometry = json.load(open('./assets/TL_SCCO_SIG.json',encoding='utf-8'))

#Choropleth 시각화 -> 추후 SIG_KOR_NM column 을 누구나 알아볼 수 있게 바꿀예정(ex.city)
fig=px.choropleth(df,geojson=geometry,locations='SIG_KOR_NM',color='Amount',
                  color_continuous_scale='Blues',
                  featureidkey='properties.SIG_KOR_NM')
fig.update_geos(fitbounds="locations",visible=False)
fig.update_layout(title_text="example",title_font_size=20)

#서울시 동 데이터 로드
dong = json.load(open('./assets/seoul.json',encoding='utf-8'))

fig1 = go.Figure(go.Scattermapbox())





app.layout = html.Div([
    
    
    
    # represents the browser address bar and doesn't render anything
    dcc.Location(id='url', refresh=False),
    
    # content will be rendered in this element
    html.Div(id='page-content')
    #html.Div(id="hidden_div_for_redirect_callback")

])


  
index_page = html.Div([
    dcc.Graph(id='graph',figure=fig),
    html.Div(id='index'),
    print("index")
])

def analytics_page(location):
    print(location)
    features = {"type": "FeatureCollection","features":[i for i in dong['features'] if i['properties']['sggnm']==location]}
    xy=features['features'][0]['geometry']['coordinates'][0][0][5]   
    fig1.update_layout(
            mapbox = {
                'style': "carto-positron",
                'center': { 'lon': xy[0], 'lat': xy[1]},
                'zoom': 12, 
                'layers': [{ 
                    'source': features,
                    'type': "fill", 
                    'below': "traces", 
                    'color': "royalblue"}]},
            margin = {'l':0, 'r':0, 'b':0, 't':0})             
    
    return html.Div(id="analytics_page-content",
        children=[
        dcc.Location(id='url_2', refresh=False),
        html.Div(id="title",
                children=[
                    html.Div(id = "second_page"),
                    html.Div(location),
                    dcc.Dropdown(cities,location,id="city-dropdown",style={'width':"50%","float": "left"}),
                    html.H2("Dashboard",style={"float": "left"})],
                style={
                     'height':'150px',
                     'backgroundColor':'#787878'}
                ),
        html.Div(id="map",children=[
            html.Div(),
            dcc.Graph(id='dong-graph',figure=fig1)],style={'width':"50%","float": "left"}),
    ])
    
@callback(
    Output('url', 'href'),
    Input('city-dropdown', 'value'), prevent_initial_call=True)
def move_page_dropdown(value):
    print("move")
    print(value)
    if value is not None:    
        return "/"+value
        
    
    
@callback(
    Output('url', 'pathname'),
    Input('graph', 'clickData'), prevent_initial_call=True)
def move_page(clickData):
    print(clickData)
    if clickData is not None:            
        location = clickData['points'][0]['location']
        return "/"+location
    else : return "/"
    


@callback(Output('page-content', 'children'),
               Input('url', 'pathname'),prevent_initial_call=True)
def display_page(pathname):
    print("display")
    
    print(pathname)
    for city in df['SIG_KOR_NM']:
        if pathname == '/'+city :
            return analytics_page(city)

    return  index_page

@callback(Output('analytics_page-content', 'children'),
               Input('url','href'),prevent_initial_call=True)
def display_page2(href):
    print("display2")
    print(href)
    
    for city in df['SIG_KOR_NM']:
        if href=="/"+city:
            return analytics_page(city)

    return  index_page







if __name__ == '__main__':
    app.run_server(debug=True)