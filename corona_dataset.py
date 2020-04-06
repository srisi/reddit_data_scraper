from pathlib import Path

from IPython import embed
import csv

import random
# set random seed so that we can randomly select documents but will always
# get the same selection
random.seed(0)

class CoronaDataset:

    def __init__(self):


        self.data = self.load_corona_data()
        print(f"Loaded Coronavirus reddit dataset with {len(self.data)} comments.")


    def load_corona_data(self):
        """
        Loads the daily corona data from data/corona and returns it as a list of dictionaries

        Each dictionary has the following attributes:
        'date': str, e.g. '2020-03-03',
        'author': str, e.g. 'SpartanMonkChaos',
        'subreddit': str, e.g. 'Coronavirus',
        'score': int, e.g. 30
        'url': e.g. 'https://www.reddit.com/r/Coronavirus/comments/fug3vz/us_blocks_medical_aids_to_cuba/fmclle7/',
        'text': Comment text

        :return:
        """

        data = []
        for filepath in Path('data', 'corona').iterdir():
            with open(filepath) as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    row['score'] = int(row['score'])
                    data.append(row)
        return data

    def get_data_sample(
            self,
            start_date='2020-01-01',
            end_date='2020-04-04',
            number_of_comments=1000,
            minimum_number_of_words_per_comment=10,
            select_by='random'
    ):
        """
        Select a sample of the data from start to end date

        :param start_date:          str, default: '2020-01-01'
        :param end_date:            str, default: '2020-04-04'
        :param number_of_comments:  int, number of comments to select, default: 1000
        :param minimum_number_of_words_per_comment: int, minimum number of words each comment needs
                                                         to contain to be included. default: 10
        :param select_by:           str, either "random" for random selection or "score" to select
                                         highest scoring comments. Default random.

        :return: list(dicts)

        # load a set with 10 random samples before 2020-01-10
        >>> dataset = CoronaDataset()
        Loaded Coronavirus reddit dataset with 75390 comments.
        >>> sample = dataset.get_data_sample(start_date='2020-01-01', end_date='2020-01-10',
        ...              number_of_comments=10)
        >>> len(sample)
        10

        # select 10 highest scoring comments from April 1st
        >>> sample = dataset.get_data_sample(start_date='2020-04-01', end_date='2020-04-01',
        ...             number_of_comments=10, select_by='score')
        >>> highest_scoring = sample[0]
        >>> highest_scoring['score']
        323
        >>> highest_scoring['text']
        'Huh. How’d you miss that one, Brian?\n\nBecause I knew that. And I’m not the governor of an entire state.'

        """

        if select_by not in {'random', 'score'}:
            raise ValueError(f'select_by has to be "random" or "score" but not {select_by}.')

        comments_matching_criteria = []
        for comment in self.data:
            comment_length = len(comment['text'].split())
            if (
                start_date <= comment['date'] <= end_date and
                comment_length >= minimum_number_of_words_per_comment
            ):
                comments_matching_criteria.append(comment)

        if select_by == 'random':
            if len(comments_matching_criteria) <= number_of_comments:
                sample = comments_matching_criteria
            else:
                sample = random.sample(comments_matching_criteria, number_of_comments)
        else:
            sample = sorted(comments_matching_criteria,
                            key=lambda x: x['score'], reverse=True)[:number_of_comments]

        if len(sample) < number_of_comments:
            print(f"Warning! Could only find {len(sample)} documents rather than the "
                  f"{number_of_comments} requested.")

        return sample




if __name__ == '__main__':
    c = CoronaDataset()
    sample = c.get_data_sample()