
'''
Takes in a diarized vtt file and counts the total no. and no. of words used by each speaker.

Requires:
python -m spacy download fr_core_news_sm
python -m spacy download en_core_web_sm'''

import argparse
import re
import spacy
import pandas as pd
import os


def wordcount_vtt_to_dataframe(file_path, language_code):
    # Load the appropriate NLP model based on the specified language.
    if language_code.upper() == 'FR':
        nlp = spacy.load("fr_core_news_sm")
    elif language_code.upper() == 'EN':
        nlp = spacy.load("en_core_web_sm")
    else:
        raise ValueError("Unsupported language. Please use 'FR' for French or 'EN' for English.")

    word_counts = {}
    # Regex to match speaker tags and their dialogue.
    speaker_regex = re.compile(r'<v ([^>]+)>([^<]+)')

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Find all occurrences of speaker and dialogue in the file.
    matches = speaker_regex.findall(content)
    for speaker, dialogue in matches:
        # Normalize speaker names by trimming spaces.
        speaker = speaker.strip()
        # Count words in the dialogue using the NLP model.
        doc = nlp(dialogue.strip())
        word_count = len([token for token in doc if token.is_alpha])
        if speaker not in word_counts:
            word_counts[speaker] = word_count
        else:
            word_counts[speaker] += word_count

    # Convert the word counts to a DataFrame
    df = pd.DataFrame(list(word_counts.items()), columns=['Speaker', 'Word Count'])

    # Calculate the total word count and append it to the DataFrame
    total_words = df['Word Count'].sum()
    total_row = pd.DataFrame([["Total", total_words]], columns=['Speaker', 'Word Count'])
    df = pd.concat([df, total_row], ignore_index=True)

    return df


def main():
    parser = argparse.ArgumentParser(description='Count words in a VTT file for each speaker.')
    parser.add_argument('-file', type=str, help='Path to the VTT file', required=True)
    parser.add_argument('-language', type=str, choices=['FR', 'EN'],
                        help='Language of the VTT file (FR for French, EN for English)', required=True)

    args = parser.parse_args()

    df = wordcount_vtt_to_dataframe(args.file, args.language)

    base_filename = os.path.splitext(args.file)[0]
    output_filename = f"{base_filename}_summary.csv"

    # Save the DataFrame to a CSV file
    df.to_csv(output_filename, index=False)

    print(f"Summary saved to {output_filename}")

    print(df)


if __name__ == "__main__":
    main()
