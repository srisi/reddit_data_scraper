from datetime import datetime, timezone
import urllib.request
import html
import json
import csv
from pathlib import Path

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

        # the code in the init file mostly just validates the input, e.g. are the submitted dates
        # formed correctly
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

    @property
    def filename(self):
        """
        generate filename for this search
        :return:
        """

        name_parts = []
        if self.search_term:
            name_parts.append(self.search_term)
        if self.subreddit:
            name_parts.append(f'r{self.subreddit}')
        if self.min_score > 0:
            name_parts.append(f'minscore_{self.min_score}')

        if self.start_date != '1990-01-01' or self.end_date != '2030-01-01':
            name_parts.append(f'{self.start_date}to{self.end_date}')

        return "_".join(name_parts)

    def execute_query_and_store_as_csv(self, output_filename=None):
        """
        Execute search and stores result as a csv file

        :return:
        """

        url = self._generate_query_url()
        documents = self._get_documents(url)
        self._store_documents_to_csv(documents, output_filename)

        print(f'Found {len(documents)} matching your search query.')

    def _generate_query_url(self):
        """
        Generates a url to query pushshift.io with the passed parameters
        :return: str

        >>> r = RedditScraper(search_term='fentanyl', subreddit='boston')
        >>> r._generate_query_url()
        'https://api.pushshift.io/reddit/search/?q=fentanyl&subreddit=boston&size=100'

        >>> r2 = RedditScraper(start_date='2014-01-01', end_date='2014-12-31')
        >>> r2._generate_query_url()
        'https://api.pushshift.io/reddit/search/?size=100&after=1388552400&before=1420002000'
        """

        search_params = {}
        if self.search_term:
            search_params['q'] = self.search_term
        if self.subreddit:
            search_params['subreddit'] = self.subreddit
        search_params['size'] = self.number_of_results

        if self.start_date != '1990-01-01':
            search_params['after'] = self.start_date_timestamp
        if self.end_date != '2030-01-01':
            search_params['before'] = self.end_date_timestamp

        url = f'https://api.pushshift.io/reddit/search/?{urllib.parse.urlencode(search_params)}'

        if self.min_score and self.min_score > 0:
            url += f'&score=>{self.min_score}'

        return url

    def _get_documents(self, url):
        """
        Downloads up to number_of_documents matching the search query from pushshift.io

        :param url: str
        :return: list[dict]
        """

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
                    'text': html.unescape(doc_raw['body']),
                })
        return documents

    def _store_documents_to_csv(self, documents, filename):
        """
        Stores the downloaded documents in a csv in the data folder.
        If no filename is provided, it will automatically generate one.

        :param documents: list[dict]
        :param filename: str
        :return:
        """

        if not filename:
            filename = self.filename

        with open(Path('data', f'{filename}.csv'), 'w') as csvfile:
            fieldnames = ['date', 'author', 'subreddit', 'score', 'url', 'text']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for doc in documents:
                writer.writerow(doc)


if __name__ == '__main__':
    r = RedditScraper(search_term='opioid',
                      subreddit='kentucky',
                      number_of_results=2000, min_score=2)
    r.execute_query_and_store_as_csv()

