#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 19:30:51 2019

@author: aleksandra deis

Script to get data for dashboards using Kaggle API:
https://github.com/Kaggle/kaggle-api

Data is saved into sqlite database (database path should be provided by the user
as a command line argument)
"""
#imports
import sys
import os
import pandas as pd
from sqlalchemy import create_engine
import datetime as dt
from datetime import date, timedelta

def load_data(kaggle_config_dir):
    '''
    Function loads data from Kaggle Meta dataset using Kaggle API
    INPUTS:
        1. kaggle_config_dir - directory, where Kaggle credentials kaggle.json are stored
    OUTPUTS:
        kernels, competitions, users, teams, submissions, datasets, discussions
        - pandas dataframes containing data loaded from Kaggle
    '''
    
    #download and unzip csv files using Kaggle API
    os.system('KAGGLE_CONFIG_DIR="{kaggle_config_dir}"'.format(kaggle_config_dir = kaggle_config_dir))
    os.system('kaggle datasets download kaggle/meta-kaggle')
    os.system('unzip -o meta-kaggle.zip')
    
    #set permissions to files
    os.system('chmod 644 Kernels.csv')
    os.system('chmod 644 Competitions.csv')
    os.system('chmod 644 Users.csv')
    os.system('chmod 644 Teams.csv')
    os.system('chmod 644 Submissions.csv')
    os.system('chmod 644 Datasets.csv')
    os.system('chmod 644 ForumMessages.csv')
    
    #load csv files into dataframes
    kernels = pd.read_csv('Kernels.csv')
    competitions = pd.read_csv('Competitions.csv')
    users = pd.read_csv('Users.csv')
    teams = pd.read_csv('Teams.csv')
    submissions = pd.read_csv('Submissions.csv')
    datasets = pd.read_csv('Datasets.csv')
    discussions = pd.read_csv('ForumMessages.csv')
    
    #return loaded datasets
    return kernels, competitions, users, teams, submissions, datasets, discussions

def date_to_first_day_of_week(day: date) -> date:
    '''
    Function to convert date to date of the first date of the week
    for corresponding date
    '''
    return day - timedelta(days=day.weekday())

def clean_data(kernels, competitions, users, teams, submissions, datasets, discussions):
    '''
    Cleaning and transformation of loaded data: adding new columns required for
    visualization
    INPUTS:
        1. kernels, competitions, users, teams, submissions, datasets, discussions
        - pandas dataframes to be processed and cleaned
    OUTPUTS:
        INPUTS:
        1. kernels, competitions, users, teams, submissions, datasets, discussions
        - cleaned pandas dataframes to be saved into database
    '''

    competitions['EnabledWeek'] = [date_to_first_day_of_week(pd.Timestamp(d).date()) for d in competitions['EnabledDate']]  
    datasets['CreationWeek'] = [date_to_first_day_of_week(pd.Timestamp(d).date()) for d in datasets['CreationDate']]
    
    kernels = kernels.dropna(subset=['CreationDate'])
    kernels['CreationWeek'] = [date_to_first_day_of_week(pd.Timestamp(d).date()) for d in kernels['CreationDate']]
    kernels['CreationDayOfWeek'] = [pd.Timestamp(d).dayofweek for d in kernels['CreationDate']]
    
    users['RegisterWeek'] = [date_to_first_day_of_week(pd.Timestamp(d).date()) for d in users['RegisterDate']]
    
    submissions['SubmissionWeek'] = [date_to_first_day_of_week(pd.Timestamp(d).date()) for d in submissions['SubmissionDate']]
    submissions['SubmissionYear'] = [pd.Timestamp(d).year for d in submissions['SubmissionDate']]
    submissions['SubmissionMonth'] = [pd.Timestamp(d).month for d in submissions['SubmissionDate']]
    submissions['SubmissionDayOfWeek'] = [pd.Timestamp(d).dayofweek for d in submissions['SubmissionDate']]
    
    return kernels, competitions, users, teams, submissions, datasets, discussions

def save_data(kernels, competitions, users, teams, submissions, datasets, discussions, database_filepath):
    '''
    Functions saves cleaned dataframe into sqlite database
    Rewrites data if the table already exists
    INPUTS:
        1. kernels, competitions, users, teams, submissions, datasets, discussions
        - cleaned pandas dataframes to be saved into database
        2. database_filename - database filename for the dataframe to be saved to
        
    OUTPUTS: none
    '''
    #establish connection to database
    conn_string = 'sqlite:///{database_filename}'.format(database_filename = database_filepath)
    engine = create_engine(conn_string)
    
    #save data to database
    kernels.to_sql('Kernels', engine, index=False, if_exists = 'replace')
    competitions.to_sql('Competitions', engine, index=False, if_exists = 'replace')
    users.to_sql('Users', engine, index=False, if_exists = 'replace')
    teams.to_sql('Teams', engine, index=False, if_exists = 'replace')
    submissions.to_sql('Submissions', engine, index=False, if_exists = 'replace')
    datasets.to_sql('Datasets', engine, index=False, if_exists = 'replace')
    discussions.to_sql('Discussions', engine, index=False, if_exists = 'replace')

def main():
    
    print(sys.argv)
    
    if len(sys.argv) == 3:
        kaggle_config_dir = sys.argv[1]
        database_filepath = sys.argv[2]

        print('Loading data...\n')
        kernels, competitions, users, teams, submissions, datasets, discussions = load_data(kaggle_config_dir)

        print('Cleaning data...\n')
        kernels, competitions, users, teams, submissions, datasets, discussions = clean_data(kernels, competitions, users, teams, submissions, datasets, discussions)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(kernels, competitions, users, teams, submissions, datasets, discussions, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepath of the kaggle config dir and database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              '/Users/username/kaggle '\
              'kaggle_dataset.db')


if __name__ == '__main__':
    main()

