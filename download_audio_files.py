import csv
import os
import time
import urllib.request
import urllib.error
from urllib.parse import urlparse

def extract_filename_from_url(url):
    """
    Extract the filename from the audio URL and add .mp3 extension.
    
    Args:
        url (str): The audio file URL
        
    Returns:
        str: The filename with .mp3 extension
    """
    # Parse the URL and get the path
    parsed = urlparse(url)
    # Get the last part of the path (after the last /)
    filename = parsed.path.split('/')[-1]
    
    # Add .mp3 extension if not already present
    if not filename.lower().endswith('.mp3'):
        filename += '.mp3'
    
    return filename

def download_with_backoff(url, filepath, max_retries=5):
    """
    Download a file with exponential backoff on rate limits and server errors.
    
    Args:
        url (str): URL to download
        filepath (str): Local path to save the file
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        bool: True if successful, False if failed after all retries
    """
    for attempt in range(max_retries + 1):
        try:
            # Create request with User-Agent to avoid being blocked
            request = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(request, timeout=30) as response:
                with open(filepath, 'wb') as f:
                    f.write(response.read())
            return True
            
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limited
                wait_time = (2 ** attempt) + 1  # Exponential backoff: 2, 3, 5, 9, 17 seconds
                print(f"    Rate limited (429). Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
            elif 500 <= e.code < 600:  # Server errors
                wait_time = (2 ** attempt) + 1
                print(f"    Server error ({e.code}). Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
            else:
                print(f"    HTTP error {e.code}: {e.reason}")
                return False
                
        except urllib.error.URLError as e:
            wait_time = (2 ** attempt) + 1
            print(f"    Network error: {e.reason}. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"    Unexpected error: {e}")
            return False
    
    print(f"    Failed to download after {max_retries} retries")
    return False

def download_audio_files(csv_file, audio_folder="audio_files"):
    """
    Download audio files from URLs in the CSV file.
    
    Args:
        csv_file (str): Path to the CSV file with audio_file_link column
        audio_folder (str): Folder to save audio files
    """
    # Create audio folder if it doesn't exist
    os.makedirs(audio_folder, exist_ok=True)
    
    downloaded_count = 0
    skipped_count = 0
    failed_count = 0
    total_count = 0
    
    try:
        with open(csv_file, 'r', encoding='utf-8', newline='') as f:
            csv_reader = csv.reader(f)
            
            # Find the audio_file_link column index
            header = next(csv_reader)
            try:
                audio_link_index = header.index('audio_file_link')
            except ValueError:
                print("Error: Could not find 'audio_file_link' column in CSV")
                return
            
            print(f"Found audio_file_link column at index {audio_link_index}")
            print(f"Starting download process...\n")
            
            # Process each row
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because header is row 1
                if audio_link_index >= len(row):
                    print(f"Row {row_num}: No audio link found, skipping")
                    continue
                
                audio_url = row[audio_link_index].strip()
                if not audio_url:
                    print(f"Row {row_num}: Empty audio link, skipping")
                    continue
                
                total_count += 1
                
                # Extract filename from URL
                filename = extract_filename_from_url(audio_url)
                filepath = os.path.join(audio_folder, filename)
                
                # Check if file already exists
                if os.path.exists(filepath):
                    print(f"Row {row_num}: {filename} already exists, skipping")
                    skipped_count += 1
                    continue
                
                print(f"Row {row_num}: Downloading {filename}...")
                
                # Download the file
                if download_with_backoff(audio_url, filepath):
                    print(f"    ✓ Successfully downloaded {filename}")
                    downloaded_count += 1
                else:
                    print(f"    ✗ Failed to download {filename}")
                    failed_count += 1
        
        # Print summary
        print(f"\n" + "="*50)
        print(f"Download Summary:")
        print(f"  Total audio links found: {total_count}")
        print(f"  Successfully downloaded: {downloaded_count}")
        print(f"  Already existed (skipped): {skipped_count}")
        print(f"  Failed to download: {failed_count}")
        print(f"="*50)
        
    except FileNotFoundError:
        print(f"Error: Could not find CSV file '{csv_file}'")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main execution
if __name__ == "__main__":
    csv_input = "duolingo_vocabulary_with_audio_file_links.csv"
    audio_folder = "audio_files"
    
    print("Duolingo Audio File Downloader")
    print("="*50)
    download_audio_files(csv_input, audio_folder)
