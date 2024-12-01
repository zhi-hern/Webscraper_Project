import logging
import agentql
from playwright.sync_api import sync_playwright
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


# change page number
URL = "https://www.propertyguru.com.sg/property-for-rent/1?_freetextDisplay=yishun&freetext=yishun"
results = []


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = agentql.wrap(browser.new_page())
    page.goto(URL)

    QUERY = """
    {
        captcha_form {
            Verify_you_are_human_checkbox
        }
    }
    """

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
    # range = (next page, last page)
    for x in range(2, 25):
        # Use query_elements() method to fetch the cookies dialog button from the page
        page.wait_for_page_ready_state()
        response = page.query_elements(QUERY)

        # Check if there is a cookie-rejection button on the page
        if response.captcha_form.Verify_you_are_human_checkbox != None:
            # If so, click the close button to reject cookies
            response.captcha_form.Verify_you_are_human_checkbox.click()

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
