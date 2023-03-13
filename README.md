# Google Keep Pocket Importer

This is a basic package which leverages [gkeepapi](https://github.com/kiwiz/gkeepapi) to import urls/notes from Pocket to Google Keep.

It also tags the imported notes.

---

### Instructions:
1. Export your pocket list: https://help.getpocket.com/article/1015-exporting-your-pocket-list

2. Create a Google App Password: https://support.google.com/accounts/answer/185833?hl=en

3. Clone the repo.

4. Install the package:

```python
pip install -e .
```

5. Run the import.py script and follow the steps to import your notes:

```python
python src\gkpi\import.py
```