#import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
import smtplib
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep


def check_availability(site):
    driver = webdriver.Chrome()
    enable_cursor = """
        function enableCursor() {
          var seleniumFollowerImg = document.createElement("img");
          seleniumFollowerImg.setAttribute('src', 'data:image/png;base64,'
            + 'iVBORw0KGgoAAAANSUhEUgAAABQAAAAeCAQAAACGG/bgAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAA'
            + 'HsYAAB7GAZEt8iwAAAAHdElNRQfgAwgMIwdxU/i7AAABZklEQVQ4y43TsU4UURSH8W+XmYwkS2I0'
            + '9CRKpKGhsvIJjG9giQmliHFZlkUIGnEF7KTiCagpsYHWhoTQaiUUxLixYZb5KAAZZhbunu7O/PKf'
            + 'e+fcA+/pqwb4DuximEqXhT4iI8dMpBWEsWsuGYdpZFttiLSSgTvhZ1W/SvfO1CvYdV1kPghV68a3'
            + '0zzUWZH5pBqEui7dnqlFmLoq0gxC1XfGZdoLal2kea8ahLoqKXNAJQBT2yJzwUTVt0bS6ANqy1ga'
            + 'VCEq/oVTtjji4hQVhhnlYBH4WIJV9vlkXLm+10R8oJb79Jl1j9UdazJRGpkrmNkSF9SOz2T71s7M'
            + 'SIfD2lmmfjGSRz3hK8l4w1P+bah/HJLN0sys2JSMZQB+jKo6KSc8vLlLn5ikzF4268Wg2+pPOWW6'
            + 'ONcpr3PrXy9VfS473M/D7H+TLmrqsXtOGctvxvMv2oVNP+Av0uHbzbxyJaywyUjx8TlnPY2YxqkD'
            + 'dAAAAABJRU5ErkJggg==');
          seleniumFollowerImg.setAttribute('id', 'selenium_mouse_follower');
          seleniumFollowerImg.setAttribute('style', 'position: absolute; z-index: 99999999999; pointer-events: none; left:0; top:0');
          document.body.appendChild(seleniumFollowerImg);
          document.onmousemove = function (e) {
            document.getElementById("selenium_mouse_follower").style.left = e.pageX + 'px';
            document.getElementById("selenium_mouse_follower").style.top = e.pageY + 'px';
          };
        };

        enableCursor();
    """
    driver.execute_script(enable_cursor)

    if (site == "texasstateparks"):
        driver.get("https://texasstateparks.reserveamerica.com/unifSearch.do?tti=Home")

        interested_in_select = Select(driver.find_element(By.ID, 'interest'))
        interested_in_select.select_by_value("camping")

        interest_submit = driver.find_element(By.XPATH, '//button[@type="submit"]')
        interest_submit.click()
    if site == "recreation.gov": 
        #opens the site
        driver.get("https://www.recreation.gov/")
        
        driver.maximize_window()

        #scrolls to explore destinations to load it
        ActionChains(driver).scroll_by_amount(0, 1500).perform()
        map_search_container = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "nav-map-search-container-wrapper"))
        )
        ActionChains(driver).scroll_to_element(map_search_container).perform()

        #opens the filter menu
        filter_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "nav-filter-button"))
        )
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(filter_button)
        )
        filter_button.click()

        #when filter menu is open, selects camping
        camping_filter_check = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@for='camping']"))
        )
        camping_filter_check.click()
        filter_button.click()
        sleep(4)
        campgrounds = []

        next_page_button = driver.find_element(By.XPATH, "//button[@aria-label='Go to next page']")

        while(next_page_button.is_enabled()):

            camps = driver.find_elements(By.CLASS_NAME, "nav-map-card-title-wrap")
            for camp in camps:
                campgrounds.append(camp.text)
            
            next_page_button.click()
            #sleep(0)
        
        camps = driver.find_elements(By.CLASS_NAME, "nav-map-card-title-wrap")
        for camp in camps:
            campgrounds.append(camp.text)

        print(campgrounds)
        sleep(30)


check_availability("recreation.gov")