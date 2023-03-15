from bs4 import BeautifulSoup
from getpass4 import getpass
import gkeepapi
import keyring
import argparse

class Client:
    # def __init__(self, Inputs):
    def __init__(self, email, label_name):
        self.email = email
        self.label_name = label_name

        self.keep = self.__auth()
        self.label = self.__label()

    def __auth(self):
        # Intialize Google Keep API
        keep = gkeepapi.Keep()

        token = keyring.get_password('google-keep-token', self.email)

        # Get Google credentials and login
        if token:
            print('Authenticating with token...')
            try:
                login = keep.resume(self.email, token)       
            except gkeepapi.exception.LoginException:
                print('Invalid token')
                keyring.delete_password('google-keep-token', self.email)
        else:
            print('Authenticating with app password...')
            try: 
                app_password = getpass("Enter App Password or leave blank to use keyring: ")
                login = keep.login(self.email, app_password)

                # Set Google API Token in keyring
                token = keep.getMasterToken()
                keyring.set_password('google-keep-token', self.email, token)
            except gkeepapi.exception.LoginException as e:
                print(e)

        assert login is True
        return keep
    
    def __label(self):
        # Create Pocket label in Google Keep
        if not self.keep.findLabel(self.label_name):
            print ('Creating label in Google Keep...')
            label = self.keep.createLabel(self.label_name)

            # Sync up changes
            self.keep.sync()

        label = self.keep.findLabel(self.label_name)

        return label
    
    @classmethod
    def get_user_input(self):
        label_name = input("Label: ")
        email = input("Email: ")
        return self(email, label_name)
    
    def create_note(self, title, url):
        # Add note if not found
        if len(list(self.keep.find(func=lambda x : x.title == title or x.text == url))) == 0:

            # Create note
            gnote = self.keep.createNote(title, url)

            # Adding Pocket label to note:
            gnote.labels.add(self.label)

            print ('Imported Title: ', title)
            print ('Imported URL: ', url)

def parse_export(html):
    # Load the HTML file as a BeautifulSoup object
    with open(html, "r", encoding="utf8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Find all anchor tags in the document
    anchors = soup.find_all("a")

    # Loop through each anchor tag and extract the URL and description
    for anchor in anchors:
        url = anchor.get("href")
        title = anchor.text.strip()

        yield title, url

def main():
    # Get CLI args
    parser = argparse.ArgumentParser(description='Get email, label and path.')
    parser.add_argument('--email', type=str, help='Google Keep Email Address')
    parser.add_argument('--label', type=str, help='Import Label')
    parser.add_argument('--path', type=str, help='Pocket Export File Path')
    args = parser.parse_args()

    # Get email and label via user input if necessary
    client = Client(args.email, args.label) if args.email and args.label else Client.get_user_input()

    # Get Pocket export file path via user input if necessary
    html = args.path if args.path else input("Path to Pocket HTML export: ")

    # Loop through exported notes and import to Google Keep
    for pnote in parse_export(html):
        client.create_note(pnote[0], pnote[1])

    # Sync changes to Google Keep
    client.keep.sync()

if __name__ == '__main__':
    main()