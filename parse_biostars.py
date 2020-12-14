
import requests
import httplib2
from bs4 import BeautifulSoup, SoupStrainer
import re
import collections
import schedule
from slack_sdk import WebClient
import time

# Regex to check.
check_for=[]

# Connect bot to Slack.
token = ''
client=WebClient(token=token)

# Start a log for checked post IDs.
post_log=collections.deque(maxlen=100)

# Define function to check posts.
def check_posts():
    # Create HTTP connection.
    http = httplib2.Http()
    # Retrieve the HTML for the Biostars homepage.
    status, response = http.request('http://www.biostars.org')
    # Loop over HTML anchors.
    for link in BeautifulSoup(response, parse_only=SoupStrainer('a')):
        # Check whether the anchor has a hypertext reference attribute.
        if link.has_attr('href'):
            # Only check link if it is a post, not a comment.
            if re.match('/p/\d+/$', link['href']):
                # Retrieve the post ID.
                post_id=re.search('\d+', link['href']).group(0)
                # Skip post ID if it's been checked already.
                if post_id in post_log: break
                # Use the Biostars API to retrieve post information.
                r=requests.get('https://www.biostars.org/api/post/' + post_id)
                # Extract the post title and content from the Json.
                title=r.json()['title']
                content=r.json()['xhtml']
                url=r.json()['url']
                # Check the title and contents for regex matches.
                # Send a message to slack with title and URL if there is a match.
                if any(re.match(x, title.lower()) for x in check_for):
                    client.chat_postMessage(channel='bots', text=title + ': ' + url)
                elif any(re.match(x, content.lower()) for x in check_for):
                    client.chat_postMessage(channel="bots", text=title + ': ' + url)
                # Add post to log so it doesn't get checked again.
                post_log.append(post_id)

# Schedule job to run every 10 minutes.
schedule.every(10).minutes.do(check_posts)

while True:
    schedule.run_pending()
    time.sleep(1)
