# Copyright 2020 University of New South Wales, University of Sydney, Ingham Institute

# Licensed under the MIT Licence;
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from styles import CARD
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.offline import plot


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

hnscc_csv = "../data/hnscc.csv"

df = pd.read_csv(hnscc_csv)

header = html.Div([
        html.Div([
            html.H1(children='Data Visualisation of Ingham Head and Neck Cancer dataset',
                    style = {'textAlign' : 'center', 'font-family' : 'Arial'}
            ),
            html.Br([]),
            ],
            style = {'padding-top' : '2%'}
        )],
        style = {'height' : '10%',
                'background-color' : '#6092cd'},      

)

def average_follow_up_duration_by_site(dataframe):
    average_follow_up_grouped_by_site = dataframe.groupby('Site')["Follow up duration (day)"].mean()
    fig = px.bar(average_follow_up_grouped_by_site, x="Follow up duration (day)", title="Average Follow Up Duration By Site", orientation='h')
    fig.update_layout(title_x=0.5)

    return dcc.Graph(
    	id='average-follow-up-duration-by-site',
		figure=fig
    )

def survival_by_age(dataframe):
    fig = px.scatter(dataframe, x="Age", y="Survival  (months)", title="Survival of months by Age of Patient", color="Alive or Dead")
    fig.update_layout(title_x=0.5)
    return dcc.Graph(
        id='age-by-cancer-grade',
        figure=fig)

def survival_by_stage(dataframe):
    df_stage_sensor = dataframe.groupby(['Stage', 'Overall Survival Censor']).size()
    df_stage_sensor = df_stage_sensor.to_frame(name='occurance').reset_index()
    occ = df_stage_sensor.loc[:,'occurance']
    fig = make_subplots(rows=1, cols=5, specs=[[{"type": "pie"}, {"type": "pie"},{"type": "pie"}, {"type": "pie"}, {"type": "pie"}]])

    fig.add_trace(go.Pie(
        values=occ[:1],
        labels=["death"],
        domain=dict(x=[0, 0.2]),
        name="Stage I",
        title="Stage I"), 
        row=1, col=1)

    fig.add_trace(go.Pie(
        values=occ[1:3],
        labels=["survival", "death"],
        domain=dict(x=[0.2, 0.4]),
        name="Stage II",
        title="Stage II",
        marker_colors=['lightskyblue','crimson']),
        row=1, col=2)

    fig.add_trace(go.Pie(
        values=occ[3:5],
        labels=["survival", "death"],
        domain=dict(x=[0, 0.5]),
        name="Stage III",
        title="Stage III",
        marker_colors=['lightskyblue','crimson']), 
        row=1, col=3)

    fig.add_trace(go.Pie(
        values=occ[5:7],
        labels=["survival", "death"],
        domain=dict(x=[0.5, 1.0]),
        name="Stage IVA",
        title="Stage IVA",
        marker_colors=['lightskyblue','crimson']),
        row=1, col=4)

    fig.add_trace(go.Pie(
        values=occ[7:9],
        labels=["survival", "death"],
        domain=dict(x=[0.5, 1.0]),
        name="Stage IVB",
        title="Stage IVB",
        marker_colors=['lightskyblue','crimson']),
        row=1, col=5)

    fig.update_traces(hole=.4, hoverinfo="label+percent+name")
    fig.update(layout_title_text='Overall survival rate based on the Stage', layout_title_x = 0.49)

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))

    return dcc.Graph(id='stage-sur-graph', figure=fig)

def age_filter(dataframe):
    df_sex_sur = dataframe.groupby(['Sex', 'Overall Survival Censor']).size()
    df_sex_sur = df_sex_sur.to_frame(name='occurance').reset_index()

    df_sex_stage = df.groupby(['Sex', 'Stage']).size()
    df_sex_stage = df_sex_stage.to_frame(name='occurance').reset_index()

    df_sex_site = df.groupby(['Sex', 'Site']).size()
    df_sex_site = df_sex_site.to_frame(name='occurance').reset_index()

    df_sex_rec = df.groupby(['Sex', 'Site of recurrence (Distal/Local/ Locoregional)']).size()
    df_sex_rec = df_sex_rec.to_frame(name='occurance').reset_index()

    gender_by_survival = html.Div(className="row", children=[
        html.Div(className="col-sm-3", children=[
            html.P("Gender:", 
                style={'margin-left':'40px','margin-top':'40px'}),
            dcc.Dropdown(
                id='gender', 
                value='Male', 
                options=[{'label': x, 'value': x} for x in df_sex_sur['Sex'].unique()],
                clearable=False,
                style={'margin-left':'30px','margin-top':'10px'}
            ),
            html.P("Diagnostic information:",
                style={'margin-left':'40px','margin-top':'80px'}),
            dcc.Dropdown(
                id='survival', 
                value='Overall Survival Censor', 
                options=[{'value': x, 'label': x} 
                        for x in ['Overall Survival Censor', 'Stage', 'Site of diagnosis', 'Site of recurrence']],
                clearable=False,
                style={'margin-left':'30px','margin-top':'10px'}
            )
        ]),
        html.Div(className="col-lg", children=[
            dcc.Graph(id="pie-chart")
        ])
    ])

    @app.callback(
        Output("pie-chart", "figure"), 
        [Input("gender", "value"), 
        Input("survival", "value")])

    def generate_chart(gender, survival):
        if survival == 'Overall Survival Censor':
            array = df_sex_sur['occurance'].loc[(df_sex_sur['Sex'] == gender)]
            fig = px.pie(df_sex_sur, values=array, labels=df_sex_site.index,
                        names=["survival", "death"])
        elif survival == 'Stage':
            array = df_sex_stage['occurance'].loc[(df_sex_stage['Sex'] == gender)]
            fig = px.pie(df_sex_stage, values=array, labels=df_sex_site.index, 
                        names=["Stage I", "Stage II", "Stage III", "Stage IVA", "Stage IVB"])
        elif survival == 'Site of diagnosis':
            array = df_sex_site['occurance'].loc[(df_sex_site['Sex'] == gender)]
            if gender == 'Female':
                fig = px.pie(df_sex_site, values=array, labels=df_sex_site.index,
                        names=["Glottis", "Hypopharynx", "Nasopharynx", "Oral cavity", "Oropharynx"])
            elif gender == 'Male':
                fig = px.pie(df_sex_site, values=array, labels=df_sex_site.index,
                        names=["CUP", "Glottis", "Hypopharynx", "Nasopharynx", "Oral cavity", "Oropharynx", "Sinus"])
        elif survival == 'Site of recurrence':
            array = df_sex_rec['occurance'].loc[(df_sex_rec['Sex'] == gender)]
            if gender == 'Female':
                fig = px.pie(df_sex_rec, values=array, 
                        names=["Complete response", "Distant metastasis", "Local recurrence", "Regional recurrence", "Residual tumor"])
            elif gender == 'Male':
                fig = px.pie(df_sex_rec, values=array, labels=df_sex_rec.index, 
                        names=["Complete response", "Distant metastasis", "Local recurrence", "Local recurrence and distant metastasis",
                        "Locoregional and distant metastasis", "Locoregional recurrence", "Regional and distant metastasis",
                        "Regional recurrence", "Regional recurrence and distant metasatsis","Residual tumor"])
        
        fig.update_layout(title=f"{survival} by {gender}", legend_traceorder="normal")
        return fig

    return gender_by_survival

def causation_of_death(dataframe):
    df_dead = dataframe.loc[(df['Alive or Dead']) == "Dead"]
    df_dead = df_dead[['Cause of Death']]
    df_dead = df_dead.groupby(['Cause of Death']).size()
    df_dead = df_dead.to_frame(name='occurance').reset_index()
    df_dead.at[2,'occurance'] = 9
    df_dead = df_dead.drop([3], axis=0)

    fig = px.bar(df_dead, x='Cause of Death', y='occurance', height=450)
    fig.update(layout_title_text="Causation of Death", layout_title_x = 0.49)
    fig.update_traces(width=0.4)
    return dcc.Graph(id='death-causation-graph', figure=fig)


def age_RT_distribution(dataframe):
    fig = px.scatter(dataframe, x="Age", y="Total RT treatment time (days)", 
                                title="Age Distribution of Total RT treatment time (days)", 
                                color="Sex",
                                log_x=True)
    fig.update_layout(title_x=0.5)

    age_RT = html.Div([
        dcc.Graph(id='age-RT-distribution', figure=fig),
        html.P("Age Range Slider:"),
        dcc.RangeSlider(
            id='range-slider',
            min=20, max=95, step=0.1,
            marks={20: '20', 95: '95'},
            value=[20, 95]),
    ])

    @app.callback(
    Output("age-RT-distribution", "figure"), 
    [Input("range-slider", "value")])

    def update_bar_chart(slider_range):
        low, high = slider_range
        mask = (dataframe['Age'] > low) & (dataframe['Age'] < high)
        fig = px.scatter(
            dataframe[mask], x="Age", y="Total RT treatment time (days)", 
            color="Sex", size='Total RT treatment time (days)', 
            title="Age Distribution of Total RT treatment time (days)",
            hover_data=['Age'])
        fig.update_layout(title_x=0.5)
        return fig

    return age_RT


def Receive_Concurrent_Chemoradiotherapy(dataframe):
    df_concurrent = dataframe.groupby(['Sex', 'Received Concurrent Chemoradiotherapy?']).size() 	
    df_concurrent = df_concurrent.to_frame(name='occurance').reset_index()
    
    occ = df_concurrent.loc[:,'occurance']
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])

    fig.add_trace(go.Pie(
        values=occ[:2],
        labels=["No","YES"],
        domain=dict(x=[0, 0.2]),
        name="Female",
        title="Female",
        marker_colors=['crimson','lightskyblue']), 
        row=1, col=1)

    fig.add_trace(go.Pie(
        values=occ[2:4],
        labels=["No","YES"],
        domain=dict(x=[0.2, 0.4]),
        name="Male",
        title="Male",
        marker_colors=['crimson','lightskyblue']),
        row=1, col=2)

    fig.update_traces(hole=.4, hoverinfo="label+percent+name")
    fig.update(layout_title_text='Received Concurrent Chemoradiotherapy ratio by Gender', layout_title_x = 0.49)

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))

    return dcc.Graph(id='concurrent-gender', figure=fig)

def BMI_difference(dataframe):
    df['difference']=df['BMI start treat (kg/m2)']-df['BMI stop treat (kg/m2)']
    diff_BMI = df[['Age','Sex','difference']]

    fig = px.scatter(df, x="Age", y="difference", 
                                title="The difference in BMI before and after treatment (>0 means an increase in BMI)", 
                                color="Sex",
                                log_x=True)
    fig.update_layout(title_x=0.5)

    bmi_diff = html.Div([
        dcc.Graph(id='bmi-difference', figure=fig),
        html.P("Age Range Slider:"),
        dcc.RangeSlider(
            id='range-slider1',
            min=20, max=95, step=0.1,
            marks={20: '20', 95: '95'},
            value=[20, 95]),
    ])

    @app.callback(
    Output("bmi-difference", "figure"), 
    [Input("range-slider1", "value")])

    def update_bar_chart(slider_range):
        low, high = slider_range
        mask = (diff_BMI['Age'] > low) & (diff_BMI['Age'] < high)
        fig = px.scatter(
            diff_BMI[mask], x="Age", y="difference", 
            color="Sex",
            hover_data=['Age'],
            title="The difference in BMI before and after treatment (>0 means an increase in BMI)")
        fig.update_layout(title_x=0.5)
        return fig

    return bmi_diff
    
app.layout = html.Div(children=[
    header,
    html.Div(className="container", children=[
        html.Div(className="row", children=[
            html.Div([
                survival_by_stage(df)
            ], className="col-lg", style=CARD)
        ]),
        html.Div(className="row", children=[
            html.Div([
                survival_by_age(df)
            ], className="col-lg", style=CARD)
        ]),
        html.Div(className="row", children=[
            html.Div([
                average_follow_up_duration_by_site(df)
            ], className="col-sm", style=CARD),
            html.Div([
                causation_of_death(df)
            ], className="col-sm", style=CARD)
        ]),
        html.Div(className="row", children=[
            html.Div([
                age_filter(df)
            ], className="col-sm", style=CARD)
        ]),
        html.Div(className="row", children=[
            html.Div([
                age_RT_distribution(df)
            ], className="col-lg", style=CARD)
        ]),
        html.Div(className="row", children=[
            html.Div([
                Receive_Concurrent_Chemoradiotherapy(df)
            ], className="col-lg", style=CARD)
        ]),
        html.Div(className="row", children=[
            html.Div([
                BMI_difference(df)
            ], className="col-lg", style=CARD)
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
