"""
UNSPLASH.COM SCRAPER

This program will crawl the landing page of unsplash.com, a creative commons image hosting site
and collected attributes about the images found there.

@author: Reis Gadsden
@version: v0.0.1

Attributes Scraped:
 - Image page url
 - Photographer
 - Image url
 - Location (if given)
 - Summary (if given)
 - Total views
 - Total downloads
 - Camera Make (if given)
 - Camera model (if given)
 - Focal Length (if given)
 - Aperture (if given)
 - Shutter Speed (if given)
 - ISO (if given)
 - Image resolution

Base link: https://unsplash.com

Additional Work Done:
- Implemented Regex
- Handle cases where information was not available
- Dynamically crawled the website, allowing for navigation of elements that is unlikely to be
    deprecated in the near future
- Gathered more then 100 pages
- Gathered more then 5 pieces of information
- Ethically Crawled with long delays
- Waited for items to appear
- Scrolled to desired item
- Preloaded desired items
- Hover over an item
- Implemented JavaScript
- Implemented user input

Additional Resources:
- https://stackoverflow.com/questions/41744368/scrolling-to-element-using-webdriver
- https://stackoverflow.com/questions/48850974/selenium-scroll-to-end-of-page-in-dynamically-loading-webpage
"""

# necessary imports
import json
import re
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains


# main class that contains the logic for crawling unsplash
class UnsplashScrape:
    base = ""  # main page
    attrs = dict()  # dictionary that contains all attributes
    crawl_amount = 0  # total pages to be crawled
    driver = ""  # initialize driver variable
    main_window = 0  # value that will hold the window value of the main page

    # initialization function of the UnsplashScrape class
    # handles user input, sets values to class wide variables, sets Firefox profile,
    # and makes call to main data collection function
    def __init__(self, main_site):
        self.base = main_site

        # get and validate user input
        while True:
            self.crawl_amount = input("Please enter the number of items you would like to retrieve (limit 1,000): ")
            if bool(re.match(r'^[0-9]+$', self.crawl_amount)) is not True or int(self.crawl_amount) > 1000 \
                    or int(self.crawl_amount) < 1:
                print("Please enter a valid integer in the range of 1 - 1,000!")
            else:
                print("Okay gathering " + self.crawl_amount + " item(s) from " + self.base + ".")
                self.crawl_amount = int(self.crawl_amount)

                # initialize selenium with custom profile
                profile = webdriver.FirefoxProfile()
                profile.set_preference("dom.disable_open_during_load", False)
                self.driver = webdriver.Firefox(firefox_profile=profile)
                self.driver.set_page_load_timeout(30)
                self.driver.get(self.base)
                self.main_window = self.driver.current_window_handle

                # call to main data collection function
                self.get_attrs()
                break

    # main data collection function
    def get_attrs(self):
        # this will scroll down the starting page loading elements until the desired
        # amount of items are loaded
        while True:
            # scroll to bottom of page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # gives time for new elements to load
            WebDriverWait(self.driver, 30).until(
                ec.presence_of_all_elements_located((By.XPATH, "//*[@itemprop='contentUrl']")))
            time.sleep(1)

            # gets all loaded elements and checks to see if the user defined crawl amount has been reached
            figures = self.driver.find_elements_by_xpath("//*[@itemprop='contentUrl']")
            if len(figures) >= self.crawl_amount:
                break

        # gets urls from loaded elements
        urls = [fig.get_attribute('href') for fig in figures[0:self.crawl_amount]]

        for url in urls:
            print(str(len(self.attrs)+1) + ". Collecting info from: " + url)
            # initialize page data container
            collected_attrs = dict()
            # only attribute that does not require you to go to the actual photo page
            collected_attrs["image_hover_text"] = self.get_image_hover(url)

            # collects all attributes from photo page and merges them with page data container
            collected_attrs.update(self.get_info(url))
            self.attrs[url] = collected_attrs

            # closes the newly opened window and switches driver back to main window
            for window in self.driver.window_handles:
                if window != self.main_window:
                    self.driver.switch_to.window(window)
                    self.driver.close()
                    self.driver.switch_to.window(self.main_window)
                    break

        # dumps final dictionary to a .json file
        self.dump_to_json()

        # closes the driver
        self.driver.quit()

    # gets the text that occurs when you hover over and image on the main page
    def get_image_hover(self, url):
        element_to_go_to = self.driver.find_element_by_xpath("//*[@href='" + url.replace(self.base, "/") + "']")
        self.driver.execute_script("arguments[0].scrollIntoView();", element_to_go_to)
        ActionChains(self.driver).move_to_element(element_to_go_to).perform()
        return element_to_go_to.get_attribute('title')

    # method that gathers data from the individual photo pages
    def get_info(self, url):
        # opens photo page up in new tab
        self.driver.execute_script('window.open("' + url + '");')

        # data collection container
        collection_info = dict()

        # switches driver form main window to new window
        for window in self.driver.window_handles:
            if window != self.main_window:
                self.driver.switch_to.window(window)
                break

        # time delay to give elements time to load and to not overload the server
        time.sleep(1)
        WebDriverWait(self.driver, 10).until(
            ec.presence_of_all_elements_located((By.XPATH, '//*[text()="Info"]')))

        # loop to find photographers name
        # thorough checking to make sure the right thing is gathered
        for val in self.driver.find_elements_by_css_selector("a[href^='/@']"):
            if val.text.strip() != "" and val.text.strip() != "Available for hire":
                collection_info["photographer"] = val.text.strip()

        # loop to find the image url
        # thorough checking to make sure the right link is gathered
        # sometimes the image wont load fast enough so if the element go stale
        # a.k.a not loaded yet it will wait two seconds and attempt to get it again
        try:
            for val in self.driver.find_elements_by_css_selector("img"):
                if val.get_attribute('itemprop') != "thumbnailUrl" and "1pixel.gif" not in val.get_attribute("src")\
                        and val.get_attribute("role") is None:
                    collection_info["img_url"] = val.get_attribute('src')
        except StaleElementReferenceException:
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'img')))
            for val in self.driver.find_elements_by_css_selector("img"):
                if val.get_attribute('itemprop') != "thumbnailUrl" and "1pixel.gif" not in val.get_attribute("src")\
                        and val.get_attribute("role") is None:
                    collection_info["img_url"] = val.get_attribute('src')

        # attempts to get a location if one is provided
        # have to handle and exception here because there is only one possible element that could match
        # so we have to handle the exception that is thrown if it is not present
        try:
            collection_info["location"] = self.driver.find_element_by_css_selector("a[href^='/s/photos'] > span").text
        except NoSuchElementException:
            collection_info["location"] = "N/A"

        # collect the summary if present
        # the only other <p> tags are ones leading to related content
        # so we can check for those
        # might cause and issue where the word Related is in the summary
        collection_info["summary"] = "N/A"
        for val in self.driver.find_elements_by_css_selector("p"):
            if "Related" not in val.text:
                collection_info["summary"] = val.text
                break

        # click the info button
        try:
            info_button = self.driver.find_element_by_xpath('//*[text()="Info"]').find_element_by_xpath("..")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", info_button)
            info_button.click()
            # wait to make sure that the stuff under the info button actually loads
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_all_elements_located((By.XPATH, '//*[text()="Views"]/../following-sibling::dd/span[1]')))
        except TimeoutException:
            time.sleep(2)
            info_button = self.driver.find_element_by_xpath('//*[text()="Info"]').find_element_by_xpath("..")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", info_button)
            info_button.click()
            # wait to make sure that the stuff under the info button actually loads
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_all_elements_located((By.XPATH, '//*[text()="Views"]/../following-sibling::dd/span[1]')))

        # everything under the info tab is basically formatted the same
        # it has a title for what it is in the dt tag with some text so we can just
        # get the second sibling of its parent node

        collection_info["views"] = int(self.driver.find_element_by_xpath
                                       ('//*[text()="Views"]/../following-sibling::dd/span[1]').text.replace(",", ""))

        collection_info["downloads"] = int(
            self.driver.find_element_by_xpath('//*[text()="Downloads"]/../following-sibling::dd/span[1]')
                .text.replace(",", ""))

        collection_info["camera_make"] = self.driver.find_element_by_xpath(
            '//*[text()="Camera Make"]/following-sibling::dd').text
        if collection_info["camera_make"] == "--":
            collection_info["camera_make"] = "N/A"

        collection_info["camera_model"] = self.driver.find_element_by_xpath(
            '//*[text()="Camera Model"]/following-sibling::dd').text
        if collection_info["camera_model"] == "--":
            collection_info["camera_model"] = "N/A"

        collection_info["focal_len"] = self.driver.find_element_by_xpath(
            '//*[text()="Focal Length"]/following-sibling::dd').text
        if collection_info["focal_len"] == "--":
            collection_info["focal_len"] = "N/A"

        collection_info["aperture"] = self.driver.find_element_by_xpath(
            '//*[text()="Aperture"]/following-sibling::dd').text
        if collection_info["aperture"] == "--":
            collection_info["aperture"] = "N/A"

        collection_info["shutter_speed"] = self.driver.find_element_by_xpath(
            '//*[text()="Shutter Speed"]/following-sibling::dd').text
        if collection_info["shutter_speed"] == "--":
            collection_info["shutter_speed"] = "N/A"

        collection_info["iso"] = self.driver.find_element_by_xpath(
            '//*[text()="ISO"]/following-sibling::dd').text
        if collection_info["iso"] == "--":
            collection_info["iso"] = "N/A"

        collection_info["img_resolution"] = self.driver.find_element_by_xpath(
            '//*[text()="Dimensions"]/following-sibling::dd').text
        if collection_info["img_resolution"] == "--":
            collection_info["img_resolution"] = "N/A"

        # return the final dictionary
        return collection_info

    def dump_to_json(self):
        # attempts to dump to json file
        try:
            with open('data.json', 'w') as fp:
                json.dump(self.attrs, fp, indent=4)
            fp.close()
        except json.JSONDecodeError:
            print("Error dumping to JSON file :(")
        else:
            print("\nSuccessfully dumped dictionary to a JSON file!")


# will run the scraper if this is main file and it is not being imported
if __name__ == "__main__":
    UnsplashScrape("https://unsplash.com/")
