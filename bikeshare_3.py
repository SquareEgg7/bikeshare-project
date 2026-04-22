import time
import pandas as pd
import numpy as np

CITY_DATA = { 'Chicago': 'chicago.csv',
              'New York City': 'new_york_city.csv',
              'Washington': 'washington.csv' }

def get_filters():
    """
    Ask user to specify a city, month, and day to analyze.

    Return:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    """
    print('Hello! Let\'s explore some US bikeshare data!')
    # get user input for city (chicago, new york city, washington). HINT: Use a while loop to handle invalid inputs
    while True:
        try:
            city = input('Please enter the city for which you would like to filter - Chicago, New York City, or Washington: ')
            if city.title() in list(CITY_DATA.keys()):
                break
            else:
                raise ValueError
        except ValueError:
            print('Invalid input')

    # get user input for month (all, january, february, ... , june)
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'All']
    while True:
        try:
            month = input('Please enter the month for which you would like to filter - January, February, March, April, May, June, or \'All\' for all months): ')
            if month.title() in months:
                break
            else:
                raise ValueError
        except ValueError:
            print('Invalid input')


    # get user input for day of week (all, monday, tuesday, ... sunday)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'All']
    while True:
        try:
            day = input('Please enter the day of the week for which you would like to filter (or \'All\' for all days): ')
            if day.title() in days:
                break
            else:
                raise ValueError
        except ValueError:
            print('Invalid input')

    print('-'*40)
    # city, month, day returned capitalized with rest of letter lowercase to handle all variations of caps/lower case input
    return city.title(), month.title(), day.title()


def load_data(city, month, day):
    """
    Load data for the specified city and filters by month and day if applicable.

    Args:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    Return:
        df - Pandas DataFrame containing city data filtered by month and day
        (int) original_size - number of trips in original dataset before filtering
    """

    # load data file into a dataframe
    df = pd.read_csv(CITY_DATA[city])
    
    # take note of size of original dataset before filtering
    original_size = len(df)
    
    # convert the Start Time column to datetime
    df['Start Time'] = pd.to_datetime(df['Start Time'])

    # extract month and day of week from Start Time to create new columns
    df['Month'] = df['Start Time'].dt.month
    df['Day of Week'] = df['Start Time'].dt.day_name()

    # filter by month if applicable
    if month != 'All':
        # use the index of the months list to get the corresponding int
        months = ['January', 'February', 'March', 'April', 'May', 'June']
        month = months.index(month) + 1
    
        # filter by month to create the new dataframe
        df = df[df['Month'] == month]

    # filter by day of week if applicable
    if day != 'All':
        # filter by day of week to create the new dataframe
        df = df[df['Day of Week'] == day.title()]

    return df, original_size


def print_summary(df, original_size, city, month, day):
    """Display summary of user's query.

    Args:
        df - Pandas DataFrame containing city data filtered by month and day
        (int) original_size - number of trips in original dataset before filtering
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    """

    # determine trip count of user query
    trip_count = len(df)

    #determine what portion of the total data for the city is represented by user query
    portion_of_original_df = '{:.1%}'.format(trip_count / original_size)
    
    # print summary of user query
    if month != 'All':
        message_month = 'in the month of ' + month
    else:
        message_month = 'in all months'
    if day != 'All':
        message_day = day + 's'
    else:
        message_day = 'all days of the week'
        
    print('You have chosen to view data for {}, showing data for {} {}, which represents {} of the {} trips in the total {} dataset.'.format(city, message_day, message_month, portion_of_original_df, format(original_size, ','), city))

def time_stats(df, month, day):
    """Display statistics on the most frequent times of travel.  

    To avoid confusion, prefiltration is noted, where applicable.  
    To avoid confusion, if dataset is filtered for only months or only days, months or days, respectively, are noted first.  
    """

    print('\nCalculating The Most Frequent Times of Travel...\n')
    start_time = time.time()

    if month == 'All':
        # display day filter first, if it's the only filter
        if day != 'All':
            day = day + 's'
            print('Analysis prefiltered to only show information related to: ', day)

        # find the most common month (from 1 to 6)
        popular_month = df['Month'].mode()[0]
    
        # convert month from integer to name
        months = ['January', 'February', 'March', 'April', 'May', 'June']
        popular_month = months[popular_month - 1]

        # display the most common month
        print('Most Frequent Start Month:', popular_month)    
    else:
        # display message to clarify that results are limited to a single month
        print('Analysis prefiltered to only show information related to: ', month)
    
    if day == 'All':
        # find the most common day of week (from Sunday to Saturday)
        popular_day_of_week = df['Day of Week'].mode()[0]
    
        # display the most common day of week
        print('Most Frequent Start Day: ', popular_day_of_week)    
    else:
        # display message to clarify that results are limited to a single day, but only if results have also been limited to a single month
        if month != 'All':
            day = day + 's'
            print('Analysis prefiltered to only show information related to: ', day)

    # extract hour from the Start Time column to create an hour column
    df['Hour'] = df['Start Time'].dt.hour

    # find the most common hour (from 0 to 23)
    popular_hour = df['Hour'].mode()[0]

    # convert integer to formatted hour with am / pm
    time_struct = time.struct_time((0, 0, 0, popular_hour, 0, 0, 0, 0, 0))
    popular_hour = time.strftime('%I:%M %p', time_struct)

    # display the most common start hour
    print('Most Frequent Start Hour: ', popular_hour)

    print('\nThis took %s seconds.' % (time.time() - start_time))
    print('-'*40)


def station_stats(df):
    """Display statistics on the most popular stations and trip."""

    print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()

    # determine the most commonly used start station:
    most_common_start_station = df['Start Station'].value_counts().index[0]

    # display most commonly used start station
    print('The most commonly used start station is: ', most_common_start_station)

    # determine the most commonly used end station:
    most_common_end_station = df['End Station'].value_counts().index[0]

    # display most commonly used end station
    print('The most commonly used end station is: ', most_common_end_station)

    # create new column composed of the start station and end station of each trip
    df['Trip'] = df['Start Station'] + ' to ' + df['End Station']
    most_common_trip = df['Trip'].value_counts().index[0]

    # display most frequent combination of start station and end station trip
    print('The most common trip taken is: ', most_common_trip)

    print('\nThis took %s seconds.' % (time.time() - start_time))
    print('-'*40)


def trip_duration_stats(df):
    """Display statistics on the total and average trip duration."""

    print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    # calculate total travel time
    total_travel_time = df['Trip Duration'].sum()
    
    #convert total travel time to minutes or hours
    if total_travel_time < 3600:
        total_travel_time = str(format((total_travel_time / 60), '.1f'))  + " minutes"
    else:
        total_travel_time = str(format((total_travel_time / 3600), ',.1f')) + " hours"

    # display total travel time
    print('The total travel time is: ' + total_travel_time)

    # calculate mean travel time
    mean_travel_time = df['Trip Duration'].mean()

    #convert mean travel time to minutes or hours
    if mean_travel_time < 3600:
        mean_travel_time = str(format((mean_travel_time / 60), '.1f')) + " minutes"
    else:
        mean_travel_time = str(format((mean_travel_time / 3600), ',.1f')) + " hours"

    # display mean travel time
    print('The mean travel time is: ' + mean_travel_time)

    print('\nThis took %s seconds.' % (time.time() - start_time))
    print('-'*40)


def user_stats(df, city):
    """Display statistics on bikeshare users."""

    print('\nCalculating User Stats...\n')
    start_time = time.time()

    # Display counts of user types
    subscribers = df['User Type'].value_counts()[0]
    customers = df['User Type'].value_counts()[1]
    no_user_type = df.isnull().sum()['User Type']
    # handles files where there is no 'dependent' 'User Type' (currently Washington and New York City, but future-proofed for other cities that may not have this 'User Type')
    while True:
        try:
            dependent = df['User Type'].value_counts()[2]
            print('Subscribers: {}\nCustomers: {}\nDependent: {}\nNo User Type Specified: {}\n'.format(format(subscribers, ','), format(customers, ','), format(dependent, ','), format(no_user_type, ',')))
            break
        except IndexError:
            print('Subscribers: {}\nCustomers: {}\nDependent: 0\nNo User Type Specified: {}\n'.format(format(subscribers, ','), format(customers, ','), format(no_user_type, ',')))
            break
    
    while True:
        try:
            # Display counts of gender
            male = df['Gender'].value_counts()[0]
            female = df['Gender'].value_counts()[1]
            no_gender = df['Gender'].isnull().sum()
            print('Male: {}\nFemale: {}\nNo Gender Specified: {}'.format(format(male, ','), format(female, ','), format(no_gender, ',')))

            # Display earliest, most recent, and most common year of birth
            earliest_birth = int(df['Birth Year'].min())
            print('\nEarliest birth year: ', earliest_birth)
            most_recent_birth = int(df['Birth Year'].max())
            print('Most recent birth year: ', most_recent_birth)
            most_common_birth = int(df['Birth Year'].mode()[0])
            print('Most common birth year: ', most_common_birth)
            no_birth_year = df['Birth Year'].isnull().sum()
            print('No birth year specified: ', format(no_birth_year, ','))
            break
        # handles files where there is no 'Gender' or 'Birth Year' column (currently only Washington, but future-proofed for other cities that may not have these columns)
        except KeyError:
            print('Gender, birth year information unavailable')
            break

    print("\nThis took %s seconds." % (time.time() - start_time))
    print('-'*40)

def raw_data(df):
    """Prompt user and print raw data in sets of five trips at a time. """

    # initialize local variables
    see_data = 'yes'
    row_count = 0
    remaining_row_count = 0
    if len(df) < 5:
        remaining_row_count = 0
    else: 
        remaining_row_count = len(df) - 5
    
    while see_data.lower() == 'yes':
        while True:
            try:
                # initial prompt before they have seen any raw data
                if row_count == 0:
                    see_data = input('\nWould you like to see the raw data? Enter yes or no.\n')
                # different prompt if they have already seen rows of raw data
                else:
                    see_data = input('\nWould you like to see more raw data? Enter yes or no.\n')
                if see_data.lower() == 'yes':
                    # if there are 5 or fewer rows remaining to be seen
                    if (row_count + 5) >= len(df):
                        for i in range(row_count, len(df)):
                            print(df.iloc[i], '\n')
                        print('Total rows in dataset: ', format(len(df), ','))
                        print('Rows seen: ', format(len(df), ','))
                        print('Rows remaining to be seen: 0')
                        break  
                    # if there are more than 5 rows remaining to be seen
                    else:    
                        for i in range(row_count, (row_count + 5)):
                            print(df.iloc[i], '\n')
                        print('Total rows in dataset: ', format(len(df), ','))
                        row_count = row_count + 5
                        print('Rows seen: ', format(row_count, ','))
                        print('Rows remaining to be seen: ', format(remaining_row_count, ','))
                        remaining_row_count = remaining_row_count - 5
                elif see_data.lower() == 'no':
                    break
                else:
                    raise ValueError
            except ValueError:
                print('Invalid input')            
       
def main():
    restart = 'yes'
    while restart.lower() == 'yes':
        city, month, day = get_filters()
        df, original_size = load_data(city, month, day)

        print_summary(df, original_size, city, month, day)
        time_stats(df, month, day)
        station_stats(df)
        trip_duration_stats(df)
        user_stats(df, city)
        raw_data(df)        

        while True:
            try:
                restart = input('\nWould you like to restart? Enter yes or no.\n')
                if restart.lower() == 'yes' or restart.lower() == 'no':
                    break
                else:
                    raise ValueError
            except:
                print('Invalid input')

if __name__ == '__main__':
	main()
