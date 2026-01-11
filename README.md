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

## Old Workflow (deprecated)

The old manual workflow using browser console scripts is deprecated but still available:

1. Go to https://www.duolingo.com/practice-hub/words
1. Run `download_duolingo_vocabulary.js` in the console
1. Get the value of the variable `result` from the console and paste it into `duolingo_vocabulary.csv`
1. Download a HAR file of the network requests made on the page, filtered to "Media"
1. Load the HAR file into https://jam.dev/utilities/har-file-viewer and copy the HTML table of requests to `duolingo_audio_file_links.txt`
1. Use a Vim macro to remove everything from `duolingo_audio_file_links.txt` except the file URLs
1. `python combine_vocabulary_and_audio_file_links.py`
1. `python download_audio_files.py`
1. `python add_audio_file_references.py`
1. `cp audio_files/* "/path/to/Anki2/User 1/collection.media"`

## Credits

Thank you Claude for writing 99% of the code.
