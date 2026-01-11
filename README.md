# `duolingo_anki`

Scripts to download Duolingo vocabulary and audio files, then format them as an Anki deck.

## Quick Start

1. Go to https://www.duolingo.com/practice-hub/words in your browser
2. Open Developer Tools (F12) and go to the Network tab
3. Click on any word to trigger an API request
4. Find the request to `learned-lexemes` in the Network tab
5. Right-click on the request and select "Copy as cURL"
6. Paste the curl command into `curl.txt` in this directory
7. Run: `python fetch_duolingo_lexemes.py`
8. Copy audio files to your Anki media folder:
   ```bash
   cp audio_files/* "/path/to/Anki2/User 1/collection.media"
   ```
9. Import `duolingo_vocabulary_final.csv` into Anki

That's it! The script will automatically:
- Fetch all your learned vocabulary from Duolingo's API
- Download all audio files
- Generate an Anki-ready CSV with sound references

## Credits

Thank you Claude for writing 99% of the code.
