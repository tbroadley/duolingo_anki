1. Go to https://www.duolingo.com/practice-hub/words
1. Run `download_duolingo_vocabulary.js` in the console
1. Get the value of the variable `result` from the console and paste it into `duolingo_vocabulary.csv`
1. Download a HAR file of the network requests made on the page, filtered to "Media"
1. Load the HAR file into https://jam.dev/utilities/har-file-viewer and copy the HTML table of requests to `duolingo_audio_file_links.txt`
1. Use a Vim macro to remove everything from `duolingo_audio_file_links.txt` except the file URLs
1. `python combine_vocabulary_and_audio_file_links.py`
1. `python download_audio_files.py`
1. `cp audio_files/* "/mnt/c/Users/burie/AppData/Roaming/Anki2/User 1/collection.media"` (TODO this only works on my computer)
1. `python add_audio_file_references.py`

This creates a `duolingo_vocabulary_final.csv` file that you can load into Anki :tada:
