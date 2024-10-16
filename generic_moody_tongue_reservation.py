from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests
import re
import smtplib
import schedule
from email.message import EmailMessage
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Reservation:
    def __init__(self):
        self.url = None
        self.driver = None
        self.availability = None

    def initialize_driver(self):
        #initialize the selenium driver and determine the URL
        self.url = 'https://resy.com/cities/chi/moody-tongue-brewery?seats=2&date=2024-02-07'
        options = webdriver.ChromeOptions()
        s = Service(r'/Users/{}/Documents/python/chromedriver-mac-arm64/chromedriver')
        self.driver = webdriver.Chrome(service=s, options=options)
        print("self.driver created")

    def login_to_resy(self):
        self.initialize_driver()
        self.driver.get(self.url)
        time.sleep(2)
        try:
            # find the login button to get redirected to the login page
            self.driver.find_element(By.CSS_SELECTOR, ".Button--login").click()
            time.sleep(2)
            self.driver.find_element(By.CSS_SELECTOR, ".AuthView__Footer > button:nth-child(1)").click()
            time.sleep(2)
        except:
            raise "Login Button not found "

        try:
            # try to login using email / password credentials
            username = self.driver.find_element(By.NAME, "email")
            username.send_keys("test@gmail.com")
            password = self.driver.find_element(By.NAME, "password")
            password.send_keys("test_password!")
            password.submit()
            print("email info entered")
        except:
            raise "Login input boxes not found"

    def select_calendar_date(self):
        #This function is used to find and click the calendar drop down menu
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#DropdownGroup__selector--date--selection')))
        time.sleep(3)
        self.driver.find_element(By.CSS_SELECTOR, '#DropdownGroup__selector--date--selection').click()
        print("Drop down menu found")
        while True:
            # we are looking for dates in March, so it will keep cycling through the months until it reaches August 2024
            time.sleep(1)
            month = self.driver.find_element(By.CSS_SELECTOR, '.CalendarMonth__Title')
            if month.text != "March 2024":
                self.driver.find_element(By.CSS_SELECTOR,
                                         '#DayPicker > div.DayPicker__navigation > button.ResyCalendar__nav_right.Button.Button--primary.Button--circle').click()
                continue
            break

    def determine_march_availability(self):
        self.availability = {}
        self.select_calendar_date()
        # we are looking for the elements for March 29th, 30th, 31st and will first check to see if the button is greyed out which indicates the date is not open yet
        # if the date is open, we will click into it and check to see the reservation times for the dining room
        # the dates and their available times are stored within the self.availability dictionary
        #March 29th
        try:
            march_twenty_nine = self.driver.find_element(By.CSS_SELECTOR,'tr.CalendarMonth__Row:nth-child(5) > td:nth-child(5) > button:nth-child(1)')
        except:
            raise "march_twenty_nine element not found "

        if march_twenty_nine.get_attribute("disabled") == None:
            march_twenty_nine.click()
            print("Here are the available set menu times for August 29th:")
            times = self.check_reservation_times()
            self.availability["March 29th"] = times
        elif (march_twenty_nine.get_attribute("disabled")) == 'true':
            print("March 29th is unavailable")
            self.availability["March 29th"] = None
        time.sleep(3)
        #March 30th
        try:
            march_thirty = self.driver.find_element(By.CSS_SELECTOR,'tr.CalendarMonth__Row:nth-child(5) > td:nth-child(6) > button:nth-child(1)')
        except:
            raise "march_thirty element not found "
        if march_thirty.get_attribute("disabled") == None:
            march_thirty.click()
            print("Here are the available set menu times for March 30th:")
            times = self.check_reservation_times()
            self.availability["March 30th:"] = times
        elif (march_thirty.get_attribute("disabled")) == 'true':
            print("March 30th is unavailable")
            self.availability["March 30th"] = None
        time.sleep(3)

        #March 31st
        try:
            march_thirty_first = self.driver.find_element(By.CSS_SELECTOR,'tr.CalendarMonth__Row:nth-child(5) > td:nth-child(7) > button:nth-child(1)')
        except:
            raise "march_thirty_first element not found "
        if march_thirty_first.get_attribute("disabled") == None:
            march_thirty_first.click()
            times = self.check_reservation_times()
            self.availability["March 31st:"] = times
        elif (march_thirty_first.get_attribute("disabled")) == 'true':
            print("March 31st is unavailable")
            self.availability["March 31st:"] = None


    def check_reservation_times(self):
        time.sleep(1)
        dining_room = self.driver.find_elements(By.XPATH,
                                                "//div[@class='ReservationButton__type' and text()='The Dining Room']")
        if dining_room == []:
            print("There are no available times")
            return None
        time.sleep(1)
        dining_room_times = self.driver.find_elements(By.XPATH, "//div[@class='ReservationButton__time']")
        times = []
        for i in range(len(dining_room_times)):
            list = dining_room_times[i].find_elements(By.XPATH, "//div[@class='ReservationButton__type']")
            if "The Dining Room" == list[i].text:
                times.append(dining_room_times[i].text)
        return times

    def send_email(self):
        # we are checking to see if any of the three days have any available times
        # if there are no available times, we do not send an email
        available_times = False
        for date, times in self.availability.items():
            if times != None:
                available_times = True

        if available_times == True:
            provider = "smtp.gmail.com"
            smtp0bj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            msg = EmailMessage()
            msg.set_content(f"""Hello Ethan, 
               \nThis is your daily report on the availability of Moody Tongue
               \n{self.availability}""")

            msg['Subject'] = 'MOODY TONGUE AVAILABILITY'
            msg['From'] = 'test@gmail.com'
            msg['To'] = 'tester@gmail.com'
            smtp0bj.login('test@gmail.com', 'password!')
            print("\n")
            smtp0bj.send_message(msg)
            print("Email sent")
        return

def main():
    reservation = Reservation()
    reservation.login_to_resy()
    reservation.determine_march_availability()
    reservation.send_email()

if __name__ == "__main__":
    main()