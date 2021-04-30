"""
UNSPLASH.COM SCRAPER

This program will crawl the landing page of unsplash.com, a creative commons image hosting site
and collected attributes about the images found there.

@author: Reis Gadsden
@version: v2.0.2

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
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd


# main class that contains the logic for crawling unsplash
class UnsplashScrape:
    base = ""  # main page
    crawl_amount = 0  # total pages to be crawled
    driver = ""  # initialize driver variable
    main_window = 0  # value that will hold the window value of the main page
    MAX_PAGES = 1000  # max number of pages allowed to be crawled

    # initialization function of the UnsplashScrape class
    # handles user input, sets values to class wide variables, sets Firefox profile,
    # and makes call to main data collection function
    def __init__(self, main_site, crawl_pages):
        self.base = main_site

        # empty lists to hold all data
        self.img_page = []
        self.img_hvr_txt = []
        self.photographer = []
        self.img_url = []
        self.location = []
        self.summary = []
        self.views = []
        self.downloads = []
        self.camera_make = []
        self.camera_model = []
        self.focal_len = []
        self.aperture = []
        self.shutter_speed = []
        self.iso = []
        self.img_resolution = []
        self.count = []

        # get and validate user input
        self.check_input = True
        while True:
            if int(crawl_pages) > self.MAX_PAGES or int(crawl_pages) < 1:
                print("Requested Crawl Amount Too Large (Limit is " + str(self.MAX_PAGES) + ")")
                self.check_input = False
                break
            else:
                print("Okay gathering " + str(crawl_pages) + " item(s) from " + self.base + ".")
                self.crawl_amount = int(crawl_pages)

                # initialize selenium with custom profile
                profile = webdriver.FirefoxProfile()
                profile.set_preference("dom.disable_open_during_load", False)
                self.driver = webdriver.Firefox(firefox_profile=profile)
                self.driver.set_page_load_timeout(30)
                self.driver.get(self.base)
                self.main_window = self.driver.current_window_handle

                # call to main data collection function
                self.get_attrs()

                # create a dictionary that can be converted to a DataFrame
                self.data = {
                    "img_page": self.img_page,
                    "img_hvr_txt": self.img_hvr_txt,
                    "photographer": self.photographer,
                    "img_url": self.img_url,
                    "location": self.location,
                    "summary": self.summary,
                    "views": self.views,
                    "downloads": self.downloads,
                    "camera_make": self.camera_make,
                    "camera_model": self.camera_model,
                    "focal_len": self.focal_len,
                    "aperture": self.aperture,
                    "shutter_speed": self.shutter_speed,
                    "iso": self.iso,
                    "img_resolution": self.img_resolution,
                    "count": self.count
                }

                # convert to dataframe
                self.df = pd.DataFrame.from_dict(self.data)

                # save dataframe as csv
                self.df.to_csv("data/data.csv", index=False)
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

        i = 1
        for url in urls:
            print(str(i) + ". Collecting info from: " + url)
            # initialize page data container
            # only attribute that does not require you to go to the actual photo page
            self.img_hvr_txt.append(self.get_image_hover(url))

            # collects all attributes from photo page and merges them with page data container
            self.img_page.append(url)
            self.get_info(url)
            # closes the newly opened window and switches driver back to main window
            for window in self.driver.window_handles:
                if window != self.main_window:
                    self.driver.switch_to.window(window)
                    self.driver.close()
                    self.driver.switch_to.window(self.main_window)
                    break
            i += 1

        # closes the driver
        self.driver.quit()

    # gets the text that occurs when you hover over and image on the main page
    def get_image_hover(self, url):
        element_to_go_to = self.driver.find_element_by_xpath("//*[@href='" + url.replace(self.base, "/") + "']")
        self.driver.execute_script("arguments[0].scrollIntoView();", element_to_go_to)
        ActionChains(self.driver).move_to_element(element_to_go_to).perform()

        if element_to_go_to.get_attribute('title') is None or element_to_go_to.get_attribute('title') == "":
            return None
        else:
            return element_to_go_to.get_attribute('title')

    # method that gathers data from the individual photo pages
    def get_info(self, url):
        # opens photo page up in new tab
        self.driver.execute_script('window.open("' + url + '");')

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
                self.photographer.append(val.get_attribute("href").replace("https://unsplash.com/@", ""))
                break

        # loop to find the image url
        # thorough checking to make sure the right link is gathered
        # sometimes the image wont load fast enough so if the element go stale
        # a.k.a not loaded yet it will wait two seconds and attempt to get it again
        try:
            for val in self.driver.find_elements_by_css_selector("img"):
                if val.get_attribute('itemprop') != "thumbnailUrl" and "1pixel.gif" not in val.get_attribute("src")\
                        and val.get_attribute("role") is None:
                    self.img_url.append(val.get_attribute('src'))
                    break
        except StaleElementReferenceException:
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_all_elements_located((By.CSS_SELECTOR, 'img')))
            for val in self.driver.find_elements_by_css_selector("img"):
                if val.get_attribute('itemprop') != "thumbnailUrl" and "1pixel.gif" not in val.get_attribute("src")\
                        and val.get_attribute("role") is None:
                    self.img_url.append(val.get_attribute('src'))
                    break

        # attempts to get a location if one is provided
        # have to handle and exception here because there is only one possible element that could match
        # so we have to handle the exception that is thrown if it is not present
        try:
            self.location.append(self.driver.find_element_by_css_selector("a[href^='/s/photos'] > span").text)
        except NoSuchElementException:
            self.location.append(None)

        # collect the summary if present
        # the only other <p> tags are ones leading to related content
        # so we can check for those
        # might cause and issue where the word Related is in the summary
        check_sum = None
        for val in self.driver.find_elements_by_css_selector("p"):
            if "Related" not in val.text:
                check_sum = val.text
                break
        self.summary.append(check_sum)

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

        self.views.append(int((self.driver.find_element_by_xpath('//*[text()="Views"]/../following-sibling::dd/span[1]')
                          .text.replace(",", ""))))

        self.downloads.append(int(
            self.driver.find_element_by_xpath('//*[text()="Downloads"]/../following-sibling::dd/span[1]')
                .text.replace(",", "")))

        check_camera_make = self.driver.find_element_by_xpath('//*[text()="Camera Make"]/following-sibling::dd').text
        if check_camera_make == "--":
            self.camera_make.append(None)
        else:
            self.camera_make.append(check_camera_make)

        check_camera_model = self.driver.find_element_by_xpath('//*[text()="Camera Model"]/following-sibling::dd').text
        if check_camera_model == "--":
            self.camera_model.append(None)
        else:
            self.camera_model.append(check_camera_model)

        check_focal_len = self.driver.find_element_by_xpath('//*[text()="Focal Length"]/following-sibling::dd').text
        if check_focal_len == "--":
            self.focal_len.append(None)
        else:
            self.focal_len.append(float(check_focal_len.replace("mm", "")))

        check_aperture = self.driver.find_element_by_xpath('//*[text()="Aperture"]/following-sibling::dd').text
        if check_aperture == "--":
            self.aperture.append(None)
        else:
            self.aperture.append(float(check_aperture.replace("\u0192/", "")))

        # create shutter speed as a float instead of fraction in string format
        check_shutter_speed = self.driver.find_element_by_xpath(
            '//*[text()="Shutter Speed"]/following-sibling::dd').text
        if check_shutter_speed == "--":
            self.shutter_speed.append(None)
        else:
            check_shutter_speed = check_shutter_speed.replace("s", "")
            if len(check_shutter_speed.split("/")) == 2:
                check_shutter_speed = check_shutter_speed.split('/')
                check_shutter_speed = float(check_shutter_speed[0]) / float(check_shutter_speed[1])
            self.shutter_speed.append(float(check_shutter_speed))

        check_iso = self.driver.find_element_by_xpath('//*[text()="ISO"]/following-sibling::dd').text
        if check_iso == "--":
            self.iso.append(None)
        else:
            self.iso.append(int(check_iso))

        check_img_res = self.driver.find_element_by_xpath('//*[text()="Dimensions"]/following-sibling::dd').text
        if check_img_res == "--":
            self.img_resolution.append(None)
        else:
            check_img_res = check_img_res.replace(" × ", ", ")
            self.img_resolution.append(check_img_res)

        # add 1 to count in order to keep a total of images when combining rows and such later on
        self.count.append(1)


# will run the scraper if this is main file and it is not being imported
if __name__ == "__main__":
    while True:
        crawl_amount = input("Enter the number you would like to crawl too.")
        try:
            crawl_amount = int(crawl_amount)
        except ValueError:
            print("Invalid Input, Try Again!")
        else:
            if crawl_amount > 0:
                us = UnsplashScrape("https://unsplash.com/", crawl_amount)
                if us.check_input:
                    break
                else:
                    print("Please enter a new value.")
            else:
                print("Invalid Input, Try Again!")
