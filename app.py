
from importlib.resources import path
from dash import Dash, html, dcc, Input, Output, callback, ctx
import dash
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import db
from datetime import timedelta, date
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import arrow_function


#두번쨰페이지 지도 소스
url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

app = Dash(__name__,suppress_callback_exceptions=True)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

cities=["광진구","강동구","성동구","강남구","강서구","강북구","관악구","구로구","금천구","노원구","동대문구","도봉구","동작구","마포구","서대문구","성북구","서초구","송파구","영등포구","용산구","양천구","은평구","종로구","중구","중랑구"]


#임시데이터
df = pd.DataFrame({
    "SIG_KOR_NM": ["광진구","강동구","성동구","강남구","강서구","강북구","관악구","구로구","금천구","노원구","동대문구","도봉구","동작구","마포구","서대문구","성북구","서초구","송파구","영등포구","용산구","양천구","은평구","종로구","중구","중랑구"],
    "Amount": [1000,500,100,0,234,764,2436,764,34,87,12,76,235,764,124,7853,14,564,236,764,1348,536,234,546,5271]
})

#마커추가
def add_marker(gu,dong):
    data = db.select_dong_cctv(gu,dong)
    position = data[['x','y']].values.tolist()
    
    return [dl.Marker(position=i) for i in position]


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
    html.Div(id='total',
        children=[
            html.H1('총 발생현황'),
            html.H3('구별 범법행위 순위'),
            html.Ol(id='total_gu_list', children=[html.Li(i[0]) for i in []]), #db.select_total_gu()[['gu_nm','count']].values.tolist()
            html.Br(),
            html.Br(),
            html.H3('누적 발생 현황'),
            html.Span('Today   '),
            html.Span(id='today_cnt',children = ''),
            html.Br(),
            html.Span('Total   '),
            html.Span(id='total_cnt',children = '')
        ],
    ),
    print("index")
])



def analytics_page(location):
    print(location)
    
    #왼쪽 지도 관련
    features = {"type": "FeatureCollection","features":[i for i in dong['features'] if i['properties']['sggnm']==location]}
    xy=features['features'][0]['geometry']['coordinates'][0][0][5]
    geobuf=dlx.geojson_to_geobuf(features)  
    crime_info = db.select_gu(location)
    
    #오른쪽 그래프 관련 수정수정수정하자~~~~~~~~~~~~~~~~
    data= go.Bar(x=list(i.to_pydatetime().day for i in crime_info['time']))
    fig2 = go.Figure(data=data)
    # fig2.add_trace(
    #     go.Scatter(x=list(i.to_pydatetime().day for i in crime_info['time']),line = dict(color='red'))
    # )     
    
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
        
        ### 왼쪽 지도 
        html.Div(children=[
            dl.Map(center=[37.58156996270885,127.01178832759342], zoom=12, 
            children=[
                dl.TileLayer(url=url,attribution=attribution), 
                dl.GeoJSON(data=features),  # in-memory geojson (slowest option)
                dl.GeoJSON(data=geobuf, format="geobuf"),  # in-memory geobuf (smaller payload than geojson)
                dl.GeoJSON(data=features, id="capitals"),  # geojson resource (faster than in-memory)
                dl.LayersControl([
                    dl.Overlay(
                        dl.LayerGroup(add_marker('강동구','명일동')), 
                        name="markers", checked=True)]),
                dl.GeoJSON(data=geobuf, id="states",format="geobuf",zoomToBoundsOnClick=True,hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray=''))),  # geobuf resource (fastest option)
                ], style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}, id="map"),
            html.Div(id="state"), html.Div(id="capital")],style={'width':"50%","float": "left"}),
        
        
        html.Div(id="map",children=[
            dcc.Graph(id='diverse-graph',figure=fig2)],style={'width':"50%","float": "right"})
    ])
    
    
    
def detail_page(detail_location):
    return html.Div(id="detail_page-content",children=[
        
        html.Div("i clieked"+detail_location)
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



@callback(Output("capital", "children"), [Input("states", "click_feature")])
def capital_click(feature):
    if feature is not None:
        return f"You clicked {feature['properties']['adm_nm']}"


@callback(Output("state", "children"), [Input("states", "hover_feature")])
def state_hover(feature):
    if feature is not None:
        return f"{feature['properties']['adm_nm']}"
    

@callback(Output("total_gu_list", "children"),Input("total",'children'))
def change_total_gu_list(none):
    return [html.Li(i[0]) for i in db.select_total_gu(11)[['gu_nm','count']].values.tolist()] 

@callback(Output("today_cnt", "children"),Input("total",'children'))
def change_today_cnt(none):
    return db.select_today()

@callback(Output("total_cnt", "children"),Input("total",'children'))
def change_today_cnt(none):
    return db.select_total()



# def update_point(trace, points, selector):
#     with fig1.batch_update():
#         return

       

@callback(Output("detail_page-content",'children'),
          Input('dong-graph','clickData'))
def A(clickData):
    print("^^"+clickData)
    return
    


    






if __name__ == '__main__':
    app.run_server(debug=True)