from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import re


##TODO: Fix formatting for numbers greater that 1000 since they apear with a comma and can't be converted to floats.


class WebElementWrapper:
    def __init__(self, driver, by, value):
        self.driver = driver
        self.locator = (by, value)
        self.element = None

    def find_element(self):
        """Attempt to find the element using the stored locator."""
        self.element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.locator)
        )

    def get_text(self):
        """Safely get text from the element, handling stale elements."""
        try:
            if not self.element:
                self.find_element()
            return self.element.text
        except StaleElementReferenceException:
            # Element is stale, find it again and retry the action
            self.find_element()
            return self.element.text

    def click(self):
        """Safely click the element, handling stale elements."""
        try:
            if not self.element:
                self.find_element()
            self.element.click()
        except StaleElementReferenceException:
            # Element is stale, find it again and retry the action
            self.find_element()
            self.element.click()


def check_exists(driver, locator):
    try:
        driver.find_element(locator[0], locator[1])
    except NoSuchElementException:
        return False
    return True

def get_tooltip_info(driver, element):
    #hover on element
    ActionChains(driver).move_to_element(element).perform()

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "tooltip"))
    )
    name = WebElementWrapper(driver, By.CSS_SELECTOR, "#tooltip  .name").get_text()
    price = WebElementWrapper(driver, By.CSS_SELECTOR, "#tooltip .price").get_text()
    owned = WebElementWrapper(driver, By.CSS_SELECTOR, "div#tooltip .tag").get_text().split(": ")[1]
    description = WebElementWrapper(driver, By.CSS_SELECTOR, "div#tooltip .description q").get_text()
    if int(owned) == 0:
        production_details = 0
    else:
        production_details = float(re.findall(r'\b\d+\.?\d*\b', WebElementWrapper(driver, By.CSS_SELECTOR, "#tooltip .descriptionBlock").get_text())[0])

    details = {
        "name": name,
        "price": int(price.replace(',', '')),
        "owned": int(owned),
        "description": description,
        "production": production_details
    }
    return details

def best_to_buy_d1(prod_rate, d1, d2):
    total = 0
    p1 = d1["price"]
    p2 = d2["price"]
    m1 = d1["production"]
    m2 = d2["production"]
    '''
    #This is just buying infinite grandmas for some reason?
    for j in range(1, int(m2/m1)+2):
        total += prod_rate/(prod_rate+((j-1)*m2))
    
    if p2 < p1/total:
        return False
    else:
        return True
    '''

    if m1/p1 > m2/p2:
        return True
    else:
        return False


#returns ID of best unlock
def check_best_unlock(driver, prod_rate, product_list):
    product_details = []
    best_unlock_number = 0
    best_unlock_id = "product0"
    for product in product_list:
        product_info = get_tooltip_info(driver, product)
        product_details.append(product_info)
    
    for k in range(len(product_details)-1):
        if product_details[k+1]["owned"] == 0:
            if product_details[k+1]["price"] < 2.5*product_details[k]["price"]:
                best_unlock_id = "product"+str(k+1)
        else:
            if best_to_buy_d1(prod_rate, product_details[best_unlock_number], product_details[k+1]):
                continue
            else: 
                best_unlock_number = k+2
                best_unlock_id = "product" + str(k+1)
    return best_unlock_id


def get_stable_prod_rate(driver, locator):
    attempts = 0
    while attempts < 5:  # You can adjust the number of retries
        try:
            # Wait for the element to be present and then try to get its text
            element = WebElementWrapper(driver, locator[0], locator[1])
            text = element.get_text().split(": ")[1]
            return text  # If successful, return the text
        except StaleElementReferenceException:
            attempts += 1
            print(f"Attempt {attempts}: Stale element reference, retrying...")
        except Exception as e:
            print(f"Error during text retrieval: {e}")
            break


def Play_game(url):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.maximize_window()

    #first we select the language

    english_button = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "langSelect-EN"))
    )
    english_button.click()

    dismiss_cookies_button = WebDriverWait(driver, 10, ignored_exceptions=StaleElementReferenceException).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@data-cc-event='click:dismiss']"))
    )
    dismiss_cookies_button.click()
    sleep(3)
    dismiss_save_button =  WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//a[@onclick='Game.prefs.showBackupWarning=0;Game.CloseNote(1);']"))
    )
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(dismiss_save_button)
    )
    dismiss_save_button.click()

    bakery_name_input = driver.find_element(By.ID, "bakeryName")
    ActionChains(driver).click(bakery_name_input).send_keys("Selene").send_keys(Keys.RETURN).perform()

    def click_cookie():
        big_cookie = driver.find_element(By.ID, "bigCookie")
        big_cookie.click()




    def game_loop():
        i = 0
        store = driver.find_element(By.ID, "store")
        purchase_interval = 80
        best_unlock_id = "product0"

        while i < 500000:
            if (i % purchase_interval == 0 and i > 100):
                prod_rate = float(get_stable_prod_rate(driver, (By.ID, "cookiesPerSecond")))
                unlocked_unlocks = driver.find_elements(By.CSS_SELECTOR, "div.product.unlocked")
                best_unlock_id = check_best_unlock(driver, prod_rate, unlocked_unlocks)

            if check_exists(driver, (By.XPATH, "//div[@alt='Golden cookie']")):
                golden_cookie = driver.find_element(By.XPATH, "//div[@alt='Golden cookie']")
                ActionChains(driver).move_to_element_with_offset(golden_cookie, 30, 30).click().perform()
            elif check_exists(driver, (By.CSS_SELECTOR, "div.framed.close.sidenote")):
                close_achievements_button = driver.find_element(By.CSS_SELECTOR, "div.framed.close.sidenote")
                close_achievements_button.click()
           
            elif (check_exists(driver, (By.CSS_SELECTOR, "div.crate.upgrade.enabled")) and (i % purchase_interval == 0)):
                purchase_best_upgrade_button = driver.find_elements(By.CSS_SELECTOR, "div.crate.upgrade.enabled")
                if len(purchase_best_upgrade_button) > 0:
                    purchase_best_upgrade_button = purchase_best_upgrade_button[-1]
                    ActionChains(driver).move_to_element(store).scroll_to_element(purchase_best_unlock_button).click(purchase_best_upgrade_button).perform()
            
            elif (check_exists(driver, (By.CSS_SELECTOR, "div#" + best_unlock_id + ".product.unlocked.enabled")) and (i % purchase_interval == 0)):
                purchase_best_unlock_button = driver.find_element(By.CSS_SELECTOR, "div#" + best_unlock_id + ".product.unlocked.enabled")
                ActionChains(driver).move_to_element(store).scroll_to_element(purchase_best_unlock_button).click(purchase_best_unlock_button).perform()
            else:
                click_cookie()
            i += 1    
    game_loop()

    sleep(30)


Play_game("https://orteil.dashnet.org/cookieclicker/")