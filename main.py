from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime import audio
from fileinput import filename
import os
import time
import playsound
import speech_recognition as sr
import pyttsx3
import pytz
import subprocess

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS= ["january", "febuary", "march", "april", "may", "juny", "july", "august", "september", "october", "november", "december"]
DAYS = ["sunday", "monday", "tuesday", "wensday","thursday", "friday", "sautrday"]



def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))

    return said.lower()
#playsound.playsound('Sound\SETUP\WELCOME.WAV')
'''
text = get_audio()
if "hi" in text:
    speak("hi")
'''

def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_event(day, service):
    # Call the Calendar API
    date  = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date  = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)
    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak("No upcoming events found.")
        print('No upcoming events found.')
        return

    # Prints the start and name of the next 10 events
    for event in events:
        speak(f"You have {len(events)} events on this day.")
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
        start_time = str(start.split("T"[1].split("-")[0]))
        if int(start_time.split(":")[0]) < 12:
            start_time = start_time + "am"
        else:
            start_time = str(int(start_time.split(":")[0]) - 12) +start_time.split(":")[1]
            start_time = start_time +"pm"
        speak(event["summary" + " at " + start_time])

def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today
    
    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
    
    if month < today.month and month != -1:
        year = year + 1

    if day < today.day and month == -1 and day != -1:
        month = month + 1

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)
    if month == -1 or day ==-1:
        return None
    return datetime.date(day=day, month=month, year=year)

def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)
    
    subprocess.Popen(["notepad.exe", file_name])
service = authenticate_google()
WAKE = "hey vabi"
#text = "do i have anything on wensday"

while True:
    print("Start: ")
    text = get_audio()
    if text.count(WAKE) > 0:
        speak("I am Listening")
        text = get_audio()
        
        CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy", "do i have anything on"]
        for phrase in CALENDAR_STRS:
            if phrase in text.lower():
                date = get_date(text)
                if date:
                    get_event(date, service)
                else:
                    speak("Please Try Again")

        NOTE_STRS = ["make a note"]
        for phrase in NOTE_STRS:
            if phrase in text.lower():
                speak("What to write")
                note_text = get_audio()
                note(note_text)
        #print(get_date(text))
        #speak(text)