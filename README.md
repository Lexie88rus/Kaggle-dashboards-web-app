# Kaggle dashboards web app
Web application containing dashboards for Kaggle activities

## Table of Contents
* [About the App](#about-the-app)
* [Repository Contents](#repository-contents)
* [Setup Instructions](#setup-instructions)
* [External Libraries](#external-libraries)

## About the App
Web app to view dashboards demonstrating Kaggle activities. Data for dashboards is collected automatically using [Kaggle API](https://github.com/Kaggle/kaggle-api).

Screenshot of the main page:
![Web-app main page](https://github.com/Lexie88rus/Kaggle-dashboards-web-app/blob/master/screenshots/main_page.png)

## Repository Contents
The repository has the following structure:
```
- app
| - templates
| |- master.html  # main page of web app
| - static
| |- githublogo.png  # github logo used in the main page
|- run.py  # Flask file that runs app

- data
|- process_data.py # script containing ETL for the initial dataset processing

- screenshots
|- main_page.png # screenshot of the main page

- README.md
```
More details on the most important repository files and scripts:
* process_data.py - script automatically downloads Kaggle meta dataset using Kaggle API and uploads preprocessed data
to SQLite database. Script takes path to Kaggle credentials token and path to resulting database file as parameters.

## Setup Instructions
Follow the instructions to run the web-app locally:
1. Install required external libraries (see the [External Libraries](#external-libraries) section below).
2. Clone the repository.
3. Navigate to the repository's root directory.
4. Run the following commands in the repository's root directory to set up database and model.

    - Run ETL pipeline that cleans data and stores in database
        <br>`$ python data/process_data.py /Users/username/kaggle dataset.db`

5. Navigate to `app` folder.
6. Run the following command in the app's directory to run the web app:
    <br>`$ python run.py`

4. Open http://0.0.0.0:3001/ in web browser.

## External Libraries
The following external libraries should be installed in order to run the app:
1. [SQLAlchemy](https://www.sqlalchemy.org) to store the preprocessed data,
2. [Plot.ly](https://plot.ly/) library for visualization,
3. [Flask](http://flask.pocoo.org/docs/1.0/) to run the web-app locally.
4. [Kaggle API](https://github.com/Kaggle/kaggle-api) Kaggle API to download Kaggle meta dataset.
