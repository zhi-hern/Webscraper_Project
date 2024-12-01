import logging
import agentql
from playwright.sync_api import sync_playwright
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


URL = "https://www.propertyguru.com.sg/property-for-rent/1?_freetextDisplay=yishun&freetext=yishun"
results = []


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = agentql.wrap(browser.new_page())
    page.goto(URL)


    LISTING_QUERY = """
    {
        listings_q[] {
            listing_title
            listing_location
            listing_price 
            listing_sqft 
            listing_link
        }
    }
    """
 
    for x in range(2, 25):

        # Scroll down the page to load
        for _ in range(16):
            page.keyboard.press("PageDown")
            page.wait_for_page_ready_state()

        # Execute listing query
        response = page.query_data(LISTING_QUERY)
        log.debug(f"Captured {len(response['listings_q'])} listings!")

        for listing in response['listings_q']:
            title = listing['listing_title']
            location = listing['listing_location']
            price = listing['listing_price']
            sqft = listing['listing_sqft']
            link = listing['listing_link']

            listings = {
                'title' : title,
                'location': location,
                'price': price,
                'sqft': sqft,
                'link': link
            }

            results.append(listings)

        try:
            # Click the next button
            page.get_by_prompt(f"Go to page {x}").click()
            # Get the search bar with the prompt text
        except:
            exit()


df = pd.DataFrame(data=results)
df.to_csv("prop_guru_Yishun_rent.csv")
