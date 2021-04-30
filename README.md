# Welcome to the Unsplash Scrape Visualizer Documentation

By: Reis Gadsden\
Version: v2.0.0\
<a href="https://github.com/reismgadsden/UnsplashScrape">GitHub</a>

#1. Overview
This program gathers 15 different attributes for a specified number of photos from the royalty free image hosting website, Unsplash. There are two major parts of the program. The first is the actual crawling and gathering of data, done via Selenium. The second is the visualization of data gathered from the crawl utilizing Pandas, Numpy, and MatPlotLib.
* Gathered attributes
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
    
<br/>
Visualizations created during the crawl include:
<ul>
<li>Top 10 Users by View</li>
<li>Average Views and Downloads by Camera Make and Model</li>
<li>Graphs showing Camera Settings</li>
</ul>
Additional features include
<ul>
<li>Viewing the most popular image</li>
<li>Creating a perfect "camera" based of view averages</li>
</ul>
   
# 2. Neccesary Imports
* Pandas
* datetime
* time
* NumPy
* warnings
* webbrowser
* Matplotlib
    * pyplot
    * ticker
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
      * expected_conditions
      
# 3. Running the Program
Running the program is simple. You can simply run <i>UnsplashScrapeVisualizer.py</i>, given that you have installed the necessary imports. On start you will have the option to either load data from a included csv, or start a new scrape (WARNING: NEW SCRAPE TAKES AN AVERAGE OF 45 MINUTES TO COMPLETE FOR 1000 IMAGES)
<br/>
<br/>
If you are only looking for the data rather then the visualizations, you can run <i>UnsplashScrape.py</i>. You might have to change a few lines in order to get the number of pages and data output that you want but it shouldn't be too much.

# 4. Data Output
All data is outputted to a folder called data, in there you will find all plots in a png format as well as a csv created from the data.
