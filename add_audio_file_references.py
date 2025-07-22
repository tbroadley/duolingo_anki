import csv
from urllib.parse import urlparse

def extract_filename_from_url(url):
    """
    Extract the filename from the audio URL and ensure .mp3 extension.
    
    Args:
        url (str): The audio file URL
        
    Returns:
        str: The filename with .mp3 extension
    """
    if not url or not url.strip():
        return ""
    
    # Parse the URL and get the path
    parsed = urlparse(url.strip())
    # Get the last part of the path (after the last /)
    filename = parsed.path.split('/')[-1]
    
    # Add .mp3 extension if not already present
    if not filename.lower().endswith('.mp3'):
        filename += '.mp3'
    
    return filename

def create_anki_sound_reference(filename):
    """
    Create an Anki-style sound reference from a filename.
    
    Args:
        filename (str): The audio filename
        
    Returns:
        str: Anki sound reference in format [sound:filename.mp3]
    """
    if not filename:
        return ""
    
    return f"[sound:{filename}]"

def convert_csv_to_anki_format(input_csv, output_csv):
    """
    Convert CSV with audio_file_link column to audio_file_reference column with Anki sound format.
    
    Args:
        input_csv (str): Path to input CSV file
        output_csv (str): Path to output CSV file
    """
    try:
        with open(input_csv, 'r', encoding='utf-8', newline='') as infile, \
             open(output_csv, 'w', encoding='utf-8', newline='') as outfile:
            
            csv_reader = csv.reader(infile)
            csv_writer = csv.writer(outfile)
            
            # Process header row
            header = next(csv_reader)
            
            # Find the audio_file_link column index
            try:
                audio_link_index = header.index('audio_file_link')
                print(f"Found 'audio_file_link' column at index {audio_link_index}")
            except ValueError:
                print("Error: Could not find 'audio_file_link' column in CSV")
                return
            
            processed_rows = 0
            converted_count = 0
            empty_count = 0
            
            # Process each data row
            for row in csv_reader:
                processed_rows += 1
                
                # Make sure row has enough columns
                while len(row) <= audio_link_index:
                    row.append('')
                
                # Get the audio URL
                audio_url = row[audio_link_index].strip()
                
                if audio_url:
                    # Extract filename from URL
                    filename = extract_filename_from_url(audio_url)
                    # Create Anki sound reference
                    sound_reference = create_anki_sound_reference(filename)
                    row[audio_link_index] = sound_reference
                    converted_count += 1
                    
                    if processed_rows <= 5:  # Show first 5 conversions as examples
                        print(f"  Row {processed_rows}: {audio_url[:50]}{'...' if len(audio_url) > 50 else ''}")
                        print(f"    -> {sound_reference}")
                else:
                    # Empty URL, leave as empty string
                    row[audio_link_index] = ''
                    empty_count += 1
                
                csv_writer.writerow(row)
            
            # Print summary
            print(f"\n" + "="*60)
            print(f"Conversion Summary:")
            print(f"  Total rows processed: {processed_rows}")
            print(f"  Audio references converted: {converted_count}")
            print(f"  Empty audio links: {empty_count}")
            print(f"  Output file: {output_csv}")
            print(f"="*60)
            
            if converted_count > 0:
                print(f"\nExample conversions:")
                print(f"  URL: https://d1vq87e9lcf771.cloudfront.net/bian/abc123")
                print(f"  ->   [sound:abc123.mp3]")
                print(f"\nYour CSV is now ready for Anki import!")
        
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_csv}'")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main execution
if __name__ == "__main__":
    input_csv = "duolingo_vocabulary_with_audio_file_links.csv"
    output_csv = "duolingo_vocabulary_final.csv"
    
    print("Duolingo to Anki Sound Reference Converter")
    print("="*60)
    print("Converting audio file URLs to Anki sound references...")
    print()
    
    convert_csv_to_anki_format(input_csv, output_csv)
