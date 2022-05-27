from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from datetime import datetime as dt

# Config
email = "abc@gmail.com"
password = "YourPassword"
search_date = "2022-06-02" # Only the date before the search date will be selected
preferred_location = "Vancouver" # Enter the same text as the website
retry_in_minutes = 25

def search():
  # Initiate the browser
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
  action = webdriver.ActionChains(driver)

  # Go to Sign in page
  driver.get('https://ais.usvisa-info.com/en-ca/niv/users/sign_in') # TODO: The en-ca her can only work for Canadian website. Need to make it configurable.
  
  # Fill credentials
  driver.find_element(by=By.NAME, value="user[email]").send_keys(email)
  driver.find_element(by=By.NAME, value="user[password]").send_keys(password)
  policy = driver.find_element(by=By.CLASS_NAME, value="icheck-label")
  action.move_to_element(policy).move_by_offset(-20, 0).click().perform()
  time.sleep(3)

  # Click Log In
  driver.find_element(by=By.NAME, value="commit").click()
  time.sleep(5)

  # Click Continue
  continue_button = driver.find_element(by=By.XPATH, value='//a[contains(@href, "/continue_actions")]')
  action = webdriver.ActionChains(driver)
  action.move_to_element(continue_button).click().perform()
  time.sleep(2)

  # Click Reschedule
  schedule_id = driver.current_url.split("/")[6]
  reschedule_button = driver.find_element(by=By.XPATH, value="//h5[contains(., 'Reschedule Appointment')]")
  action = webdriver.ActionChains(driver)
  action.move_to_element(reschedule_button).click().perform()
  time.sleep(2)
  continue_button = driver.find_element(by=By.XPATH, value='//a[@href="/en-ca/niv/schedule/' + schedule_id + '/appointment"]')
  action = webdriver.ActionChains(driver)
  action.move_to_element(continue_button).click().perform()
  time.sleep(5)

  # Schedule appointment page
  consular = driver.find_element(by=By.ID, value="appointments_consulate_appointment_facility_id")
  select = Select(consular)
  select.select_by_visible_text(preferred_location)

  date_picker = driver.find_element(by=By.ID, value="appointments_consulate_appointment_date")
  action = webdriver.ActionChains(driver)
  action.move_to_element(date_picker).click().perform()

  # Click next date
  found_clickable_date = False
  clickable_date = None
  count = 0
  while found_clickable_date is False and count < 3:
    driver.implicitly_wait(0)
    try:
      clickable_date = driver.find_element(by=By.XPATH, value="//td[@data-handler='selectDay']")
      found_clickable_date = True
    except NoSuchElementException:
      date_picker_next = driver.find_element(by=By.CLASS_NAME, value="ui-datepicker-next")
      action = webdriver.ActionChains(driver)
      action.move_to_element(date_picker_next).click().perform()
      count += 1

  driver.implicitly_wait(30)


  if found_clickable_date is True and clickable_date is not None:
    action = webdriver.ActionChains(driver)
    action.move_to_element(clickable_date).click().perform()
    time.sleep(2)
    selected_date = dt.strptime(date_picker.get_attribute("value"), "%Y-%m-%d")
    expected_date = dt.strptime(search_date, "%Y-%m-%d")
    print("selected date is: " + selected_date.strftime("%m/%d/%y"))
    print("expected date is: " + expected_date.strftime("%m/%d/%y"))
    if selected_date >= expected_date:
      print("The selected date is too late, skip")
    else:
      time_picker = driver.find_element(by=By.ID, value="appointments_consulate_appointment_time")
      select = Select(time_picker)
      try:
        select.select_by_index(1)
      except NoSuchElementException:
        print("Cannot find selectable time")
        return False
      submit = driver.find_element(by=By.ID, value="appointments_submit")
      action = webdriver.ActionChains(driver)
      action.move_to_element(submit).click().perform()
      confirm = driver.find_element(by=By.XPATH, value="//a[contains(text(), 'Confirm')]")
      action = webdriver.ActionChains(driver)
      action.move_to_element(confirm).click().perform()
      driver.quit()
      print("Rescheduled to " + selected_date.strftime("%m/%d/%y"))
      return True
  else:
    print("Not found")

  driver.quit()
  return False

# Schedule run
while search() is False:
  for i in range(retry_in_minutes):
    print("Retrying in " + str(retry_in_minutes - i) + " minutes")
    time.sleep(60)
