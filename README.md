# UnsplashScrape Documentation

By: Reis Gadsden
Version: v1.0.1

# This documentation is incomplete and does not cover everything except an initial setup and describing programs fuctionality.

# 1. Purpose
The purpose of this documentation is to crawl and gather several bits of data from the royalty free image sharing website <b><a href = "https://unsplash.com">unsplash.com</a></b>. It will gather said data and store it in a formatted .json file, data.json.
*Gathered attributes
  * Image Page URL - Each image has its own unique webpage
  * Photographer - the account name of the person which the photo belongs to
  * URL of the Image - the direct url of the image (img.src)
  * Total views
  * Total downloads
  * Resoltuion of the image
  * Some images contain extra optional info, these are gathered as well, if provided:
    * Location - Geographical location where the image was taken
    * Summary - sometimes the artist will provide a sentence describing the photo
    * Camera Make
    * Camera Model
    * Focal Length
    * Aperture
    * Shutter Speed
    * ISO
    
# 2. Neccesary Imports
* json
* re
* time
* selenium
  * webdriver
    * common
      * exceptions
        * NoSuchElementException
        * StaleElementReferenceException
        * TimeoutException
      * by.BY
      * action_chains.ActionChains
    * support
      * ui.WebDriverWait
      * expected_conditions as ec
      
# 3. First Time Running
Upon the first time running a prompt in the console will display
<pre><code>Please enter the number of items you would like to retrieve (limit 1,000): </code></pre>
You may enter any valid integer value up to 1,000. If you would like to retrieve more items, you can simply change the value of MAX_PAGES to whatever you would like. It was kept at 1,000 for brevity.
