from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from credetials import USERNAME, PASSWORD
from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
# Creating a webdriver instance
chrome_options = Options()
chrome_options.add_argument("--incognito")
driver = webdriver.Chrome(options = chrome_options)
driver.fullscreen_window()
# This instance will be used to log into LinkedIn

# Opening linkedIn's login page
driver.get("https://www.linkedin.com/")

# waiting for the page to load


# entering username
username = driver.find_element(By.ID, "session_key")
driver.implicitly_wait(3)
# In case of an error, try changing the element
# tag used here.

# Enter Your Email Address
username.send_keys(USERNAME) 

# entering password
pword = driver.find_element(By.ID, "session_password")
driver.implicitly_wait(3)

# In case of an error, try changing the element 
# tag used here.

# Enter Your Password
pword.send_keys(PASSWORD)	 
driver.implicitly_wait(3)

# Clicking on the log in button
# Format (syntax) of writing XPath --> 
# //tagname[@attribute='value']
driver.find_element(By.XPATH, "//button[@type='submit']").click()
# In case of an error, try changing the
# XPath used here.
# //*[@id="global-nav-search"]/div
search_button = driver.find_element(By.XPATH,'//*[@id="global-nav-search"]/div')
driver.implicitly_wait(3)
search_button.click()


search = driver.find_element(By.XPATH, "//*[@id='global-nav-typeahead']/input")
driver.implicitly_wait(3)
search.click()
search.clear()
search.send_keys('automation in IT')
time.sleep(2)
search.send_keys(Keys.RETURN)

#TODO - get posts

time.sleep(5)
current_url = driver.current_url
posts_url = current_url.replace('all', 'content',1)
driver.get(posts_url)

# page_source = driver.page_source
# file_ps = open('page_source.txt','w',encoding='utf-8')
# # print(page_source)
# # test = page_source.__str__
# file_ps.write(page_source)
# soup = BeautifulSoup(page_source, features="html.parser")
# soup_txt = open('soup_post.txt','w',encoding='utf-8')
# soup_txt.write(soup.prettify())


#####################################################################################################################

SCROLL_PAUSE_TIME = 1.5
MAX_SCROLLS = False

# JavaScript commands
SCROLL_COMMAND = "window.scrollTo(0, document.body.scrollHeight);"
GET_SCROLL_HEIGHT_COMMAND = "return document.body.scrollHeight"

# Initial scroll height
last_height = driver.execute_script(GET_SCROLL_HEIGHT_COMMAND)
scrolls = 0
no_change_count = 0

while True:
    # Scroll down to bottom
    driver.execute_script(SCROLL_COMMAND)

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script(GET_SCROLL_HEIGHT_COMMAND)
    
    # Increment no change count or reset it
    no_change_count = no_change_count + 1 if new_height == last_height else 0
    
    # Break loop if the scroll height has not changed for 3 cycles or reached the maximum scrolls
    if no_change_count >= 3 or (MAX_SCROLLS and scrolls >= MAX_SCROLLS):
        break
    
    last_height = new_height
    scrolls += 1
    if(scrolls == 5): 
        break
company_page = driver.page_source
linkedin_soup = bs(company_page,features='html.parser')
#print(linkedin_soup.prettify())

containers = linkedin_soup.find_all("div",{"class":"feed-shared-update-v2"})
containers = [container for container in containers if 'activity' in container.get('data-urn', '')]
print(len(containers))

#Saving the container html for bebugging purposes
containers_text = "\n\n".join([c.prettify() for c in containers])
with open(f"soup_containers.txt", "w+",encoding='utf-8') as t:
    t.write(containers_text)

def get_actual_date(date):
    today = datetime.today().strftime('%Y-%m-%d')
    current_year = datetime.today().strftime('%Y')
    
    def get_past_date(days=0, weeks=0, months=0, years=0):
        date_format = '%Y-%m-%d'
        dtObj = datetime.strptime(today, date_format)
        past_date = dtObj - relativedelta(days=days, weeks=weeks, months=months, years=years)
        past_date_str = past_date.strftime(date_format)
        return past_date_str

    past_date = date
    
    if 'hour' in date:
        past_date = today
    elif 'day' in date:
        date.split(" ")[0]
        past_date = get_past_date(days=int(date.split(" ")[0]))
    elif 'week' in date:
        past_date = get_past_date(weeks=int(date.split(" ")[0]))
    elif 'month' in date:
        past_date = get_past_date(months=int(date.split(" ")[0]))
    elif 'year' in date:
        past_date = get_past_date(months=int(date.split(" ")[0]))
    else:
        split_date = date.split("-")
        if len(split_date) == 2:
            past_month = split_date[0]
            past_day =  split_date[1]
            if len(past_month) < 2:
                past_month = "0"+past_month
            if len(past_day) < 2:
                past_day = "0"+past_day
            past_date = f"{current_year}-{past_month}-{past_day}"
        elif len(split_date) == 3:
            past_month = split_date[0]
            past_day =  split_date[1]
            past_year = split_date[2]
            if len(past_month) < 2:
                past_month = "0"+past_month
            if len(past_day) < 2:
                past_day = "0"+past_day
            past_date = f"{past_year}-{past_month}-{past_day}"

    return past_date



def convert_abbreviated_to_number(s):
    if isinstance(s,str) and 'K' in s:
        return int(float(s.replace('K', '')) * 1000)
    elif isinstance(s,str) and 'M' in s:
        return int(float(s.replace('M', '')) * 1000000)
    else:
        return int(s)
        
        
        
        
def get_text(container, selector, attributes):
    try:
        element = container.find(selector, attributes)
        if element:
            return element.text.strip()
    except Exception as e:
        print(e)
    return ""

def get_media_info(container):
    media_info = [("div", {"class": "update-components-video"}, "Video"),
                  ("div", {"class": "update-components-linkedin-video"}, "Video"),
                  ("div", {"class": "update-components-image"}, "Image"),
                  ("article", {"class": "update-components-article"}, "Article"),
                  ("div", {"class": "feed-shared-external-video__meta"}, "Youtube Video"),
                  ("div", {"class": "feed-shared-mini-update-v2 feed-shared-update-v2__update-content-wrapper artdeco-card"}, "Shared Post"),
                  ("div", {"class": "feed-shared-poll ember-view"}, "Other: Poll, Shared Post, etc")]
    
    for selector, attrs, media_type in media_info:
        element = container.find(selector, attrs)
        if element:
            link = element.find('a', href=True)
            return link['href'] if link else "None", media_type
    return "None", "Unknown"

posts_data = []

# Main loop to process each container
for container in containers:
    post_text = get_text(container, "div", {"class": "feed-shared-update-v2__description-wrapper"})
    media_link, media_type = get_media_info(container)
    post_date = get_text(container, "div", {"class": "ml4 mt2 text-body-xsmall t-black--light"})
    post_date = get_actual_date(post_date)
    
    # Reactions (likes)
    reactions_element = container.find_all(lambda tag: tag.name == 'button' and 'aria-label' in tag.attrs and 'reaction' in tag['aria-label'].lower())
    reactions_idx = 1 if len(reactions_element) > 1 else 0
    post_reactions = reactions_element[reactions_idx].text.strip() if reactions_element and reactions_element[reactions_idx].text.strip() != '' else 0

    # Comments
    comment_element = container.find_all(lambda tag: tag.name == 'button' and 'aria-label' in tag.attrs and 'comment' in tag['aria-label'].lower())
    comment_idx = 1 if len(comment_element) > 1 else 0
    post_comments = comment_element[comment_idx].text.strip() if comment_element and comment_element[comment_idx].text.strip() != '' else 0

    # Shares
    shares_element = container.find_all(lambda tag: tag.name == 'button' and 'aria-label' in tag.attrs and 'repost' in tag['aria-label'].lower())
    shares_idx = 1 if len(shares_element) > 1 else 0
    post_shares = shares_element[shares_idx].text.strip() if shares_element and shares_element[shares_idx].text.strip() != '' else 0
        
        
    # Append the collected data to the posts_data list
    posts_data.append({
        # "Page": company_name,#FIXME - fix required
        "Date": post_date,
        "Post Text": post_text,
        "Media Type": media_type,
        "Likes": post_reactions,
        "Comments": post_comments,
        "Shares":post_shares,
        "Likes Numeric": convert_abbreviated_to_number(post_reactions),
        "Media Link": media_link
    })


posts_data = []

# Main loop to process each container
for container in containers:
    post_text = get_text(container, "div", {"class": "feed-shared-update-v2__description-wrapper"})
    media_link, media_type = get_media_info(container)
    post_date = get_text(container, "div", {"class": "ml4 mt2 text-body-xsmall t-black--light"})
    post_date = get_actual_date(post_date)
    
    # Reactions (likes)
    reactions_element = container.find_all(lambda tag: tag.name == 'button' and 'aria-label' in tag.attrs and 'reaction' in tag['aria-label'].lower())
    reactions_idx = 1 if len(reactions_element) > 1 else 0
    post_reactions = reactions_element[reactions_idx].text.strip() if reactions_element and reactions_element[reactions_idx].text.strip() != '' else 0

    # Comments
    comment_element = container.find_all(lambda tag: tag.name == 'button' and 'aria-label' in tag.attrs and 'comment' in tag['aria-label'].lower())
    comment_idx = 1 if len(comment_element) > 1 else 0
    post_comments = comment_element[comment_idx].text.strip() if comment_element and comment_element[comment_idx].text.strip() != '' else 0

    # Shares
    shares_element = container.find_all(lambda tag: tag.name == 'button' and 'aria-label' in tag.attrs and 'repost' in tag['aria-label'].lower())
    shares_idx = 1 if len(shares_element) > 1 else 0
    post_shares = shares_element[shares_idx].text.strip() if shares_element and shares_element[shares_idx].text.strip() != '' else 0
        
        
    # Append the collected data to the posts_data list
    posts_data.append({
        # "Page": company_name,
        "Date": post_date,
        "Post Text": post_text,
        "Media Type": media_type,
        "Likes": post_reactions,
        "Comments": post_comments,
        "Shares":post_shares,
        "Likes Numeric": convert_abbreviated_to_number(post_reactions),
        "Media Link": media_link
    })

print(posts_data)

try:
    df = pd.DataFrame(posts_data)
except:
    for item in list(data.keys()):
        print(item)
        print(len(data[item]))
        
for col in df.columns:
    try:
        df[col] = df[col].astype(int)
    except:
        pass
    
df.sort_values(by="Likes Numeric", inplace=True, ascending=False)

df.to_csv("posts.csv", encoding='utf-8', index=False)
# df.to_excel("{}_linkedin_posts.xlsx".format(company_name), index=False)
time.sleep(3)
driver.quit()