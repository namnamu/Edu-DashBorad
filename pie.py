from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def inputdata(filename):
    df=pd.read_excel(filename)
    df=df.groupby(['행정구역별','시점']).agg({'매우만족':'sum','약간만족':'sum','보통':'sum','약간불만족':'sum','매우불만족':'sum'}).reset_index()
    return df


app = Dash(__name__)


filename='17개 시도별 학생의 학교생활만족도 & 교원 1인당 학생수.xlsx'
pie_df=inputdata(filename)
df = pd.read_excel(filename)# line에서 사용할 df


slider_option='시점'
dropdown_option = '행정구역별'
a = '시점'
b = '재적학생수'
c = '교원수'
z='만족도환산점수'

# 화면 구성 요소
satis_line=html.Div([
    html.H2(children='연도별 만족도', style={'textAlign':'center'}),
    # 드롭다운
    html.Div(
        dcc.Dropdown(
            id='dropdown-selection-pie',
            options=pie_df[dropdown_option].unique(),
            value='전국', clearable=False
        )),
    # 라인 그래프
    dcc.Graph(id='graph-content-satis_line') #데코레이터에서 사용함
],style={'width': '30%', 'padding': '0px 20px 20px 20px','display':'inline-block'})

pie = html.Div([
    html.H2(children="만족도 ",style={'textAlign':'center'}),
    # 그래프
    html.Div(
        dcc.Graph(
            id='graph-with-slider'
        )
    ),
    # 슬라이더
    html.Div(
        dcc.Slider(  
            pie_df[slider_option].min(),
            pie_df[slider_option].max(),
            step=None,
            id='crossfilter-year--slider',
            value=pie_df[slider_option].max(),
            marks={str(year): str(year) for year in pie_df[slider_option].unique()} # 년도를 표기하기 위한 마커
        )
    )
],style={'width': '30%','display':'inline-block','padding': '0px 20px 20px 20px'})

line = html.Div([
    html.H2(children='연도별 학생수와 교원수', style={'textAlign': 'center'}),
    html.Div(
        dcc.Dropdown(
            id='dropdown-selection-line',
            options=pie_df[dropdown_option].unique(),
            value='전국', clearable=False
        )),
    dcc.Graph(id='graph-content'),

],style={'width': '30%', 'padding': '0px 20px 20px 20px','display':'inline-block'})



# 화면 구성
app.layout=html.Div([
    satis_line,
    pie,
    line,
],style={'text-align' : 'center'})

# 만족도 라인 이벤트 
@callback( 
    Output('graph-content-satis_line', 'figure'), 
    Input('dropdown-selection-pie', 'value') 
)
def update_bar_graph(value):
    dff = df[df[dropdown_option]==value]
    
    fig=go.Figure()
    
    fig.add_trace(go.Scatter(name=z,x=dff[a],y=dff[z]))

    fig.update_layout(barmode='group')
    return fig

# 파이 이벤트 
@callback(
    Output('graph-with-slider', 'figure'),
    Input(component_id='crossfilter-year--slider', component_property='value'),
    Input(component_id='dropdown-selection-pie', component_property='value'))
def update_figure(slider_data,dropdown_data):
    pie_df=inputdata(filename)
    # 조건 마스킹
    pie_df=pie_df[pie_df[slider_option].apply(lambda x: True if x==slider_data else False)]
    pie_df=pie_df[pie_df[dropdown_option].apply(lambda x: True if x==dropdown_data else False)]
    # 라벨과 값
    labels = pie_df.columns[2:]
    values = list(pie_df.iloc[0,2:])

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_layout(transition_duration=500)
    return fig

# 사람 수 라인 이벤트
@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection-line', 'value'),
)
def update_graph(value):
    dff = df[df[dropdown_option] == value]

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=dff[a], y=dff[b], name='학생수', mode='lines+markers', yaxis='y1'))
    fig.add_trace(go.Scatter(x=dff[a], y=dff[c], name='교원수', mode='lines+markers', yaxis='y2'))

    fig.update_layout(
        xaxis_title='연도',
        yaxis_title='재적학생수',
        yaxis2=dict(
            title='교원수',
            overlaying='y',
            side='right'
        )
    )

    return fig


if __name__ == '__main__':
    app.run(debug=True)