# -*- coding: utf-8 -*-
from dash import Dash, html, dcc, Input, Output, callback, ctx, ALL, no_update
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
import dash_bootstrap_components as dbc
import numpy as np


#두번쨰페이지 지도 소스
url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

app = Dash(__name__,suppress_callback_exceptions=True)
server = app.server

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

cities=["광진구","강동구","성동구","강남구","강서구","강북구","관악구","구로구","금천구","노원구","동대문구","도봉구","동작구","마포구","서대문구","성북구","서초구","송파구","영등포구","용산구","양천구","은평구","종로구","중구","중랑구"]

        

#서울시 구 데이터 로드
geometry = json.load(open('./assets/TL_SCCO_SIG.json',encoding='utf-8'))



#서울시 동 데이터 로드
dong = json.load(open('./assets/seoul.json',encoding='utf-8'))




#2. content
sidebar = html.Div([
    html.Div([
        #html.H2(children='Zol-zol-zol',className='font'),
        html.P(children=html.Img(src="assets\zolzolzol_logo.ico",width=160),className="logo"),
        html.Hr(className='hr'),
        html.Div(
            children=[
                html.H4(children=['단속 가능한 범법행위 유형',html.H5('   (단속대상 : 오토바이)')],className='sidebar_text1'),
                html.H5(children=['1. 정지선 위반 행위',html.Br(),html.Br(),'2. 보행자도로 주행 위반 행위']),
                
        ], className='sidebar_text2'), 
        html.Hr(className='hr'),
        ],
        className='sidebar')]
)

header = html.Div(
    children=[
                html.A(href="/",children=html.Img(src="assets\motorcycle.ico", ), className="header_img"),
                #html.H1(children="Dashboard", className="header_title"),
                #html.P(children="설명~", className="header_description"),
            ],
            className='header_box',
)


page_layoutbox=html.Div(
    children=[
        # represents the browser address bar and doesn't render anything
        dcc.Location(id='url', refresh=False),
    
        # content will be rendered in this element
        html.Div(id='page-content'),
        #html.Div(id="hidden_div_for_redirect_callback")
    ],
    className='layoutbox'
)

app.layout = html.Div([
    header,
    sidebar,
    page_layoutbox

])

#서울시 구별 순위 top5 stacked barplot
#fig0 = go.Figure(data=data)
#fig0.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
#                   marker_line_width=1.5, opacity=0.6)
#fig0.update_layout(
#    title='보행자도로 주행 위반 TOP5',
#    paper_bgcolor='#F5F7FA',
#    autosize=False,
#    width=580,
#    height=330,)
# fig4 = go.Figure(data=data)
# fig4.update_layout(
#     title='정지선 위반 TOP5',
#     paper_bgcolor='white',
#     autosize=False,
#     width=580,
#     height=330)
  
index_page = html.Div([
    html.H1(children='서울시 오토바이 범법행위 발생현황',className='main_title'),
    
    #html.H3('누적 발생 현황',className='index_text2'),
    html.Div([
        html.Span('Total', className='total_idx'),
        html.Br(),
        html.Span(id='total_cnt',children = '', className='total_cnt'),
    ],className='totalbox'), 
    #html.Br(),
    html.Div([
        html.Span('Today   ',className='today_idx'),
        html.Br(),
        html.Span(id='today_cnt',children = '',className='today_cnt'),
    ],className='todaybox'),
    dcc.Dropdown(
        ['2022-12','2022-11','2022-10','2022-09'], '2022-12', 
        id='date-dropdown',
        className="dropdown_date",
        ),
    html.Div(id='dd_date'),
    #지도
    dcc.Graph(id='graph',className='graph'),
    html.Div([
        html.Div(
            id="map_people",
            children=[
                dcc.Graph(id='index-graph'),
            ],
            className='index-graph_people'),
        #html.Br(),
        html.Div(
            id="map_stopline",
            children=[
                    dcc.Graph(id='index-graph_stopline'),
                ],
            className='index-graph_stopline'),

        ],
        className='index-graph_box'),       
    html.Div(id='index'),
    html.Div(id='total',
        children=[           
            html.Br(),
            
            #html.H3('자치구별 범법행위 발생순위',className='index_text3'),
            #html.Ol(id='total_gu_list', children=[html.Li(childeren=i[0]) for i in []], className='city_top5'), #db.select_total_gu()[['gu_nm','count']].values.tolist(),
            dcc.Graph(id='top5',className='top5'),
        ],
    ),
    print("index")
],
className="index_page")



def analytics_page(location):
    print(location)
    
    #왼쪽 지도 관련
    features = {"type": "FeatureCollection","features":[i for i in dong['features'] if i['properties']['sggnm']==location]}
    geobuf=dlx.geojson_to_geobuf(features)  
    
    
    return html.Div(id="analytics_page-content",
        children=[
        dcc.Location(id='url_2', refresh=False),
        html.Div(id="title",
                children=[
                    html.H1(id = "second_page"),
                    html.H1(location,className='location'),
                    html.H1('  상세현황',className='location_text'),
                    dcc.Dropdown(cities,location,id="city-dropdown",className='city-dropdown'),
                    html.Br(),html.Br(),html.Br()],
                # style={ 
                #      'height':'150px',
                #      'backgroundColor':'#787878'}
                ),
        
        ### 왼쪽 지도 
        html.Div(children=[
            dl.Map(id="left_map", zoom=12, 
            children=[
                dl.TileLayer(url=url,attribution=attribution), 
                dl.GeoJSON(data=features),  # in-memory geojson (slowest option)
                dl.GeoJSON(data=geobuf, format="geobuf"),  # in-memory geobuf (smaller payload than geojson)
                dl.GeoJSON(data=features, id="capitals"),  # geojson resource (faster than in-memory)
                dl.LayersControl([
                    dl.Overlay(
                        dl.LayerGroup(id="marker",children=[]), 
                        name="markers", checked=True)]),
                dl.GeoJSON(data=geobuf, id="states",format="geobuf",zoomToBoundsOnClick=True,hoverStyle=arrow_function(dict(weight=5, color='#666', dashArray=''))),  # geobuf resource (fastest option)
                ], style={'width': '90%', 'height': '500px', 'margin-top': "-30px"}),
            html.H3(id="state",style={'font-family':'LINESeedKR-Bd'}), html.Div(id="capital")],style={'width':"50%","float": "left","margin-left":"50px"}),
        
        ##오른쪽
        html.Div(id="right_page",children=display_gu_page(location),style={'height':'50%'},className='right_page'),
        
        #****
        
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
    return no_update
        
    
    
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
    for city in cities:
        if pathname == '/'+city :
            return analytics_page(city)

    return  index_page

@callback(Output('analytics_page-content', 'children'),
               Input('url','href'),prevent_initial_call=True)
def display_page2(href):
    print("display2")
    print(href)
    
    for city in cities:
        if href=="/"+city:
            return analytics_page(city)

    return  no_update


#동 클릭시 CCTV 마커표시
@callback(Output("marker", "children"), [Input("states", "click_feature")],prevent_initial_call=True)
def capital_click(feature):
    if feature is not None:
        si,gu,dong = feature['properties']['adm_nm'].split()
        data = db.select_dong_cctv(gu,dong)
        position = data[['id','x','y']].values.tolist()
        return [dl.Marker(id=dict(tag="mark", index=position[i][0])
                          ,position=[position[i][1],position[i][2]]) for i in range(len(position))]

        


@callback(Output("state", "children"), [Input("states", "hover_feature")])
def state_hover(feature):
    if feature is not None:
        return f"{feature['properties']['adm_nm']}"
    

########################################
#
@callback(#Output("total_gu_list", "children"),
          Output("index-graph", "figure"),
          Output("index-graph_stopline", "figure"),
          Output("graph", "figure"),
          Output("top5","figure"),
          Input("date-dropdown",'value'))
def change_total_gu_list(value):
    month = value[-2:]
    gu = db.select_total_gu(month)
    
    gu_road = db.select_crime_gu(month, "보행자 도로 위반")
    data1= go.Bar(x=gu_road['gu_nm'],y=gu_road['count'])
    fig = go.Figure(data=data1)
    fig.update_traces(marker_color='#6667AB', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5, opacity=0.8)
    fig.update_layout(
        title='보행자도로 주행 위반행위 발생순위',
        font=dict({'family':'LINESeedKR-Bd'}),
        paper_bgcolor='white',
        autosize=False,
        width=580,
        height=330,)
    
    
    
    gu_stopline = db.select_crime_gu(month, "정지선 위반")
    data2= go.Bar(x=gu_stopline['gu_nm'],y=gu_stopline['count'])
    fig4 = go.Figure(data=data2)
    fig4.update_traces(marker_color='#6667AB', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5, opacity=0.8)
    fig4.update_layout(
        title='정지선 위반행위 발생순위',
        font=dict({'family':'LINESeedKR-Bd'}),
        paper_bgcolor='white',
        autosize=False,
        width=580,
        height=330,
        )

    print("확인용")    
    total_cnt=db.select_total_cnt_gu(month)
    total=total_cnt['count'].sum()
    print(total)
    top5=gu['count'].sum()
    print(top5)
    etc=total-top5
    print(etc)
    gu_etc=gu
    print(gu_etc)
    #gu_etc.loc[-1]=['etc',etc]
    print(type(gu_etc['count']))
    #gu_etc['count'] = gu_etc['count'].astype(int)
    print(type(gu_etc['count']))

    fig0 = px.treemap(gu_etc, path=[px.Constant('서울시 범법행위 발생수 1~5위'), 'gu_nm'], 
                values='count', color='count',
                color_continuous_scale='Blues',
                hover_data=['gu_nm', 'count'],
                #color_continuous_midpoint=np.average(gu_etc['count'], weights=gu_etc['count'])
                )
    fig0.update_traces(hovertemplate='labels=%{label}<br>count=%{value}<extra></extra>')
    
    #fig0.data[0]['textfont']['size'] = 20
    fig0.update_layout(margin = dict(t=0, l=0, r=0, b=0),
                        height=105,width=815,
                        paper_bgcolor='#F5F7FA',
                        autosize=False,
                        font=dict({'family':'LINESeedKR-Bd','size':15}),
                        )

#    fig0 = go.Figure(data=data3)
#    fig0.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
#                       marker_line_width=1.5, opacity=0.6)
#    fig0.update_layout(
#        title='구별 TOP5',
#        paper_bgcolor='#F5F7FA',
#        autosize=False,
#        width=580,
#        height=330,
#        barmode='stack',
#        template=None,
        
#        )
    #여기 구별 top5
    #[html.Li(i[0]) for i in gu[['gu_nm','count']].values.tolist()],
    return fig,fig4,make_choropleth(month),fig0


def make_choropleth(month):
    #임시데이터
    df = db.select_total_cnt_gu(month)
    data=[],
    for i in cities:
        if i not in df['gu_nm'].values.tolist():
            df = pd.concat([df,pd.DataFrame({'gu_nm':[i],'count':[0]})],ignore_index=True)     

    df['count'] = df['count'].astype(int)
    #Choropleth 시각화 -> 추후 SIG_KOR_NM column 을 누구나 알아볼 수 있게 바꿀예정(ex.city)
    fig=px.choropleth(df,geojson=geometry,locations='gu_nm',color='count',
                      color_continuous_scale='Blues',
                      featureidkey='properties.SIG_KOR_NM')
    fig.update_geos(fitbounds="locations",visible=False)
    fig.update_layout(paper_bgcolor='#F5F7FA',font=dict({'family':'LINESeedKR-Bd'}))

    
    return fig


@callback(Output("today_cnt", "children"),Input("total",'children'))
def change_today_cnt(none):
    return db.select_today()

@callback(Output("total_cnt", "children"),Input("total",'children'))
def change_today_cnt(none):
    return db.select_total()

#왼쪽맵의 초점변경
@callback(
    Output("left_map", "center"),
    Input("city-dropdown",'value'))
def change_map_center(value):
    center = {"광진구":[37.545059,127.085334],"강동구":[37.5488426,127.1471646],"성동구":[37.553761,127.040564],"강남구":[37.495534,127.063303],"강서구":[37.560584,126.823248],"강북구":[37.643249,127.011323],"관악구":[37.467109,126.945020],"구로구":[37.494210,126.856663],"금천구":[37.460393,126.900460],"노원구":[37.651773,127.074682],"동대문구":[37.581575,127.054693],"도봉구":[37.668849,127.032367],"동작구":[37.498399,126.950762],"마포구":[37.559235,126.908165],"서대문구":[37.577460,126.939250],"성북구":[37.605515,127.017753],"서초구":[37.473553,127.031060],"송파구":[37.505350,127.115259],"영등포구":[37.522020,126.910389],"용산구":[37.531202,126.979884],"양천구":[37.524491,126.855483],"은평구":[37.618588,126.927385],"종로구":[37.594335,126.976226],"중구":[37.559865,126.995855],"중랑구":[37.596661,127.092716]}
    return center[value]
    

#오른쪽 그래프 바꾸기
@callback(Output("right_page", "children"),
          Input("city-dropdown",'value'),
          Input("states", "click_feature"),
          Input(dict(tag="mark", index=ALL), "n_clicks"),
          prevent_initial_call=True
          )
def change_right_page(value1,value2,value3):
    triggered_id = ctx.triggered_id
    print(triggered_id)
    print(dash.callback_context.triggered)
    
    
    if triggered_id == 'city-dropdown':
        print("1")
        print(value1) #ex) 강남구
        return display_gu_page(value1)
    elif triggered_id == 'states':
        print("2")
        print(value2) #ex) 'properties': {'OBJECTID': 378, 'adm_nm': '서울특별시 강남구 대치2동'
        return display_dong_page(value2['properties']['adm_nm'])
    else:
        k = dash.callback_context.triggered #ex)[{'prop_id': '{"index":"C000893","tag":"mark"}.n_clicks', 'value': 1}]
        if k[0]['value'] is not None and len(k)==1: #triggered_id['tag'] == 'mark'
            print("^^")        
        
            return display_cctv_page(triggered_id['index'])
        else:
            print("4")
            return no_update
        
    
        
    
    

#첫번째 페이지 오른쪽
def display_gu_page(value):
    dong1 = db.select_stopline(value)
    data= go.Bar(x=dong1['dong_nm'],y=dong1['count'])
    flg = go.Figure(data=data)
    flg.update_layout(title='정지선 위반행위 발생순위',font=dict({'family':'LINESeedKR-Bd'}),paper_bgcolor='#F5F7FA'),
    flg.update_traces(marker_color='#6667AB', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5, opacity=0.8)
    
    dong2 = db.select_road(value)
    data2= go.Bar(x=dong2['dong_nm'],y=dong2['count'])
    flg2 = go.Figure(data=data2)
    flg2.update_layout(title='보행자도로 주행 위반행위 발생순위',font=dict({'family':'LINESeedKR-Bd'}),paper_bgcolor='#F5F7FA'),
    flg2.update_traces(marker_color='#6667AB', marker_line_color='rgb(8,48,107)',
                  marker_line_width=1.5, opacity=0.8)



    return [
        graph_layout([1,value]),
        html.Br(),
        html.H2(children=[value+" 위반유형별 발생현황"],className='locationsub'),
    
        html.Div(id="none1",children=[dcc.Graph(id='dong-graph_stopline_top5',figure=flg)],className='dong-graph_stopline_top5'),
        html.Div(id="none2",children=[dcc.Graph(id='dong-graph_road_top5',figure=flg2)],className='dong-graph_road_top5')
    ]

#두번째 페이지 오른쪽
def display_dong_page(value):
    si,gun,gu = value.split()
    return [
        html.H2(children=[gun+" "+gu],className='gun_gu_text'),
        html.Br(),
        graph_layout([2,value])
    ]

#세번째 페이지 오른쪽(cctv누르면 바뀌는 그래프)
#세번째 페이지 오른쪽
def display_cctv_page(value):
    crime = ['정지선 위반', '보행자 도로 위반']
    
    data = db.select_cctv(value,crime[0])
    data1 = db.select_cctv(value,crime[1])
    df = pd.concat([data,data1],ignore_index=True)

    fig = px.pie(df, names='crime_type', 
             hole = 0.7,
             width=500,
             height=230,
             #title='범법행위 비율',
             color_discrete_sequence=['#4c78a8', '#72b7b2'])
    fig.update_layout(plot_bgcolor='#F5F7FA', font=dict({'family':'LINESeedKR-Bd'}),paper_bgcolor='#F5F7FA')


    #cctv 위치 정보
    location = db.select_cctv_location(value).loc[0]

    return [
        html.H2(children=[location['gu_nm']+" "+location['dong_nm']],className='gun_gu_text'),
        html.Div(id="pie",children=[dcc.Graph(id='pie',figure=fig)],className='pie'),
        graph_cctv_layout([3,value]),
        
    ]


# html.Ul(id='cctv_list', children = [
#                 html.Li(id='crime_list',children=[ 
#                                    i,
#                                    html.Ul(children=[
#                                            html.Li(j[3]) for j in data[data['type']==i].values.tolist()])
#                                     ]) for i in crime ]) 


#추이 그래프
@callback(
    Output("analytics", "figure"),
    [Input("display_figure", "value"),
    ],
)
def make_graph(value):
    value = json.loads(value)
    print(value) #ex)['일간통계',[1,value값]]

    if value[1][0] == 1: #구통계
        data1 = db.select_gu(value[1][1],"정지선 위반")
        if not data1.empty :
            data1['time'] = pd.to_datetime(data1['time'].dt.date)
        
        data2 = db.select_gu(value[1][1],"보행자 도로 위반")
        if not data2.empty:
            data2['time'] = pd.to_datetime(data2['time'].dt.date)
            
    elif value[1][0] ==2 : #동통계
        si,gu,dong = value[1][1].split()
        
        data1 = db.select_gu_dong(gu,dong,"정지선 위반")
        if not data1.empty :
            data1['time'] = pd.to_datetime(data1['time'].dt.date)
        
        data2 = db.select_gu_dong(gu,dong,"보행자 도로 위반")
        if not data2.empty :
            data2['time'] = pd.to_datetime(data2['time'].dt.date)
        
        
    if data1.empty and data2.empty:
        fig = go.Figure()
        fig.update_layout(
            xaxis= {
                "visible": False },
            yaxis= {
                "visible": False },
            annotations= [
                {
                "text": "No matching data found",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 25
                }
                }
            ],
            paper_bgcolor='#F5F7FA',
            plot_bgcolor='#F5F7FA'
        )
        print("1234")
        return fig    

    if '일간 통계' in value[0]:
        if not data1.empty :
            data1=data1.groupby('time').sum()
            data1 = data1.reset_index(drop=False)
        if not data2.empty:
            data2=data2.groupby('time').sum()
            data2 = data2.reset_index(drop=False)
        fig = go.Figure(go.Scatter(x=data1['time'], y=data1['crime_cnt'],
                mode='lines+markers', name='정지선 위반'))
        fig.add_traces(go.Scatter(x=data2['time'], y=data2['crime_cnt'],
                mode='lines+markers', name='보행자 도로 위반'))
        fig.update_layout(template='seaborn',paper_bgcolor='#F5F7FA')
        

    
    if '주간 통계' in value[0]:
        if not data1.empty :
            data1 = data1.resample(rule='1W', on='time').sum()
            data1 = data1.reset_index(drop=False)
        if not data2.empty:
            data2 = data2.resample(rule='1W', on='time').sum()        
            data2 = data2.reset_index(drop=False)

        fig = go.Figure(go.Scatter(x=data1['time'], y=data1['crime_cnt'],
                mode='lines+markers', name='정지선 위반'))
        fig.add_traces(go.Scatter(x=data2['time'], y=data2['crime_cnt'],
                mode='lines+markers', name='보행자 도로 위반'))
        fig.update_layout(template='seaborn',paper_bgcolor='#F5F7FA')

    if '월간 통계' in value[0]:
        if not data1.empty:
            data1 = data1.resample(rule='1M', on='time').sum()
            data1 = data1.reset_index(drop=False)
            
        
        if not data2.empty:
            data2 = data2.resample(rule='1M', on='time').sum()
            data2 = data2.reset_index(drop=False)
            
        
        
        fig = go.Figure(go.Scatter(x=data1['time'], y=data1['crime_cnt'],
                mode='lines+markers', name='정지선 위반'))
        fig.add_traces(go.Scatter(x=data2['time'], y=data2['crime_cnt'],
                mode='lines+markers', name='보행자 도로 위반'))
        fig.update_layout(template='seaborn',paper_bgcolor='#F5F7FA')

    
    
    
    # Aesthetics
    fig.update_layout(margin= {'t':50, 'b':0, 'r': 0, 'l': 0, 'pad': 0})
    #fig.update_layout(hovermode = 'x')
    #fig.update_layout(showlegend=True, legend=dict(x=1,y=0.85))
    fig.update_layout(uirevision='constant')
    fig.update_layout(title='<b>범법행위 발생 추이',font=dict({'family':'LINESeedKR-Bd'}),)
    fig.update_layout(paper_bgcolor='#F5F7FA')

    return(fig)




def graph_layout(value):
    
    controls = html.Div(
    children=[
        dbc.Card(
            [dbc.Col(
                    [
                        #dbc.Label("Options"),
                        dcc.RadioItems(id="display_figure", 
                        options=[
                                {'label': '일간 통계', 'value': json.dumps(['일간 통계',value])},
                                {'label': '주간 통계', 'value': json.dumps(['주간 통계',value])},
                                {'label': '월간 통계', 'value': json.dumps(['월간 통계',value])}
                            ],
                        value=json.dumps(['일간 통계',value]),
                        labelStyle={'display': 'inline-block', 'width': '10em', 'line-height':'0.5em'}
                        ) 
                    ], 
                ),
                dbc.Col(
                    [dbc.Label(""),]
                ),
            ],
            body=True,
            style = {'font-size': 'large'}),],
            className='controls',
    )
    return html.Div(
        children=[
            dbc.Container([
                html.H2("범법행위 발생 추이",className='graph_title'),
            html.Hr(),
            dbc.Row([
                dbc.Col([controls],xs = 4), #여기서 xs가 뭐지?
                dbc.Col([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id="analytics")),
                    ])
                ]),
            ]),
            html.Br(),
            dbc.Row([
    
            ]), 
        ],
        fluid=True,className='dong-graph')
        
    ],
    className='container_dong',)
    #동 누르면 나오는 그래프
    

@callback(
    Output("cctv_analytics", "figure"),
    [Input("display_cctv_figure", "value"),
    ],
)
def make_cctv_graph(value):
    value = json.loads(value)
    data1 = db.select_cctv(value[1][1],"정지선 위반")
    data2 = db.select_cctv(value[1][1],"보행자 도로 위반")

    if data1.empty and data2.empty:
        fig = go.Figure()
        fig.update_layout(
            xaxis= {
                "visible": False },
            yaxis= {
                "visible": False },
            annotations= [
                {
                "text": "No matching data found",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 25
                }
                }
            ],
            paper_bgcolor='#F5F7FA',
            plot_bgcolor='#F5F7FA'
        )
        print("1234")
        return fig

    if not data1.empty :
        data1['time'] = pd.to_datetime(data1['time'].dt.date)
        
    
    if not data2.empty:
        data2['time'] = pd.to_datetime(data2['time'].dt.date)

    print("#####")
        
        
    if '주간 통계' in value[0]:
        if not data1.empty :
            data1 = data1.resample(rule='1W', on='time').sum()
            data1 = data1.reset_index(drop=False)
        if not data2.empty:
            data2 = data2.resample(rule='1W', on='time').sum()        
            data2 = data2.reset_index(drop=False)
            
        fig = go.Figure(go.Scatter(x=data1['time'], y=data1['crime_cnt'],
                mode='lines+markers', name='정지선 위반'))
        fig.add_traces(go.Scatter(x=data2['time'], y=data2['crime_cnt'],
                mode='lines+markers', name='보행자 도로 위반'))
        fig.update_layout(template='seaborn')
        
    fig.update_layout(margin= {'t':50, 'b':0, 'r': 0, 'l': 0, 'pad': 0})
    fig.update_layout(uirevision='constant')
    fig.update_layout(title='<b>범법행위 발생 추이',font=dict({'family':'LINESeedKR-Bd'}),)
    fig.update_layout(template='seaborn',paper_bgcolor='#F5F7FA')
    
    return(fig)
    
    
def graph_cctv_layout(value):
    
    controls = html.Div(
    children=[
        dbc.Card(
            [dbc.Col(
                    [
                        #dbc.Label("Options"),
                        dcc.RadioItems(id="display_cctv_figure", 
                        value=json.dumps(['주간 통계',value]),
                        labelStyle={'display': 'inline-block', 'width': '10em', 'line-height':'0.5em'}
                        ) 
                    ], 
                ),
                dbc.Col(
                    [dbc.Label(""),]
                ),
            ],
            body=True,
            style = {'font-size': 'large'}),],
            className='controls',
    )
    return html.Div(
        children=[
            dbc.Container([
                html.H2("범법행위 발생 추이",className='graph_title'),
            html.Hr(),
            dbc.Row([
                dbc.Col([controls],xs = 4), 
                dbc.Col([
                    dbc.Row([
                        dbc.Col(dcc.Graph(id="cctv_analytics")),
                        #cctv 누르면 나오는 그래프
                    ])
                ]),
            ]),
            html.Br(),
            dbc.Row([
    
            ]), 
        ],
        fluid=True)
    ],className='container_cctv',
    )
    
    





if __name__ == '__main__':
    app.run_server(debug=True)