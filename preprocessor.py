import re
import pandas as pd

def preprocess(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s(?:AM|PM|am|pm)\s-\s'
    data = data.replace('\u202F', ' ').replace('\xa0', ' ').strip()
    messages = re.split(pattern, data)[1:]  # Messages
    dates = re.findall(pattern, data)  # Timestamps
    dates = [date.strip() for date in dates]
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert msg_date to datetime format
    try:
        df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %I:%M %p - ')
    except ValueError as e:
        print("Error in datetime conversion:", e)

    # Rename column
    df.rename(columns={'message_date': 'date'}, inplace=True)
    users = []  # List to store usernames
    messages = []  # List to store messages

    for message in df['user_message']:  # Rename loop variable to avoid conflict
        entry = re.split(r'(\w+):\s', message)
        if len(entry) > 1:  # If a username exists
            users.append(entry[1])  # Add the username to the users list
            messages.append(entry[2])  # Add the message to the messages list
        else:
            users.append('group_notification')  # For system messages
            messages.append(entry[0])  # Add the full message to the messages list

    # Add extracted users and messages to the DataFrame
    df['user'] = users
    df['message'] = messages

    # Drop the original user_msg column
    df.drop(columns=['user_message'], inplace=True)
    df['date'] = df['date'].str.replace(' -$', '', regex=True)

    # Convert to datetime format
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y, %I:%M %p', errors='coerce')

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()

    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['am_pm'] = df['date'].dt.strftime('%p')  # AM/PM

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df


