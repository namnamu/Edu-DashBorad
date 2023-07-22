from dash import Dash, dcc, html, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


app = Dash(__name__)

# 데이터 선언 함수
def inputdata(filename):
    df=pd.read_excel(filename) #파일 읽어오기
    #데이터 전처리
    df=df.groupby(['행정구역별','시점']).agg({'매우만족':'sum','약간만족':'sum','보통':'sum','약간불만족':'sum','매우불만족':'sum'}).reset_index()

    return df

# 데이터프레임 선언(변수명 df)
df=inputdata('17개 시도별 학생의 학교생활만족도 & 교원 1인당 학생수.xlsx')
# 조회할 데이터.(컬럼 명으로 초기화한다.)
slider_option='시점'
dropdown_option='행정구역별'

# 화면 구성.
app.layout = html.Div([
    # 슬라이더
    html.Div(
        dcc.Slider( 
            df[slider_option].min(), # 최소 숫자부터
            df[slider_option].max(), # 최대 숫자까지
            step=None, # 건너뛸 정도
            id='crossfilter-year--slider',
            value=df[slider_option].max(), # 초기 값
            marks={str(year): str(year) for year in df[slider_option].unique()} # 년도를 표기하기 위한 마커
        ), style={'width': '49%', 'padding': '0px 20px 20px 20px'}),
    # 드롭다운
    html.Div(
        dcc.Dropdown(
            id='crossfilter-loc--dropdown',
            options=df[dropdown_option].unique(), # 해당 컬럼의 종류
            value=df[dropdown_option].unique()[0], # 초기 값
            clearable=False
        ), style={'width': '49%', 'padding': '0px 20px 20px 20px'}),
    # 그래프
    html.Div(
        dcc.Graph(
            id='graph-with-slider'
        ),style={'width': '50%', 'padding': '0px 20px 20px 20px'}),
    # 조건 확인(아직 안됨.)
    # html.Div(
    #     dash_table.DataTable(df.to_dict('records'),[{'매우만족':df.iloc[0, 2],'약간만족':df.iloc[0, 3],'보통':df.iloc[0, 4],'약간불만족':df.iloc[0, 5],'매우불만족':df.iloc[0, 6]} ])
    # )
])

# 조건 이벤트
@callback(
    Output('graph-with-slider', 'figure'),
    Input(component_id='crossfilter-year--slider', component_property='value'),
    Input(component_id='crossfilter-loc--dropdown', component_property='value'))
def update_figure(slider_data,dropdown_data): #콜백에서 들어올 input데이터 순서대로
    df=inputdata('17개 시도별 학생의 학교생활만족도 & 교원 1인당 학생수.xlsx') # 옵션들은 들고 들어오면서 df는 왜 못 가져오지?
    # -> 병합시 통째로 함수형으로 만들거나, 클래스로 묶어버려야할 것 같다. 
    
    # 조건 검색 기능
    df=df[df[slider_option].apply(lambda x: True if x==slider_data else False)]
    df=df[df[dropdown_option].apply(lambda x: True if x==dropdown_data else False)]
    
    labels = df.columns[2:] # 컬럼명
    values = list(df.iloc[0,2:]) #각 해당하는 값(직접 명시된 %)
    
    # 그래프 초기화
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig.update_layout(transition_duration=500)
    # output전달
    return fig


if __name__ == '__main__':
    app.run(debug=True)