from bs4 import BeautifulSoup
from getpass4 import getpass
import gkeepapi
import keyring

class Client:
    # def __init__(self, Inputs):
    def __init__(self):
        self.label_name = input("Label: ")
        self.email = input("Email: ")
        self.app_password = getpass("Enter App Password or leave blank to use keyring: ")

        self.keep = self.__client()
        self.label = self.__label()

    def __client(self):
        # Intialize Google Keep API
        keep = gkeepapi.Keep()

        # Get Google credentials and login
        if self.app_password:
            print('Logging in...')
            login = keep.login(self.email, self.app_password)

            # Set Google API Token in keyring
            token = keep.getMasterToken()
            keyring.set_password('google-keep-token', self.email, token)
        else:
            print('Reusing token...')
            token = keyring.get_password('google-keep-token', self.email)
            login = keep.resume(self.email, token)

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

    client = Client()

    html = input("Path to Pocket HTML export: ")

    for note in parse_export(html):
        client.create_note(note[0], note[1])

    client.keep.sync()


if __name__ == '__main__':
    main()