import json  # Import the JSON module to handle JSON data
import re  # Import the regular expression module to perform text processing
import pandas as pd  # Import pandas for data manipulation and analysis
import spacy  # Import spaCy for natural language processing

nlp = spacy.load('en_core_web_sm')  # Load the spaCy English model

def perform_ner(document):
    """Perform Named Entity Recognition using spaCy"""
    # Process the document using spaCy NLP pipeline
    doc = nlp(document)  
    # Extract named entities and their labels
    entities = [(ent.text, ent.label_) for ent in doc.ents]  
    # Return the list of entities
    return entities  

def process_book(original_text_file, char_json_path, output_prefix, remove_character=None):
    """Process a book to analyze character relationships and frequencies"""
    # Load the original text
    with open(original_text_file, 'r', encoding='utf-8') as tf:
        # Read and convert the text to lowercase
        original_text = tf.read().lower()  
    
    # Load the character data from the specified JSON file
    with open(char_json_path, 'r') as file:
        characters_data = json.load(file)  
    
    characters = []
    for character, aliases in characters_data["ThroughTheLookingGlass"]["characters"].items():
        # Add the main character name in lowercase
        characters.append(character.lower())  
        # Add aliases in lowercase
        characters.extend(alias.lower() for alias in aliases)  
    
    # Remove the specified character from the list
    if remove_character:
        characters = [char for char in characters if char != remove_character.lower()]  

    # Store sentences with their associated named entities
    sent_entity_df = []

    # Tokenize the text into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', original_text)

    def filter_entity(sentence):
        """ Function to filter out non-character entities from a sentence and handle "the" prefix"""
        return [character.replace("the ", "") for character in characters if character in sentence]  

    # Loop through sentences, store named entity list for each sentence
    for idx, sentence in enumerate(sentences):
        # Filter entities in the sentence
        entity_list = filter_entity(sentence)  
        context_entities = []
        if idx >= 2:
            # Get entities from previous two sentences
            context_entities += sent_entity_df[idx-2]['entities']
        if idx >= 1:
            context_entities += sent_entity_df[idx-1]['entities']
        context_entities += entity_list
        # Filter out duplicate context entities while preserving order
        context_entities = list(dict.fromkeys(context_entities))
        # Store the result
        sent_entity_df.append({"sentence": sentence, "entities": entity_list, "context_entities": context_entities})  

    # Convert the list to a DataFrame
    sent_entity_df = pd.DataFrame(sent_entity_df)  

    # Filter out sentences with fewer than 2 unique entities
    sent_entity_df_filtered = sent_entity_df[sent_entity_df['context_entities'].apply(lambda x: len(set(x))) >= 2]  

    # Initialize dictionary to store relationships and their counts
    relationship_counts = {}

    # Iterate through context_entities
    for _, row in sent_entity_df_filtered.iterrows():
        # Get unique entities in the sentence
        entity = set(row['entities'])  
        # Get unique context entities
        context_ent = set(row['context_entities'])  
        
        for ent in entity:
            for cont in context_ent:
                # Skip if the entity and context entity are the same
                if ent == cont:
                    continue  
                # Create a tuple representing the relationship pair
                relationship_pair = (ent, cont)
                # Increment the count for the relationship pair in the dictionary
                relationship_counts[relationship_pair] = relationship_counts.get(relationship_pair, 0) + 1

    # Convert dictionary (= relationship counts) to DataFrame
    relationship_df = pd.DataFrame(list(relationship_counts.items()), columns=['source_target', 'count']) 

    # Split the source_target tuple into separate columns
    relationship_df[['source', 'target']] = pd.DataFrame(relationship_df['source_target'].tolist(), index=relationship_df.index)  

    # Drop the combined column
    relationship_df.drop(columns=['source_target'], inplace=True)  

    # Aggregate the counts for the same relationship in both directions
    relationship_df = relationship_df.groupby(['source', 'target'], as_index=False)['count'].sum()  
    
    # Sort the relationships to ensure consistent order for bidirectional relationships
    relationship_df[['source', 'target']] = relationship_df[['source', 'target']].apply(lambda row: pd.Series(sorted(row)), axis=1)  
    
    # Drop duplicates to keep only one direction of the relationship with the aggregated count
    relationship_df.drop_duplicates(['source', 'target'], inplace=True)  

    # Calculate the total number of relationships and normalize the relationship counts 
    total_relationships = relationship_df['count'].sum()  
    relationship_df['normalized_count'] = relationship_df['count'] / total_relationships 

    # Reset the index
    #relationship_df.reset_index(drop=True, inplace=True)

    # Save the relationship DataFrame to CSV
    relationship_df.to_csv(f'{output_prefix}_relationship_data.csv', index=False)  

    # Character mentions and frequencies
    character_mentions = []
    for character in characters:
        # Create a pattern for exact matches of character names
        pattern = r'\b' + re.escape(character) + r'\b'  
        # Find all mentions of the character
        mentions = re.findall(pattern, original_text, flags=re.IGNORECASE)  
        # Add mentions to the list
        character_mentions.extend(mentions)  
        
    # Remove "the" prefix from mentions
    character_mentions = [mention.replace("the ", "") for mention in character_mentions] 

    character_counts = {}
    for character in character_mentions:
        # Count the mentions for each character
        character_counts[character] = character_counts.get(character, 0) + 1  

    # Calculate total mentions
    total_mentions = sum(character_counts.values())  
    # Calculate frequencies
    character_freqs = {character: count / total_mentions for character, count in character_counts.items()}  

    # Convert to DataFrame and sort by frequency
    result_df = pd.DataFrame(list(character_freqs.items()), columns=['character', 'frequency'])  
    result_df.sort_values(by='frequency', ascending=False, inplace=True)  

    # Save results (= character frequencies) to a CSV file
    result_df.to_csv(f'{output_prefix}_character_frequencies.csv', index=False)  

# Process the book with and without a specific character removed
process_book('alice_preprocessing/text_analytics_alice/through_the_looking_glass.txt', 'lookingglass_chars.json', 'book3')
process_book('alice_preprocessing/text_analytics_alice/through_the_looking_glass.txt', 'lookingglass_chars.json', 'book3_no_alice', remove_character='alice')
process_book('alice_preprocessing/text_analytics_alice/through_the_looking_glass.txt', 'lookingglass_chars.json', 'book3_no_lily', remove_character='lily')