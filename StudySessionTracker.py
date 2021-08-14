import os
import time
import pandas as pd 
import numpy as np
from datetime import datetime, timedelta, date
import seaborn as sns
import matplotlib.pyplot as plt
plt.style.use('dark_background')
sns.set_palette('brg')

CWD = os.getcwd()
TRACKER_PATH = os.path.join(CWD, 'Tracker')

if not os.path.isdir(TRACKER_PATH):
    os.mkdir(TRACKER_PATH)

def convert_to_hours(minutes):
    hours = int(minutes / 60)
    remaining_minutes = int(minutes % 60)
    return hours, remaining_minutes

def annotate_bars(g):
    for p in g.patches:
        if int(p.get_height()) >= 60:
            hours, minutes = convert_to_hours(int(p.get_height()))
            text = '{} hrs {} mins'.format(hours, minutes)
        else:
            text = '{} mins'.format(int(p.get_height()))
        g.annotate(text, 
                    xy = (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', 
                    va = 'center', 
                    xytext = (0, 5), 
                    textcoords = 'offset points')
    return g

class StudyTracker():
    """
    This is for fun. I am hoping to make a tracker that I can
    use when I finish a study session.

    For now, the plan is to create/update a csv with the amount of time that I studied,
    what I studied, and a little discription.

    Eventually, I will add a way to visualize my studying
    """
    def __init__(self):
        self.tracker_file = 'study_tracker.csv'
        # create or load the csv file
        if not self.tracker_file in os.listdir(TRACKER_PATH):
            tracker_csv = pd.DataFrame(columns = ['Topic', 'TimeSpent', 'TimeStart','TimeEnd','Description','Date'])
            tracker_csv.to_csv(os.path.join(TRACKER_PATH, self.tracker_file), index = False)
        
        self.tracker_df = pd.read_csv(os.path.join(TRACKER_PATH, self.tracker_file))
        self.tracker_df['Date'] = pd.to_datetime(self.tracker_df['Date'])
    
    def add_session(self, topic, timeSpent, description):
        """
        timeSpent will always be defined in minutes
        """
        index = len(self.tracker_df)
        current_time = datetime.now()
        timeStart = current_time - timedelta(minutes = timeSpent)
        current_date = date.today()
        tmp_dict = {'Topic' : topic,
                    'TimeSpent' : timeSpent,
                    'TimeStart' : timeStart.strftime('%H:%M'),
                    'TimeEnd' : current_time.strftime('%H:%M'),
                    'Description' : description,
                    'Date' : current_date.strftime('%m/%d/%y')}
        
        tmp_df = pd.DataFrame(tmp_dict, index = [index])
        self.tracker_df = self.tracker_df.append(tmp_df, ignore_index = False)  
        self.tracker_df['Date'] = pd.to_datetime(self.tracker_df['Date'])


    def summarize_session(self, interval = 'day'):
        """
        Visualize the amount of studying that was done for a given interval.
        The options for the interval are 'day', 'week', 'month', or 'year'.
        """
        # summarize by day
        if interval == 'day':
            today = date.today().strftime('%m/%d/%y')
            # filter df
            filtered_df = self.tracker_df[self.tracker_df['Date'] == today]
            if len(filtered_df) == 0:
                return None, None
            # groupby and aggregate
            grouped = filtered_df.groupby(by = 'Topic').agg({'TimeSpent' : 'sum'})
            grouped.reset_index(inplace = True)
            total_time = grouped['TimeSpent'].sum()
            # plot topic and amount of time spent
            fig, ax = plt.subplots(1,1)
            g = sns.barplot(data = grouped, x = 'Topic', y = 'TimeSpent', ax = ax)
            g = annotate_bars(g)
            g.set_title('Minutes Spent on Topics for {}'.format(today))
            g.set(ylabel = 'Time Spent (minutes)')
            plt.tight_layout()
            return fig, total_time

        # summarize by week
        if interval == 'week':
            today = date.today()
            week_ago = today - timedelta(days = 7)
            # filter df
            filtered_df = self.tracker_df[(self.tracker_df['Date'] > pd.to_datetime(week_ago)) & (self.tracker_df['Date'] <= pd.to_datetime(today))]
            # groupby and aggregate
            grouped = filtered_df.groupby(by = 'Topic').agg({'TimeSpent' : 'sum'})
            grouped.reset_index(inplace = True)
            total_time = grouped['TimeSpent'].sum()
            # plot topic and amount of time spent
            fig, ax = plt.subplots(1,1)
            g = sns.barplot(data = grouped, x = 'Topic', y = 'TimeSpent')
            g = annotate_bars(g)
            g.set_title('Minutes Spent on Topics for {} to {}'.format(week_ago.strftime('%m/%d/%y'), today.strftime('%m/%d/%y')))
            g.set(ylabel = 'Time Spent (minutes)')
            plt.tight_layout()
            return fig, total_time
        
        # summarize by month
        # instead of using time delta, I will try to keep them in terms of actual months.
        if interval == 'month':
            current_month = date.today().replace(day = 1)
            # filter df
            filtered_df = self.tracker_df[self.tracker_df['Date'] >= pd.to_datetime(current_month)]
            # groupby and aggregate
            grouped = filtered_df.groupby(by = 'Topic').agg({'TimeSpent' : 'sum'})
            grouped.reset_index(inplace = True)
            total_time = grouped['TimeSpent'].sum()
            # plot topic and amount of time spent
            fig, ax = plt.subplots(1,1)
            g = sns.barplot(data = grouped, x = 'Topic', y = 'TimeSpent')
            g = annotate_bars(g)
            month = datetime.strptime(str(current_month.month), '%m')
            year = datetime.strptime(str(current_month.year), '%Y')
            g.set_title('Minutes Spent on Topics for {} {}'.format(month.strftime('%B'),year.strftime('%Y')))
            g.set(ylabel = 'Time Spent (minutes)')
            plt.tight_layout()
            return fig, total_time
        
        if interval == 'year':
            current_year = date.today().replace(month = 1, day = 1)
            # filter df
            filtered_df = self.tracker_df[self.tracker_df['Date'] >= pd.to_datetime(current_year)]
            # groupby and aggregate
            grouped = filtered_df.groupby(by = 'Topic').agg({'TimeSpent' : 'sum'})
            grouped.reset_index(inplace = True)
            total_time = grouped['TimeSpent'].sum()
            # plot topic and amount of time spent
            fig, ax = plt.subplots(1,1)
            g = sns.barplot(data = grouped, x = 'Topic', y = 'TimeSpent')
            g = annotate_bars(g)
            year = datetime.strptime(str(current_year.year), '%Y')
            g.set_title('Minutes Spent on Topics for {}'.format(year.strftime('%Y')))
            g.set(ylabel = 'Time Spent (minutes)')
            plt.tight_layout()
            return fig, total_time

    def close_tracker(self):
        """
        Save the csv.
        """
        self.tracker_df.to_csv(os.path.join(TRACKER_PATH, self.tracker_file), index = False)
    
if __name__ == '__main__':
    tracker = StudyTracker()
    # topic = input('What topic did you study? \n')
    # timeSpent = int(input('How long did you study? \n')) # should be int for minutes
    # description = input('What did you learn? \n')

    # tracker.add_session(topic, timeSpent, description)
    tracker.summarize_session(interval = 'month')
    tracker.close_tracker()