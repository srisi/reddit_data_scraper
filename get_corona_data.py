# It usually makes sense to define a task in one file and then execute it in another
# to do that, we need to import the reddit scraper from reddit_scraper.py, which the following
# line does.
from reddit_scraper import RedditScraper

from datetime import date, timedelta

from IPython import embed
from pathlib import Path

import csv
import time

def get_daily_corona_data(search_term, subreddit, filename):
    """
    Get the 1000 highest scoring comments from reddit for each day from 2020-01-01 to 2020-04-04

    r/coronavirus has more than 1000 comments for each day after 01-24 -> we're using
    r/coronavirus after 01-24. Before that, we're using the search term "coronavirus" to look
    for comments all across reddit.

    :return:
    """

    current_date = date(2020, 1, 1)
    end_date = date(2020, 4, 26)
    documents = []

    # iterate over all days from the start date (= current_date) as long as current_date + 1 day
    # is less than the end date
    while current_date + timedelta(days=1) <= end_date:


        r = RedditScraper(
            subreddit=subreddit, search_term=search_term,
            # end date is current day + 24 hours
            start_date=str(current_date), end_date=str(current_date + timedelta(days=1)),
            number_of_results=2000, min_score=0, sort_by='score'
        )
        url = r._generate_query_url()
        documents += r._get_documents(url)

        print(len(documents))

        print(current_date)
        current_date += timedelta(days=1)
        time.sleep(1)

    filepath = Path(f'data/{filename}')
    with open(filepath, 'w') as csvfile:
        fieldnames = ['date', 'author', 'subreddit', 'score', 'url', 'text']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for doc in documents:
            writer.writerow(doc)


if __name__ == '__main__':
    # time.sleep(1200)
    get_daily_corona_data(subreddit=None, search_term='coronavirus',
                          filename='all_subreddits.csv')
    # time.sleep(1200)
    # get_daily_corona_data(subreddit='coronavirus', search_term=None,
    #                       filename='coronavirus.csv')
    # time.sleep(1200)
    # get_daily_corona_data(subreddit='china_flu', search_term=None,
    #                       filename='china_flu.csv')