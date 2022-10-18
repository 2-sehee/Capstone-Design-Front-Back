from dash import Dash, html, dcc, Input, Output, callback
import dash
import plotly.express as px
import pandas as pd
import dash_defer_js_import as dji
import dash_leaflet as dls
import json


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = Dash(__name__,suppress_callback_exceptions=True)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options


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



app.layout = html.Div([
    
    
    
    # represents the browser address bar and doesn't render anything
    dcc.Location(id='url', refresh=False),
    
    # content will be rendered in this element
    html.Div(id='page-content'),
    #html.Div(id="hidden_div_for_redirect_callback")

])


#style= {'display': 'block'}

# @callback(Output('page-content', 'children'),
#               [Input('url', 'pathname')])
def display_page(pathname):
     return html.Div([
         html.H3(f'You are on page {pathname}')
     ]) 
    
  
index_page = html.Div([
    dcc.Graph(id='graph',figure=fig),
    html.Div(id='index'),
    print("index")
])

def analytics_page(location):
    return html.Div([
            html.Div(id = "second_page"),
            html.H3(f'You click {location}')
    ])

    
@callback(
    Output('url', 'pathname'),
    Input('graph', 'clickData'), prevent_initial_call=True)
def move_page(clickData):
    print(clickData)
    if clickData is not None:            
        location = clickData['points'][0]['location']
        return "/"+location
        #dcc.Link(herf="/"+location,style= {'display': 'block'})
    else : return "/"
    


@callback(Output('page-content', 'children'),
               [Input('url', 'pathname')],prevent_initial_call=True)
def display_page(pathname):
    for city in df['SIG_KOR_NM']:
        if pathname == '/'+city:
            return analytics_page(city)
    print("display")
    return  index_page



if __name__ == '__main__':
    app.run_server(debug=True)