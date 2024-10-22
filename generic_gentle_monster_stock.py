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
import threading
import datetime

class GentleMonster():
    def __init__(self,url):
        """Initialize variables """
        self.driver = None
        self.url = url
        self.cappybara_charm = None
        self.cup_piece_charm = None

    def initiate_driver(self):
        """Initialize the selenium web browser and adding options"""
        options = webdriver.ChromeOptions()
        s = Service(r'/usr/lib/chromium-browser/chromedriver')
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        self.driver = webdriver.Chrome(service=s, options=options)
        print("self.driver created")

    def check_out_button_status(self):
        """Checks to see if the button-checkout button is greyed out or not.  If it is greyed out, we return False.  Otherwise, we return True and continue """
        self.driver.get(self.url)
        time.sleep(2)
        try:
            checkout_button = self.driver.find_element(By.ID, "button-checkout")
            print("Checkout Button Found")
            return True
        except:
            print("Check out button not there")
            return False

    def get_glasses(self):
        """Main function to add the charms and the glasses to our shopping cart and will send an email notifying it has been added."""
        self.initiate_driver()
        if self.check_out_button_status() == False:
            print("Checkout button not found. Exiting ")
            exit()

        self.get_charm()

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "button-checkout")))

        add_to_bag = self.driver.find_element(By.ID, "button-checkout")
        print("add_to_bag button found")
        add_to_bag.click()

        element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#cart_group > div.cart_btn_group > div.btn_item.cart_popup_btn.font--rg.font--11 > button')))
        element.click()

        checkout_button = self.driver.find_element(By.CSS_SELECTOR,'#cart_group > div > div.cart_btn_group > div.btn_item.cart_popup_btn.font--rg.font--11 > button')
        print("checkout button clicked")
        checkout_button.click()
        time.sleep(4)

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="login_id"]')))


        """After we click the checkout button, we are lead to a login page to save our order """
        username = self.driver.find_element(By.XPATH, '//*[@id="login_id"]')
        self.driver.execute_script("arguments[0].click();", username)
        time.sleep(1)
        username.send_keys("tester@gmail.com")
        print("username inputted")

        password = self.driver.find_element(By.XPATH, '//*[@id="login_pw"]')
        self.driver.execute_script("arguments[0].click();", password)
        time.sleep(3)
        password.send_keys('password1')
        print("password inputted")

        password.submit()
        time.sleep(3)

        print("shipping address page found")

        self.send_email()


    def send_email(self):
        """Sends an email notifying that the charm and the glasses were added to your account's shopping cart using the smptlib module """
        provider = "smtp.gmail.com"
        smtp0bj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp0bj.login('test@gmail.com', 'test')
        msg = EmailMessage()
        msg.set_content(f"""JENNIE KIM GLITTER GLASSES HAVE BEEN ADDED TO YOUR SHOPPING CART!""")

        msg['Subject'] = '*BUY NOW* GLITTER GLASSES ADDED TO SHOPPING CART'
        msg['From'] = 'test@gmail.com'
        msg['To'] = 'test@gmail.com', 'test@gmail.com'
        print("\n")
        smtp0bj.send_message(msg)
        print("Email sent")

    def get_charm(self):
        """Selenium will locate the cappybara and the cup piece charms and will click on them, adding them to our order  """
        time.sleep(2)

        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="container_sq"]/div[1]/div/div[2]/div/div[4]/div/ul/li[3]')))

        try:
            cappybara = self.driver.find_element(By.XPATH, '//*[@id="container_sq"]/div[1]/div/div[2]/div/div[4]/div/ul/li[3]')
            cappybara.click()
            print("cappybara charm added")
            self.cappybara_charm = True
        except:
            print("cappybara charm NOT added")
            self.cappybara_charm = False

        try:
            cup_piece = self.driver.find_element(By.XPATH,'//*[@id="container_sq"]/div[1]/div/div[2]/div/div[4]/div/ul/li[8]')
            time.sleep(1)
            cup_piece.click()
            print("cup piece charm added")
            self.cup_piece_charm = True
        except:
            print("cup piece charm NOT added")
            self.cup_piece_charm = False

def failure_email():
    """If the code fails in any way while running, it will send a notification through email"""
    provider = "smtp.gmail.com"
    smtp0bj = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp0bj.login('test@gmail.com', 'test')
    msg = EmailMessage()
    msg.set_content(f"""BOT HAS FAILED NEED RESTART""")

    msg['Subject'] = 'BOT JENNY_GLASSES FAILURE'
    msg['From'] = 'testr@gmail.com'
    msg['To'] = 'testk@gmail.com'
    print("\n")
    smtp0bj.send_message(msg)
    print("Email sent")

def main():
    url = 'https://www.gentlemonster.com/us/shop/item/glitter02/DSTWI61J90EM'
    gentle_monster = GentleMonster(url)
    gentle_monster.get_glasses()

schedule.every(1).minutes.do(main)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)

except:
    failure_email()
