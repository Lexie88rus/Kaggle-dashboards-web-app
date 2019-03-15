import sys
import json
import plotly
import pandas as pd

from flask import Flask
from flask import render_template, request, jsonify
import plotly.graph_objs as go
from sklearn.externals import joblib
from sqlalchemy import create_engine

from datetime import date, timedelta

app = Flask(__name__)

def enabled_week_to_cumulative_count(weekly_competitions, date):
    '''
    Returns cumulative count of competitions enabled at a date
    '''
    return weekly_competitions[weekly_competitions['EnabledWeek'] <= date]['Count'].sum()

def creation_week_to_cumulative_count(weekly_datasets, date):
    '''
    Returns cumulative count of datasets created at a date
    '''
    return weekly_datasets[weekly_datasets['CreationWeek'] <= date]['Count'].sum()

# load data
print("Loading data \n")

engine = create_engine('sqlite:///../data/database.db')
kernels = pd.read_sql_table('Kernels', engine)
competitions = pd.read_sql_table('Competitions', engine)
users = pd.read_sql_table('Users', engine)
teams = pd.read_sql_table('Teams', engine)
submissions = pd.read_sql_table('Submissions', engine)
datasets = pd.read_sql_table('Datasets', engine)
discussions = pd.read_sql_table('Discussions', engine)

# index webpage displays dashboards
@app.route('/')
@app.route('/index')
def index():
    
    # extract data needed for visuals
    
    print("Creating visuals \n")
    
    competitions['Count'] = 1
    weekly_competitions = competitions.groupby('EnabledWeek')[['Count']].sum()
    weekly_competitions.reset_index(level=0, inplace=True)
    weekly_competitions['CumulativeCount'] = [enabled_week_to_cumulative_count(weekly_competitions, d) for d in weekly_competitions['EnabledWeek']]
    weekly_competitions = weekly_competitions.sort_values(by='EnabledWeek', ascending=True)
    weekly_competitions = weekly_competitions[weekly_competitions['EnabledWeek'] >= date(2015,1,1)]
    
    datasets['Count'] = 1
    weekly_datasets = datasets.groupby('CreationWeek')[['Count']].sum()
    weekly_datasets.reset_index(level=0, inplace=True)
    weekly_datasets['CumulativeCount'] = [creation_week_to_cumulative_count(weekly_datasets, d) for d in weekly_datasets['CreationWeek']]
    weekly_datasets = weekly_datasets.sort_values(by='CreationWeek', ascending=True)
    weekly_datasets = weekly_datasets[weekly_datasets['CreationWeek'] >= date(2015,1,1)]
    
    submissions['Count'] = 1
    weekly_submissions = submissions.groupby('SubmissionWeek')[['Count']].sum()
    weekly_submissions.reset_index(level=0, inplace=True)
    
    
    kernels['Count'] = 1
    weekly_kernels = kernels.groupby('CreationWeek')[['Count']].sum()
    weekly_kernels.reset_index(level=0, inplace=True)
    weekly_kernels = weekly_kernels.sort_values(by='CreationWeek', ascending=True)
    weekly_kernels = weekly_kernels[weekly_kernels['CreationWeek'] >= date(2015,1,1)]
    
    users['Count'] = 1
    weekly_users = users.groupby('RegisterWeek')[['Count']].sum()
    weekly_users.reset_index(level=0, inplace=True)
    weekly_users = weekly_users.sort_values(by='RegisterWeek', ascending=True)
    weekly_users = weekly_users[weekly_users['RegisterWeek'] >= date(2015,1,1)]
    
    heatmap_data = submissions.groupby(['SubmissionYear', 'SubmissionMonth']).size().reset_index()
    heatmap_data.columns = ['SubmissionYear', 'SubmissionMonth', 'Submissions']
    heatmap = []
    for year in heatmap_data.SubmissionYear.unique():
        row = []
        for month in range(1, 13):
            try:
                row.append(heatmap_data[(heatmap_data['SubmissionYear'] == year) & (heatmap_data['SubmissionMonth'] == month)]['Submissions'].values[0])
            except:
                row.append(0)   
        heatmap.append(row)
    
    # create visuals
    
    #plot 1: Cumulative count of competitions and datasets
    data1 = [
    #competitions
    go.Scatter(
            x=[pd.Timestamp(d).date() for d in weekly_competitions.EnabledWeek.values],
            y=weekly_competitions.CumulativeCount.values,
            mode='lines',
            name='Competitions',
            line=dict(width=4, color='#68B6AF')),
    
    #datasets
    go.Scatter(
            x=[pd.Timestamp(d).date() for d in weekly_datasets.CreationWeek.values],
            y=weekly_datasets.CumulativeCount.values,
            mode='lines',
            name='Datasets',
            line=dict(width=4, color='#82C5A0')),
    ]

    layout1 = go.Layout(
            title='Overall number of Kaggle activities over time',
            xaxis=dict(title='WeekStart', ticklen=5, zeroline=False, gridwidth=2),
            yaxis=dict(title='Total number of activities', ticklen=5, gridwidth=2),
            showlegend=True,
            #paper_bgcolor='rgb(254, 247, 234)',
            #plot_bgcolor='rgb(254, 247, 234)',
            )
    
    #plot 2: Count of submissions per week
    data2 = [
    #submissions
    go.Scatter(
        x=[pd.Timestamp(d).date() for d in weekly_submissions.SubmissionWeek.values],
        y=weekly_submissions.Count.values,
        mode='lines',
        name='Submissions',
        line=dict(width=4, color='#68B6AF')
    )]

    layout2 = go.Layout(
            title='Submissions per week',
            xaxis=dict(title='WeekStart', ticklen=5, zeroline=False, gridwidth=2),
            yaxis=dict(title='Number of submissions', ticklen=5, gridwidth=2),
            showlegend=False,
    )
    
    #plot 3: Weekly count of new kernels and users
    data3 = [
    #kernels
    go.Scatter(
        x=[pd.Timestamp(d).date() for d in weekly_kernels.CreationWeek.values],
        y=weekly_kernels.Count.values,
        mode='lines',
        name='Kernels',
        line=dict(width=4, color='#68B6AF')
    ),
    #users
    go.Scatter(
        x=weekly_users.RegisterWeek.values,
        y=weekly_users.Count.values,
        mode='lines',
        name='Users',
        line=dict(width=4, color='#FFD1F0')
    )]

    layout3 = go.Layout(
            title='Kernels per week',
            xaxis=dict(title='WeekStart', ticklen=5, zeroline=False, gridwidth=2),
            yaxis=dict(title='Number of new kernels', ticklen=5, gridwidth=2),
            showlegend=False,
    )
    
    #plot 4: Submissions heatmap
    trace = go.Heatmap(z=heatmap,
                   y=[2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019],
                   x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    data4=[trace]
    layout4 = dict(
            title='Submissions Heatmap',
            xaxis=dict(title='Month'),
            yaxis=dict(title='Year')
            )
    
    fig1 = go.Figure(data=data1, layout=layout1)
    fig2 = go.Figure(data=data2, layout=layout2)
    fig3 = go.Figure(data=data3, layout=layout3)
    fig4 = go.Figure(data=data4, layout=layout4)
    
    graphs = []
    graphs.append(fig1)
    graphs.append(fig2)
    graphs.append(fig3)
    graphs.append(fig4)
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)

def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


if __name__ == '__main__':
    main()