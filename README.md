# Facebook Group Posts Scraper
A GUI app that allows post scraping from Facebook groups, using keywords to filter relevant posts.

Was mainly developed to assist with finding relevant jobs.

Based on [facebook-scraper](https://github.com/kevinzg/facebook-scraper) by [kevinzg](https://github.com/kevinzg).

## How To Use
To install necessary libraries to run this project:
```
pip install -r requirements.txt
```
To start the GUI app:
```
py main.py
```

## Setting up the app
### Credentials
Inside the GUI app, insert you credentials.

This allows you to scrape from private groups you've joined to.

If save login info is checked, the credentials will be saved in a file once you start scraping, so you won't need to enter them again.

### Groups
Add a Group ID for a group you wanna scrape from.

***How to find a group id?***
Sometimes it will just appear in the url link - ![url example](https://user-images.githubusercontent.com/25244950/154581089-f1c417f2-3901-49af-8d23-4737f9c069e6.png), 
if it doesn't, go into the page source and search for ```fb://group```, the group ID will come right after.

Added groups will be saved in a file, so you'll be able to use them again once you relaunch the app.
You can either remove groups you don't wanna use, or just uncheck them.

### Keywords
Add Keywords to filter posts; 
only posts that contain at least one of the keywords will be returned.

Added keywords will be saved in a file, so you'll be able to use them again once you relaunch the app.
You can either remove keywords you don't wanna use, or just uncheck them.

### Start scraping
After you're done setting up your groups and keywords, you can launch the scraper by pressing the start button.

Once done - an html file will be created, containing all the scraped posts.

***Pay attention!*** If you scrape too much, or scrape from too many groups - facebook may ban you (probably temporarily).
Therefore, use at your own risk.
