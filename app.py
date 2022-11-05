<<<<<<< HEAD

from importlib.resources import path
from dash import Dash, html, dcc, Input, Output, callback, ctx
=======
from turtle import width
from dash import Dash, Input, Output, State, dcc, html, callback
>>>>>>> 6d6fbe8 (offcanvas 사용 코드)
import dash
import dash_bootstrap_components as dbc
from datetime import date
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import db
from datetime import timedelta, date


<<<<<<< HEAD

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = Dash(__name__,suppress_callback_exceptions=True)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

cities=["광진구","강동구","성동구","강남구","강서구","강북구","관악구","구로구","금천구","노원구","동대문구","도봉구","동작구","마포구","서대문구","성북구","서초구","송파구","영등포구","용산구","양천구","은평구","종로구","중구","중랑구"]

=======
app = dash.Dash(__name__)
>>>>>>> 6d6fbe8 (offcanvas 사용 코드)

#임시데이터
df = pd.DataFrame({
    "SIG_KOR_NM": ["광진구","강동구","성동구","강남구","강서구","강북구","관악구","구로구","금천구","노원구","동대문구","도봉구","동작구","마포구","서대문구","성북구","서초구","송파구","영등포구","용산구","양천구","은평구","종로구","중구","중랑구"],
    "Amount": [1000,500,100,0,234,764,2436,764,34,87,12,76,235,764,124,7853,14,564,236,764,1348,536,234,546,5271]
})

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "absolute",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "display":"visible",
    "float":"left",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.



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





offcanvas = html.Div([
    dbc.Button(
        "open offcanvas",
        id="open-offcanvas",
        n_clicks=0
    ),
    dbc.Offcanvas(
        html.P(
             html.Div([
                html.H2(children='데이터 셋팅'),
                html.H3(children='기간 및 이동수단을 설정해주세요.'),
                html.H4('기간 설정'),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    min_date_allowed=date(2000, 1, 1),
                    max_date_allowed=date(2022, 10, 16),
                    initial_visible_month=date(2022, 9, 15),
                ),
                html.H4('이동수단 설정'),
                dcc.Dropdown(
                    ['오토바이'], '오토바이', 
                    id='mobility-dropdown',
                    style={
                        'width':"18rem",
                    },),
                html.Div(id='dd_mobility'),
                ],
                style=SIDEBAR_STYLE),
        ),
        id="offcanvas",
        title="title",
        is_open=False,
        close_button=True,
    ),
])


<<<<<<< HEAD
  
=======

CONTENT_STYLE = {
    "margin-left": "20rem",
    "mragin-right": "2rem",
    "padding": "2rem 1rem",
}
content =  html.Div([   
    # represents the browser address bar and doesn't render anything
    dcc.Location(id='url', refresh=False),
    
    # content will be rendered in this element
    html.Div(id='page-content'),
    #html.Div(id="hidden_div_for_redirect_callback")
    ],
    style=CONTENT_STYLE
)

>>>>>>> 6d6fbe8 (offcanvas 사용 코드)
index_page = html.Div([
    dcc.Graph(id='graph',figure=fig),
    html.Div(id='index'),
    print("index")
])

def analytics_page(location):
    print(location)
    
    #왼쪽 지도 관련
    features = {"type": "FeatureCollection","features":[i for i in dong['features'] if i['properties']['sggnm']==location]}
    xy=features['features'][0]['geometry']['coordinates'][0][0][5]
    crime_info = db.select_gu(str(location))
    fig1.add_trace(go.Scattermapbox(
        lat= crime_info['x'] if not crime_info.empty else [],
        lon=crime_info['y'] if not crime_info.empty else [],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14,
            color='rgb(242, 24, 24)'
        ),
        text=crime_info['location'] if not crime_info.empty else [],
    ))
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
    
    #오른쪽 그래프 관련 수정수정수정하자~~~~~~~~~~~~~~~~
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(x=list(i.time() for i in crime_info['time']),line = dict(color='red'))
    )     
    
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
        
        html.Div(id="map",children=[
            html.Div(),
            dcc.Graph(id='dong-graph',figure=fig2)],style={'width':"50%","float": "right"})
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

@callback(
    Output("offcanvas","is_open"),
    [Input("open-offcanvas","n_clicks")],
    [State("offcanvas","is_open")],
)

<<<<<<< HEAD






=======
def toggle_opencanvas(n,is_open):
    if n:
        return not is_open
    return is_open

app.layout = html.Div([offcanvas, content])
#서버 실행
>>>>>>> 6d6fbe8 (offcanvas 사용 코드)
if __name__ == '__main__':
    app.run_server(debug=True)