from dash import html, dcc, Dash, Input, Output, callback
import dash
import json
import plotly.express as px
import pandas as pd

dash.register_page(__name__, path='/')


#임시데이터
df = pd.DataFrame({
    "SIG_KOR_NM": ["광진구","강동구","성동구","강남구","강서구","강북구","관악구","구로구","금천구","노원구","동대문구","도봉구","동작구","마포구","서대문구","성북구","서초구","송파구","영등포구","용산구","양천구","은평구","종로구","중구","중랑구"],
    "Amount": [1000,500,100,0,234,764,2436,764,34,87,12,76,235,764,124,7853,14,564,236,764,1348,536,234,546,5271]
})


#데이터 로드
geometry = json.load(open('./assets/TL_SCCO_SIG.json',encoding='utf-8'))

#Choropleth 시각화 -> 추후 SIG_KOR_NM column 을 누구나 알아볼 수 있게 바꿀예정(ex.city)
fig=px.choropleth(df,geojson=geometry,locations='SIG_KOR_NM',color='Amount',
                  color_continuous_scale='Blues',
                  featureidkey='properties.SIG_KOR_NM')
fig.update_geos(fitbounds="locations",visible=False)
fig.update_layout(title_text="example",title_font_size=20)


layout = html.Div(children=[

    dcc.Graph(
        id='graph',
        figure=fig
    )
    

])

@callback(
    Output(component_id='graph', component_property='figure'),
    Input(component_id='graph', component_property='clickData'))
def move_page(clickData):
    if clickData is not None:            
        location = clickData['points'][0]['location']
        
    print(clickData)
    return