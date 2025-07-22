import csv

def merge_vocabulary_with_audio_links(csv_file, txt_file, output_file):
    """
    Merges Duolingo vocabulary CSV with audio file links.
    
    Args:
        csv_file (str): Path to the original CSV file
        txt_file (str): Path to the text file containing audio links
        output_file (str): Path for the output CSV file
    """
    try:
        # Read all audio file links
        with open(txt_file, 'r', encoding='utf-8') as f:
            audio_links = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(audio_links)} audio links")
        
        # Process CSV file line by line
        with open(csv_file, 'r', encoding='utf-8', newline='') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            
            csv_reader = csv.reader(infile)
            csv_writer = csv.writer(outfile)
            
            row_count = 0
            
            # Process each row
            for i, row in enumerate(csv_reader):
                if i == 0:
                    # Header row - add the new column name
                    row.append('audio_file_link')
                else:
                    # Data row - add corresponding audio link
                    audio_index = i - 1  # Subtract 1 because we skip header
                    if audio_index < len(audio_links):
                        row.append(audio_links[audio_index])
                    else:
                        row.append('')  # Empty string if no matching audio link
                
                csv_writer.writerow(row)
                row_count += 1
            
            data_rows = row_count - 1  # Subtract header row
            print(f"Successfully processed {data_rows} data rows")
            
            if data_rows != len(audio_links):
                print(f"Note: CSV has {data_rows} data rows but there are {len(audio_links)} audio links")
        
        print(f"Created {output_file} successfully!")
        
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Main execution
if __name__ == "__main__":
    csv_input = "duolingo_vocabulary.csv"
    txt_input = "duolingo_audio_file_links.txt"
    csv_output = "duolingo_vocabulary_with_audio_file_links.csv"
    
    merge_vocabulary_with_audio_links(csv_input, txt_input, csv_output)
