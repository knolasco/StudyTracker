import tkinter as tk
from ttkthemes import themed_tk as thk 
from ttkwidgets import TimeLine
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import Calendar
from datetime import date, datetime
from StudySessionTracker import StudyTracker


# ================================== helper functions =======================================
WIDTH, HEIGHT = 1536, 864


def exit_button(root):
    tk.Button(root, text = 'Press to Exit the Program', command = root.quit).place(x = WIDTH*0.85, y = 10)

def create_calendar(root):
    # add the calendar
    today = date.today()
    cal = Calendar(root, selectmode = 'none',
                year = today.year, month = today.month,
                day = today.day,
                background = 'black',
                showweeknumbers = False,
                borderwidth = 10)
    return cal

def highlight_studied_dates(df, root, cal):
    dates = df['Date'].unique()
    for date in dates:
        # convert the dates to work within the calendar
        date = pd.Timestamp(np.datetime64(date).astype(datetime))
        date = date.to_pydatetime()
        cal.calevent_create(date, 'studied', 'studied')

    cal.tag_config('studied', background = 'green', foreground = 'black')
    cal.place(x = int(WIDTH*0.75), y = 70)
    label = tk.Label(root, text = 'Highlighted Dates = Study Dates')
    label.place(x = int(WIDTH*0.75), y = 40)


def summarize_dropdown(root):
    # create tk variable
    tkvar = tk.StringVar(root)
    # create the dictionary with the different options
    options = {'Day','Week','Month','Year'}
    # set the defaul
    tkvar.set('Day')
    # make the dropdown
    popupMenu = tk.OptionMenu(root, tkvar, *options)
    tk.Label(root, text = 'Choose a time interval',  font = ('Arial', 15)).place(x = WIDTH*0.75, y = 275)
    popupMenu.place(x = WIDTH*0.8, y = 300)

    def change_dropdown(*args):
        """
        update the dropdown option
        """
        show_barplot(root, tkvar.get().lower())

    # link the change
    tkvar.trace('w', change_dropdown)

def format_time(total_time):
    if total_time < 60:
        return str(total_time) + ' minutes'
    else:
        hours, minutes = int(total_time / 60), int(total_time % 60)
        return '{} hours and {} minutes'.format(hours, minutes)

def show_barplot(root, option = 'Day'):
    """
    Draw a barplot based on what the user chooses
    """
    fig, total_time = tracker.summarize_session(interval = option.lower())
    if fig is None:
        pass
    else:
        fig_size = fig.get_size_inches()*fig.dpi
        fig_width, fig_height = fig_size[0], fig_size[1]
        canvas = FigureCanvasTkAgg(fig, master = root)
        canvas.draw()
        canvas.get_tk_widget().place(x = int(WIDTH/2 - fig_width/2), y = 0)
        time_formatted = format_time(total_time)
        if 'time_label' in vars():
            time_label.config(text = 'Total time spent for this interval is {}'.format(time_formatted))
        else:
            time_label = time_label = tk.Label(root, text = 'Total time spent for this interval is {}'.format(time_formatted), font = ('Arial', 15))
            time_label.place(x = int((WIDTH/2 - fig_width/2)*1.2), y = int(fig_height))

def session_entries(root, tracker):
    # declare the string variables
    topic_var = tk.StringVar()
    time_var = tk.StringVar()
    description_var = tk.StringVar()

    def add_session():
        topic = topic_var.get()
        time_spent = int(time_var.get())
        description = description_var.get()
        # add it to the tracker
        tracker.add_session(topic, time_spent, description)
        # update the plot
        show_barplot(root)
        # replace the variables to be blank
        topic_var.set('')
        time_var.set('')
        description_var.set('')

    # make the labels
    FONT = ('Arial', 10, 'bold')
    topic_label = tk.Label(root, text = 'Topic Studied', font = FONT).place(x = 0, y = 0)
    time_label = tk.Label(root, text = 'Amount of Time Studied (minutes)', font = FONT).place(x = 0, y = 20)
    description_label = tk.Label(root, text = 'Description of Study Session', font = FONT).place(x = 0, y = 40)

    # make the entries
    ENTRY_FONT = ('Arial', 10, 'normal')
    topic_entry = tk.Entry(root, textvariable = topic_var, font = ENTRY_FONT).place(x = 300, y = 0)
    time_entry = tk.Entry(root, textvariable = time_var, font = ENTRY_FONT).place(x = 300, y = 20)
    description_entry = tk.Entry(root, textvariable = description_var, font = ENTRY_FONT).place(x = 300, y = 40)

    # add button that will add it to the df
    button = tk.Button(root, text = 'Add Session', command = add_session).place(x = 0, y = 60)

def init_root():
    root = thk.ThemedTk()
    root.set_theme('radiance')
    root.title('Study Tracker')
    # root geometry
    root.geometry('1536x864')
    return root
        

# ===================================== end of helper functions =============================

if __name__ == '__main__':
    # initiate tracker
    tracker = StudyTracker()
    # create the root object
    root = thk.ThemedTk()
    root.set_theme('radiance')
    root.title('Study Tracker')
    # root geometry
    root.geometry('1536x864')

    cal = create_calendar(root)
    highlight_studied_dates(tracker.tracker_df, root, cal)
    summarize_dropdown(root)
    show_barplot(root)
    session_entries(root, tracker)

    # execute tkinter
    exit_button(root)
    root.mainloop()
    # close tracker
    tracker.close_tracker()