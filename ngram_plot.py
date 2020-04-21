from datetime import date, timedelta
import re
import matplotlib.pyplot as plt
import csv

from corona_dataset import CoronaDataset


def create_ngram_plot(term, display_mode='counts'):
    """
    Create and show an ngram plot for the provided term within the
    reddit coronavirus dataset
    """

    if display_mode == 'counts':
        search_term_counts_by_day = get_daily_counts_of_search_term(term)
    else:
        search_term_counts_by_day = get_daily_frequencies_of_search_term(term)

    y = get_moving_averaged_data(search_term_counts_by_day,
                                 number_of_days_to_average_on_each_side=3)

    print(search_term_counts_by_day)
    print(y)

    all_dates = get_all_days_between_start_date_and_end_date()

    # increase plot size to 1000 x 500 pixels
    plt.figure(figsize=(20, 10))
    plt.plot(all_dates, y)

    # set ticks by hand to the beginning and middle of each month
    plt.xticks([
        '2020-01-01', '2020-01-15', '2020-02-01', '2020-02-15', '2020-03-01', '2020-03-15',
        '2020-04-01'
    ])

    # set a plot title with font size 20
    plt.title(f'Counts of "{term}" in the Coronavirus dataset.', fontsize=20)
    plt.show()


def store_ngram_data_in_csv(term, filename):
    """
    Instead of plotting ngram data, stores it in a csv

    :param term:
    :param filename:
    :param display_mode:
    :return:
    """

    if not filename.endswith('.csv'):
        raise ValueError("data will be written in csv format, so the filename has to end in "
                         "'.csv'.")

    # get data to display and average it
    # counts
    search_term_counts_by_day = get_daily_counts_of_search_term(term)
    search_term_counts_by_day = get_moving_averaged_data(search_term_counts_by_day,
                                 number_of_days_to_average_on_each_side=3)
    # frequencies
    search_term_frequencies_by_day = get_daily_frequencies_of_search_term(term)
    search_term_frequencies_by_day = get_moving_averaged_data(search_term_frequencies_by_day,
                                  number_of_days_to_average_on_each_side=3)

    # get list of dates for x-axis labels
    dates = get_all_days_between_start_date_and_end_date()

    # throw an error if the number of daily counts we have doesn't equal the number of dates
    assert len(search_term_counts_by_day) == len(dates)

    # finally, write this data to disk as a csv file (which is very similar to an excel file.
    # we are writing the data as two columns, one for dates and one for counts.
    # so we are writing "date", "count", "frequency" in the first row. the following rows are
    # actual data, eg. "2020-01-05", 0, 0.0
    # csv stands for "Comma-separated values", i.e. the different values (or columns) are separated
    # by commas
    # operating with the csv is a bit ... janky. Generally, the documentation gives you good
    # patterns to just copy: https://docs.python.org/3/library/csv.html
    with open(filename, 'w', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        # write the header
        csv_writer.writerow(['date', 'count', 'frequency'])
        # write all data rows
        for i in range(len(search_term_counts_by_day)):
            csv_writer.writerow([dates[i],
                                 search_term_counts_by_day[i],
                                 search_term_frequencies_by_day[i]])



def get_daily_counts_of_search_term(term):
    """
    Get the absolute number of times the term appeared for each day
    in the dataset as a list
    """

    dataset = CoronaDataset()
    all_dates = get_all_days_between_start_date_and_end_date()

    search_term_counts_by_day = []

    # iterate over all days
    for date in all_dates:

        # get a sample for this particular day with 1000 comments
        day_sample = dataset.get_data_sample(start_date=date, end_date=date,
                                             number_of_comments=1000)

        # variable to store the number of appearances on that day
        day_count_of_searchterm = 0

        # iterate over all comments in the sample of that day
        for comment in day_sample:

            # get the tokenized text for that comment
            text = comment['text'].lower()
            tokenized_text = re.findall(r'\b\w\w+\b', text)

            # iterate over all words...
            for word in tokenized_text:
                # ... and if it is the word that we're looking for,
                # increment the count by one
                if word == term:
                    day_count_of_searchterm += 1

        # at the end of each day, add the count to our search_term_counts_by_day list
        search_term_counts_by_day.append(day_count_of_searchterm)

    return search_term_counts_by_day

def get_daily_frequencies_of_search_term(term):
    """
    Get the absolute number of times the term appeared for each day
    in the dataset as a list
    """

    dataset = CoronaDataset()
    all_dates = get_all_days_between_start_date_and_end_date()

    search_term_frequencies_by_day = []

    # iterate over all days
    for date in all_dates:

        day_sample = dataset.get_data_sample(start_date=date, end_date=date,
                                             number_of_comments=1000)
        day_count_of_searchterm = 0
        total_count_of_terms = 0

        for comment in day_sample:
            text = comment['text'].lower()
            tokenized_text = re.findall(r'\b\w\w+\b', text)

            for word in tokenized_text:
                total_count_of_terms += 1
                if word == term:
                    day_count_of_searchterm += 1

        # avoid division by zero
        term_frequency = day_count_of_searchterm / (total_count_of_terms + 0.0000001)

        search_term_frequencies_by_day.append(term_frequency)

    return search_term_frequencies_by_day


def get_all_days_between_start_date_and_end_date(start_date='2020-01-01', end_date='2020-04-04'):
    """
    Get all days between start_date and end_date as a list of strings
    """

    all_dates = []

    # the date function expects integers, i.e. calling it like this date(2020, 1, 1)
    # since we have strings, we extract the relevant parts and turn them into integers.
    # e.g. start_date[:4] extracts the first 4 characters from the start date, which is
    # "2020". start_date[5:7] extracts the month and start_date[8:] extracts the date.
    current_date = date(int(start_date[:4]), int(start_date[5:7]), int(start_date[8:]))
    end_date = date(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:]))

    # start at the start date and iterate as long as we have not hit the end date
    while current_date <= end_date:
        # add each date to the list...
        all_dates.append(str(current_date))
        # ... and increment current_date to the next day
        current_date = current_date + timedelta(days=1)

    return all_dates


def get_moving_averaged_data(data, number_of_days_to_average_on_each_side=3):
    """
    Returns the data list after applying a moving average to it.
    number_of_days_to_average_on_each_side tells us how many days to include
    in the average on each side. With the default setting of 3, we are averaging
    a week of data (3 days before the current day; the current day; and 3 days after)
    """

    averaged_data = []

    # i goes from 0 to the nth (last) day.
    # using range here allows us to access the day before and after i
    for i in range(len(data)):
        # our goal is to select a sublist going from number_of_days before the current
        # day to number_of_days after.

        # however, we can't look into negative days, so if the number were to become
        # negative, we use 0 instead
        start_index = max(0, i - number_of_days_to_average_on_each_side)

        # same principle: we want to go number_of_days out but only until we hit the end
        # of the list
        # note the + 1 at the end. selecting a slice from a list is exclusive at the upper
        # end. i.e. we're selecting elements up to but not including the end_index.
        end_index = min(len(data), i + number_of_days_to_average_on_each_side + 1)

        # now, we can find our selected values
        selected_values = data[start_index: end_index]

        # ... and use them to calculate the average
        averaged_data.append(sum(selected_values) / len(selected_values))

    return averaged_data

if __name__ == '__main__':
    # create_ngram_plot('covid')
    store_ngram_data_in_csv('covid', 'covid.csv')