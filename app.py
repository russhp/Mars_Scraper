from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

# make client
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")


@app.route('/')
def index():
    # run query on mongo database containing scraped results
    query = mongo.db.mars_db.find_one()
    
    # check if query has contents before unpacking
    if query:
        # unpack query results into python variables
        news_p = query['top_news']['news_p']
        news_title = query['top_news']['news_title']
        date = query['top_news']['date']
        featured_image = query['featured_image']
        mars_weather = query['mars_weather']
        table = query['facts_table']
        hemis_list = query['hemisphere_images']

    # render the index page using variables local to index() function
    return render_template('index.html',
                **locals())

@app.route('/scrape')
def scraper():
    # make collection object
    mars_db = mongo.db.mars_db
    
    # run scraper python app and save to dictionary
    mars_dict = scrape_mars.scrape()
    
    # push dictionary results to mongo using the collection object
    # syntax: .update(find_param, whatsupdating_param, **kwargs)
    mars_db.update({}, mars_dict, upsert=True)
    
    # when done scraping, redirect to home page.
    return redirect('/', code=302)