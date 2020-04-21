# It usually makes sense to define a task in one file and then execute it in another
# to do that, we need to import the reddit scraper from reddit_scraper.py, which the following
# line does.
from reddit_scraper import RedditScraper

from datetime import date, timedelta

import time

def get_daily_corona_data():
    """
    Get the 1000 highest scoring comments from reddit for each day from 2020-01-01 to 2020-04-04

    r/coronavirus has more than 1000 comments for each day after 01-24 -> we're using
    r/coronavirus after 01-24. Before that, we're using the search term "coronavirus" to look
    for comments all across reddit.

    :return:
    """

    current_date = date(2020, 1, 1)
    end_date = date(2020, 4, 21)

    # iterate over all days from the start date (= current_date) as long as current_date + 1 day
    # is less than the end date
    while current_date + timedelta(days=1) <= end_date:

        # before 01-24, search for mentions of "coronavirus" across reddit
        if current_date < date(2020, 1, 24):
            search_term = 'coronavirus'
            subreddit = None

        # after 01-24, look for comments in r/coronavirus
        else:
            search_term = None
            subreddit = 'coronavirus'

        search_term = 'coronavirus'
        subreddit = None

        r = RedditScraper(
            subreddit=subreddit, search_term=search_term,
            # end date is current day + 24 hours
            start_date=str(current_date), end_date=str(current_date + timedelta(days=1)),
            number_of_results=2000, min_score=0, sort_by='score'
        )
        r.execute_query_and_store_as_csv()

        print(current_date)
        current_date += timedelta(days=1)
        time.sleep(1)


if __name__ == '__main__':
    get_daily_corona_data()