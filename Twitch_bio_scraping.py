import time
from selenium import webdriver



driver = webdriver.Chrome('C:/Users/gianl/Desktop/chromedriver.exe')  # Optional argument, if not specified will search path.

driver.get('http://www.google.it/')

time.sleep(5) # Let the user actually see something!

search_box = driver.find_element_by_name('q')

search_box.send_keys('un po di figa qua')

search_box.submit()

time.sleep(5) # Let the user actually see something!

driver.quit()
