#!/usr/bin/env python3
"""
Fetch learned lexemes from Duolingo API and create an Anki-ready CSV file.
This script replaces the manual browser-based workflow.
"""

import csv
import json
import os
import re
import time
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs


def parse_curl_command(curl_file='curl.txt'):
    """
    Parse the curl command file to extract URL, headers, and data.

    Returns:
        tuple: (url, headers_dict, post_data)
    """
    print("Parsing curl command...")

    with open(curl_file, 'r') as f:
        curl_content = f.read()

    # Extract URL (first quoted string after 'curl')
    url_match = re.search(r"curl\s+'([^']+)'", curl_content)
    if not url_match:
        raise ValueError("Could not find URL in curl command")
    url = url_match.group(1)

    # Extract headers
    headers = {}
    header_pattern = r"-H\s+'([^:]+):\s*([^']+)'"
    for match in re.finditer(header_pattern, curl_content):
        header_name = match.group(1)
        header_value = match.group(2)
        headers[header_name] = header_value

    # Extract POST data
    data_match = re.search(r"--data-raw\s+'([^']+)'", curl_content, re.DOTALL)
    post_data = data_match.group(1) if data_match else None

    print(f"  URL: {url}")
    print(f"  Headers: {len(headers)} found")
    print(f"  POST data: {'Yes' if post_data else 'No'}")

    return url, headers, post_data


def extract_base_url_and_params(url):
    """
    Extract base URL and parameters from the URL.

    Returns:
        tuple: (base_url, user_id, learning_lang, from_lang, params)
    """
    parsed = urlparse(url)

    # Extract user ID and languages from path
    # Path format: /2017-06-30/users/{user_id}/courses/{learning_lang}/{from_lang}/learned-lexemes
    path_parts = parsed.path.split('/')
    user_id = path_parts[4]
    learning_lang = path_parts[6]
    from_lang = path_parts[7]

    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    # Parse query parameters
    params = parse_qs(parsed.query)
    # Convert lists to single values
    params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}

    return base_url, user_id, learning_lang, from_lang, params


def fetch_lexemes(base_url, headers, post_data, start_index=0, limit=50):
    """
    Fetch learned lexemes from Duolingo API.

    Returns:
        dict: API response as JSON
    """
    # Build URL with pagination parameters
    url = f"{base_url}?limit={limit}&sortBy=LEARNED_DATE&startIndex={start_index}"

    print(f"  Fetching lexemes from startIndex={start_index}...")

    # Create request
    data = post_data.encode('utf-8') if post_data else None
    request = urllib.request.Request(url, data=data, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            response_data = response.read()
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code}: {e.reason}")
        print(f"  Response: {e.read().decode('utf-8')}")
        raise
    except Exception as e:
        print(f"  Error: {e}")
        raise


def fetch_all_lexemes(base_url, headers, post_data, limit=50):
    """
    Fetch all learned lexemes by paginating through the API.

    Returns:
        list: All lexeme objects from the API
    """
    print("\nFetching all lexemes...")
    all_lexemes = []
    start_index = 0

    while True:
        response = fetch_lexemes(base_url, headers, post_data, start_index, limit)

        # Extract lexemes from response
        # The actual structure might vary - adjust based on the API response
        if 'lexemes' in response:
            lexemes = response['lexemes']
        elif 'results' in response:
            lexemes = response['results']
        else:
            # If we don't know the structure, print it
            print(f"  Response keys: {list(response.keys())}")
            lexemes = response.get('lexemes', response.get('results', []))

        if not lexemes:
            print(f"  No more lexemes found")
            break

        all_lexemes.extend(lexemes)
        print(f"  Retrieved {len(lexemes)} lexemes (total: {len(all_lexemes)})")

        # Check if there are more pages
        if len(lexemes) < limit:
            break

        start_index += limit
        time.sleep(0.5)  # Be nice to the API

    print(f"\nTotal lexemes retrieved: {len(all_lexemes)}")
    return all_lexemes


def extract_lexeme_data(lexeme):
    """
    Extract relevant data from a lexeme object.

    Returns:
        dict: Extracted data (word, translation, audio_url)
    """
    # These field names are guesses - adjust based on actual API response
    word = lexeme.get('lexeme', {}).get('word', '') or lexeme.get('word', '') or lexeme.get('learningWord', '')
    translation = lexeme.get('lexeme', {}).get('translation', '') or lexeme.get('translation', '') or lexeme.get('translations', [''])[0]

    # Audio URL might be nested
    audio_url = ''
    if 'lexeme' in lexeme and 'audio' in lexeme['lexeme']:
        audio_url = lexeme['lexeme']['audio']
    elif 'audio' in lexeme:
        audio_url = lexeme['audio']
    elif 'tts' in lexeme:
        audio_url = lexeme['tts']
    elif 'lexeme' in lexeme and 'tts' in lexeme['lexeme']:
        audio_url = lexeme['lexeme']['tts']

    return {
        'word': word,
        'translation': translation,
        'audio_url': audio_url
    }


def download_audio_file(url, filepath, max_retries=3):
    """
    Download an audio file with retry logic.

    Returns:
        bool: True if successful, False otherwise
    """
    for attempt in range(max_retries):
        try:
            request = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            with urllib.request.urlopen(request, timeout=30) as response:
                with open(filepath, 'wb') as f:
                    f.write(response.read())
            return True

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"    Failed to download {os.path.basename(filepath)}: {e}")
                return False

    return False


def extract_filename_from_url(url):
    """Extract filename from audio URL."""
    parsed = urlparse(url)
    filename = parsed.path.split('/')[-1]
    if not filename.lower().endswith('.mp3'):
        filename += '.mp3'
    return filename


def download_all_audio_files(lexeme_data_list, audio_folder='audio_files'):
    """
    Download all audio files from the lexeme data.

    Returns:
        dict: Mapping of audio URLs to local filenames
    """
    print(f"\nDownloading audio files to '{audio_folder}/'...")
    os.makedirs(audio_folder, exist_ok=True)

    url_to_filename = {}
    downloaded = 0
    skipped = 0
    failed = 0

    for i, data in enumerate(lexeme_data_list, 1):
        audio_url = data['audio_url']
        if not audio_url:
            continue

        filename = extract_filename_from_url(audio_url)
        filepath = os.path.join(audio_folder, filename)
        url_to_filename[audio_url] = filename

        if os.path.exists(filepath):
            skipped += 1
            if i <= 3:
                print(f"  [{i}/{len(lexeme_data_list)}] {filename} - already exists")
            continue

        if i <= 3 or i % 10 == 0:
            print(f"  [{i}/{len(lexeme_data_list)}] Downloading {filename}...")

        if download_audio_file(audio_url, filepath):
            downloaded += 1
        else:
            failed += 1

        # Rate limiting
        if i % 10 == 0:
            time.sleep(1)

    print(f"\nAudio download summary:")
    print(f"  Downloaded: {downloaded}")
    print(f"  Already existed: {skipped}")
    print(f"  Failed: {failed}")

    return url_to_filename


def create_anki_csv(lexeme_data_list, url_to_filename, output_file='duolingo_vocabulary_final.csv'):
    """
    Create the final Anki-ready CSV file.
    """
    print(f"\nCreating Anki CSV: {output_file}...")

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(['vietnamese', 'english', 'audio'])

        # Write data
        for data in lexeme_data_list:
            word = data['word']
            translation = data['translation']
            audio_url = data['audio_url']

            # Create Anki sound reference
            audio_reference = ''
            if audio_url and audio_url in url_to_filename:
                filename = url_to_filename[audio_url]
                audio_reference = f"[sound:{filename}]"

            writer.writerow([word, translation, audio_reference])

    print(f"  Created {output_file} with {len(lexeme_data_list)} entries")


def main():
    """Main execution flow."""
    print("="*60)
    print("Duolingo to Anki Converter")
    print("="*60)

    try:
        # Step 1: Parse curl command
        url, headers, post_data = parse_curl_command('curl.txt')
        base_url, user_id, learning_lang, from_lang, params = extract_base_url_and_params(url)

        print(f"\nConfiguration:")
        print(f"  User ID: {user_id}")
        print(f"  Learning: {learning_lang}")
        print(f"  From: {from_lang}")

        # Step 2: Fetch all lexemes
        all_lexemes = fetch_all_lexemes(base_url, headers, post_data, limit=50)

        if not all_lexemes:
            print("\nNo lexemes found. The API might have changed or authentication may have failed.")
            print("Please check your curl.txt file and ensure the Bearer token and cookies are up to date.")
            return

        # Step 3: Extract data from lexemes
        print("\nExtracting lexeme data...")
        lexeme_data_list = [extract_lexeme_data(lex) for lex in all_lexemes]

        # Print first few entries as a sample
        print("\nSample entries:")
        for i, data in enumerate(lexeme_data_list[:3], 1):
            print(f"  {i}. {data['word']} = {data['translation']}")
            print(f"     Audio: {data['audio_url'][:50] if data['audio_url'] else 'None'}{'...' if data['audio_url'] and len(data['audio_url']) > 50 else ''}")

        # Step 4: Download audio files
        url_to_filename = download_all_audio_files(lexeme_data_list)

        # Step 5: Create final CSV
        create_anki_csv(lexeme_data_list, url_to_filename)

        print("\n" + "="*60)
        print("SUCCESS! Your Anki deck is ready.")
        print("="*60)
        print("\nNext steps:")
        print("1. Copy audio files to your Anki media folder:")
        print("   cp audio_files/* '<Anki folder>/User 1/collection.media'")
        print("2. Import duolingo_vocabulary_final.csv into Anki")

    except FileNotFoundError:
        print("\nError: curl.txt file not found.")
        print("Please create a curl.txt file with your Duolingo API curl command.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
