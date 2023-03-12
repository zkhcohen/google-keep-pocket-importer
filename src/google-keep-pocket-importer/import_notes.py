from bs4 import BeautifulSoup
from getpass4 import getpass
import gkeepapi
import keyring

# Intialize Google Keep API
keep = gkeepapi.Keep()

# Get Google credentials and login
email = input("Email: ")
token = keyring.get_password('google-keep-token', email)

if token is None:
    app_password = getpass("App Password: ")
    success = keep.login(email, app_password)

    # Set Google API Token in keyring
    token = keep.getMasterToken()
    keyring.set_password('google-keep-token', email, token)
else:
    keep.resume(email, token)

# Create Pocket label in Google Keep
label_name = input("Label: ")
label = keep.findLabel(label_name)

if not label:
    print ('Creating Pocket label in Google Keep...')
    label = keep.createLabel(label_name)
    
    # Sync up changes
    keep.sync()

    label = keep.findLabel(label_name)

# Define the path to the HTML file to read
html_file = input("Path to Pocket HTML export: ")

# Load the HTML file as a BeautifulSoup object
with open(html_file, "r", encoding="utf8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Find all anchor tags in the document
anchors = soup.find_all("a")

# Loop through each anchor tag and extract the URL and description
for anchor in anchors:
    url = anchor.get("href")
    title = anchor.text.strip()

    print ('Import Title: ', title)
    print ('Import URL: ', url)

    # Add note if not found
    if len(list(keep.find(query=url))) == 0:
        gnote = keep.createNote(title, url)

        # Adding Pocket label to note:
        gnote.labels.add(label)

        # Sync up changes
        keep.sync()

        # Retrieve new note
        gnote = list(keep.find(query=url))[0]

        print ('Note Title: ', gnote.title)
        print ('Note Text: ', gnote.text)

    else:
        print ('Note already added!')

