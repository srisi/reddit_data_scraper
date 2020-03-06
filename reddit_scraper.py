from datetime import datetime, timezone
import urllib
from IPython import embed
import json


class RedditScraper:

    def __init__(self,
               search_term=None, subreddit=None, number_of_results=100,
               start_date='1990-01-01', end_date='2030-01-01',
               min_score=0
               ):
        """

        :param search_term: all comments need to include this search term
        :param subreddit: limit results to subreddit
        :param number_of_results: max number of comments to return
        :param start_date: all comments need to be posted on or after this date (format: YYYY-MM-DD)
        :param end_date: all comments need to be posted before or on this date (format: YYYY-MM-DD)
        :param min_score: minimum score (upvotes) for a comment to be included.
        """

        for param in [search_term, subreddit]:
            if not (isinstance(param, str) or param is None):
                raise ValueError("Search term and sub reddit have to be strings.")
        self.search_term = search_term
        self.subreddit = subreddit

        for date, description in [(start_date, 'start_date'), (end_date, 'end_date')]:

            try:
                dt = datetime.strptime(date, "%Y-%m-%d")
                timestamp = int(datetime.timestamp(dt))
                # only encode date if it is not the default to speed up query
                self.__setattr__(description, date)
                self.__setattr__(f'{description}_timestamp', timestamp)
            except (TypeError, ValueError):
                raise ValueError("date has to follow the format YYYY-MM-DD, e.g. 1900-01-01.")

        for param in [number_of_results, min_score]:
            if not isinstance(param, int) or param < 0:
                raise ValueError("number_of_results and min_score have to be positive integers.")
        self.number_of_results = number_of_results
        self.min_score = min_score

    def execute_query_and_store_as_csv(self):
        """
        Execute search and stores result

        :return:
        """

        url = self.generate_query()
        documents = []
        with urllib.request.urlopen(url) as response:
            response = response.read().decode('utf-8')

            for doc_raw in json.loads(response)['data']:

                timestamp = doc_raw['created_utc']
                datetime_utc = datetime.utcfromtimestamp(timestamp)
                datetime_est = datetime_utc.replace(tzinfo=timezone.utc).astimezone(tz=None)
                date_str = datetime_est.strftime('%Y-%m-%d')

                if 'permalink' in doc_raw:
                    url = f'https://www.reddit.com{doc_raw["permalink"]}'
                else:
                    url = 'n/a'

                documents.append({
                    'date': date_str,
                    'author': doc_raw['author'],
                    'subreddit': doc_raw['subreddit'],
                    'score': doc_raw['score'],
                    'url': url,
                    'text': doc_raw['body'],
                })


        embed()


    def generate_query(self):
        """
        This function generates a query to pushshift.io with the passed parameters
        :return:
        """

        search_params = {}
        if self.search_term:
            search_params['q'] = self.search_term
        if self.subreddit:
            search_params['subreddit'] = self.subreddit
        search_params['size'] = self.number_of_results
        search_params['after'] = self.start_date_timestamp
        search_params['before'] = self.end_date_timestamp

        url = f'https://api.pushshift.io/reddit/search/?{urllib.parse.urlencode(search_params)}'

        if self.min_score and self.min_score > 0:
            url += f'&score=>{self.min_score}'

        return url

if __name__ == '__main__':
    r = RedditScraper(search_term='fentanyl', subreddit='Boston', min_score=5)
    r.execute_query_and_store_as_csv()

