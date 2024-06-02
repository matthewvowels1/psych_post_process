import re
import sys
import argparse

'''
We found that whisper occasionally bugs and outputs the same line for the same person again and again.

This code looks for instances where this occurs 3 or more times in a row in a vtt file with speaker assignments and deletes them.

It includes a function for removing empty spaces.

'''

def remove_duplicate_lines(lines):
    cleaned_lines = []
    prev_speaker = None
    prev_text = None
    count = 1
    buffer = []

    i = 0
    while i < len(lines) - 1:
        # Get current and next line without stripping to preserve file structure
        timestamp_line = lines[i]
        dialogue_line = lines[i + 1]

        # Check if the current line is a timestamp
        if re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', timestamp_line.strip()):
            # Check if the next line is a valid speaker dialogue
            match = re.search(r'<v ([^>]+)>(.*)', dialogue_line.strip())
            if match:
                speaker, text = match.groups()
                text = text.strip()  # Only strip the text content for comparison
                # Check if current speaker and text match the previous
                if speaker == prev_speaker and text == prev_text:
                    count += 1
                else:
                    if count >= 3:
                        # Keep only the first instance from buffer
                        cleaned_lines.append(buffer[0][0])  # Timestamp
                        cleaned_lines.append(buffer[0][1])  # Dialogue
                        cleaned_lines.append('\n')  # Ensure a blank line after the entry
                    else:
                        # Append all buffered entries
                        for entry in buffer:
                            cleaned_lines.extend(entry)
                            cleaned_lines.append('\n')
                    # Reset buffer and count
                    buffer = [(timestamp_line, dialogue_line)]
                    count = 1
                # Update previous speaker and text
                prev_speaker = speaker
                prev_text = text
            i += 2  # Move to the next pair of lines
        else:
            # Append any non-timestamp line directly
            cleaned_lines.append(timestamp_line)
            i += 1

    # Flush any remaining entries in the buffer at the end
    if count >= 3:
        cleaned_lines.append(buffer[0][0])
        cleaned_lines.append(buffer[0][1])
        cleaned_lines.append('\n')
    else:
        for entry in buffer:
            cleaned_lines.extend(entry)
            cleaned_lines.append('\n')

    return cleaned_lines


def get_consistent_spacing(cleaned_lines):
    spaced_lines = []
    previous_line_blank = False

    for line in cleaned_lines:
        if line.strip() == '':
            if not previous_line_blank:
                spaced_lines.append(line)
                previous_line_blank = True
        else:
            spaced_lines.append(line)
            previous_line_blank = False

    return spaced_lines

def clean_vtt_file(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    cleaned_lines = remove_duplicate_lines(lines)
    spaced_lines = get_consistent_spacing(cleaned_lines)

    # Writing the cleaned lines to the output file
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.writelines(spaced_lines)

def main():
    parser = argparse.ArgumentParser(description='Clean VTT file by removing duplicate and empty entries.')
    parser.add_argument('--input', type=str, help='Input VTT filename', required=True)
    parser.add_argument('--output', type=str, help='Output cleaned VTT filename', required=True)
    args = parser.parse_args()

    clean_vtt_file(args.input, args.output)

if __name__ == "__main__":
    main()