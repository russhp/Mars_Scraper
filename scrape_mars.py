
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import sys

def scrape():
    """Initializes web broser using splinter library, scrapes info relating to
    mars, and returns a dictionary containing four objects.
    
    Note that scrape() can take about 2 minutes to run with average internet speed.
    If internet is too slow, hopefull error handling will exit, 
    but it may crash.
    
    Returns:
    
    - top-news: dict contating the top news article and snippet from
        https://mars.nasa.gov/news/
        
    - featured_image: str containing the url of the current top image from
        https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars
        
    - mars_weather: str containing text of most recent tweet from @MarsWxReport
        https://twitter.com/marswxreport?lang=en
        
    - facts_table: str containing an html table of mars facts, scraped from
        https://space-facts.com/mars/
        
    - hemisphere_images: list of dicts containing titles and urls of four mars
        hemispheres from
        https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars
    """
    
    # initialize broswer object, headless=True to prevent 
    # new window from opening
    with Browser('chrome', executable_path='drivers/chromedriver',
                      headless=True) as browser:
    
    

        # urls to scrape
        news_url = 'https://mars.nasa.gov/news/'
        image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
        tweet_url = 'https://twitter.com/marswxreport?lang=en'
        facts_url = 'https://space-facts.com/mars/'
        hemis_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'


        ## NASA Mars News

        # visit news site, make soup
        browser.visit(news_url)
        time.sleep(5)
        news_soup = bs(browser.html, 'lxml')
        
        # queries to collect article title, snippet, and date
        news_title_query = news_soup.find(class_='content_title', 
                                          string=True)
        time.sleep(5)
        news_snippet_query = news_soup.find(class_='article_teaser_body', 
                                            string=True)
        time.sleep(5)
        news_date_query = news_soup.find(class_='list_date', 
                                         string=True)

        # make a dictionary contatining the string results from the queries
        # only if the data loaded. If it didn't internet is probably too slow.
        if news_title_query:
            news_dict = {'news_title':news_title_query.text,
                         'news_p':news_snippet_query.text,
                         'date':news_date_query.text}
        else:
            print("internet is too slow, adjust sleep times in "
                  "the code or find better internet connection.")
            browser.quit()
            sys.exit()


        ## JPL Mars Space Images - Featured Image

        # base url used to make HiRes image link.
        jpl_url = 'https://www.jpl.nasa.gov'

        # visit image site, make soup
        browser.visit(image_url)
        time.sleep(5)

        # 'FULL IMAGE' click stays on the same page but 
        # opens a collapsed overlay
        browser.click_link_by_partial_text('FULL IMAGE')
        time.sleep(5)

        # 'more info' links to another page containing the full-size image
        browser.click_link_by_partial_text('more info')
        time.sleep(5)

        # collect image url from page, which is partial, 
        # and add the base url with string concatination
        image_soup = bs(browser.html, 'lxml')
        image_query = image_soup.find(class_='main_image')
        featured_image_url = jpl_url + image_query['src']


        ## Mars Weather

        # visit Twitter for weather post, make soup
        browser.visit(tweet_url)
        time.sleep(5)
        tweet_soup = bs(browser.html, 'lxml')

        # run query, remove everything after first line of tweet,
        # could be an
        tweet_query = tweet_soup.find(class_='tweet-text')
        mars_weather = tweet_query.text.split('\n')[0]


        ## Mars Facts

        # can read the table off website directly using pandas and the url
        facts_raw_list = pd.read_html(facts_url)

        # resulting list of one item is modified to make dataframe
        facts_raw_list[0].columns = ['feature', 'value']
        facts_df = facts_raw_list[0]

        # dataframe is then exported to html table, 
        # and newline characters are removed
        facts_html = facts_df.to_html(index=False, header=False)
        facts_html = facts_html.replace('dataframe', 'table table-dark')
        facts_html = facts_html.replace('\n', '')


        ## Mars Hemispheres

        # hemispheres website is visited once to 
        # establish link text to be clicked
        browser.visit(hemis_url)
        time.sleep(5)
        hemis_soup = bs(browser.html, 'lxml')
        hemis_query = hemis_soup.find_all(class_='item')

        # initialize list for list of dictionaries
        hemisphere_image_urls = []

        # from first query, retrieved all h3.text contents, 
        # which are the links for accessing the full images.
        # Then, loop over the four links and collect images. 
        # Note there are even bigger .tif files (>20mb) 
        # that are not being used for downloading/rehosting
        for result in hemis_query:

            # click through each link located in <h3> tag
            browser.click_link_by_partial_text(result.h3.text)
            time.sleep(5)
            
            # make soup of resulting page
            hemis_temp_soup = bs(browser.html, 'lxml')
            # modify image name
            hemi_name = result.h3.text.replace('Hemisphere Enhanced', '')
            # collect image url
            hemi_img_url = hemis_temp_soup.find(target='_blank')['href']
            # and put name and url into list of dictionaries
            hemisphere_image_urls.append({'title':hemi_name,
                                          'img_url':hemi_img_url})
            # return to home page to click through the next link
            browser.visit(hemis_url)
            
            
        ## Make final output dictionary
        output = dict(
            top_news=news_dict,
            featured_image=featured_image_url,
            mars_weather=mars_weather,
            facts_table=facts_html,
            hemisphere_images=hemisphere_image_urls
        )
    return output