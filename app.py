import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from string import ascii_lowercase

# Function to get Google Autosuggest suggestions
def get_google_autosuggest(keyword, country_code='us', language_code='en'):
    url = 'http://suggestqueries.google.com/complete/search'
    params = {
        'output': 'toolbar',
        'hl': language_code,
        'gl': country_code,
        'q': keyword
    }
    response = requests.get(url, params=params)
    suggestions = []
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'xml')
        for suggestion in soup.find_all('suggestion'):
            suggestion_text = suggestion.get('data')
            suggestions.append(suggestion_text)
    return suggestions

# Function to remove duplicates
def remove_duplicates(suggestions):
    seen = set()
    unique_suggestions = []
    for suggestion in suggestions:
        if suggestion['Query'] not in seen:
            seen.add(suggestion['Query'])
            unique_suggestions.append(suggestion)
    return unique_suggestions

# Main Streamlit app
def main():
    st.title("Advanced Google Autosuggest Scraper with Query Type")

    st.markdown("""
    ## How It Works
    - **Enter a seed keyword**: The app will scrape Google Autosuggest results for that keyword.
    - **Alphabet Soup Method**: It repeats the operation for every letter of the alphabet (a-z) appended to the seed keyword.
    - **Wildcard Searches**: Wildcard searches are applied before, after, and sometimes in-between the keyword and its modifiers.
    - **Extended Content-Type and Question Modifiers**: Expanded to include various question, action, comparison, and issue modifiers.
    - **Query Types**: Each query is categorized by its type, such as Questions, Actions, Comparisons, Issues, Alphabetic, or Numbers.
    """)

    seed_keyword = st.text_input("Enter your seed keyword:")

    if seed_keyword:
        if st.button('Scrape Suggestions'):
            st.write("Fetching suggestions...")

            # List to store keyword variations
            keywords = []
            query_types = []

            # Alphabetic and Number variations
            for c in ascii_lowercase:
                keywords.append(seed_keyword + ' ' + c)
                keywords.append(f'{seed_keyword} {c} *')
                keywords.append(f'* {seed_keyword} {c}')
                query_types.extend(['Alphabetic', 'Alphabetic', 'Alphabetic'])
            
            for i in range(0, 10):
                keywords.append(seed_keyword + ' ' + str(i))
                keywords.append(f'{seed_keyword} {str(i)} *')
                keywords.append(f'* {seed_keyword} {str(i)}')
                query_types.extend(['Numbers', 'Numbers', 'Numbers'])

            # Extended modifiers grouped by type
            modifiers_by_type = {
                'Questions': ['could', 'would', 'should', 'can', 'will', 'why', 'how', 'is', 'are', 'when', 'where', 'what', 'who', 'does', 'might', 'may'],
                'Actions': ['learn', 'find', 'use', 'get', 'fix', 'troubleshoot', 'apply', 'configure', 'install', 'remove', 'enable', 'disable'],
                'Comparisons': ['vs', 'comparison', 'advantages', 'disadvantages', 'alternatives'],
                'Problems': ['broken', 'not working', 'stopped', 'issues', 'errors', 'failed', 'cant', "doesn't", "won't"],
                'How-To': ['how to', 'steps to', 'guide to', 'tutorial on', 'checklist for', 'setup', 'configure', 'fix'],
                'Content Types': ['tips', 'techniques', 'strategies', 'best practices', 'reviews', 'case study', 'interview', 'questions', 'research', 'statistics', 'trends'],
                'Miscellaneous': ['certifications', 'training', 'tools', 'software', 'platforms', 'apps', 'reports', 'conferences', 'troubleshooting', 'events']
            }

            # Append modifiers with wildcard variations and add to keyword list
            for query_type, modifier_list in modifiers_by_type.items():
                for modifier in modifier_list:
                    keywords.append(f'{modifier} {seed_keyword}')
                    keywords.append(f'* {modifier} {seed_keyword}')
                    keywords.append(f'{modifier} {seed_keyword} *')
                    keywords.append(f'{modifier} * {seed_keyword}')
                    keywords.append(f'* {seed_keyword} {modifier}')
                    query_types.extend([query_type] * 5)

            # List to store all suggestions
            sugg_all = []
            
            # Fetch suggestions for each keyword variation
            for kw, query_type in zip(keywords, query_types):
                suggestions = get_google_autosuggest(kw)
                if suggestions:
                    for suggestion in suggestions:
                        # Renaming wildcards to their parent modifier
                        parent_modifier = kw.replace('*', '').replace(seed_keyword, '').strip() or 'Original'
                        sugg_all.append({'Modifier': parent_modifier, 'Query': suggestion, 'Type': query_type})
            
            # Remove duplicates
            sugg_all = remove_duplicates(sugg_all)
            
            # Display the results
            if sugg_all:
                df = pd.DataFrame(sugg_all)
                st.write(df)
                st.download_button(
                    label="Download results as CSV",
                    data=df.to_csv(index=False),
                    file_name="autosuggest_results.csv",
                    mime="text/csv",
                )
            else:
                st.write("No suggestions found.")

if __name__ == '__main__':
    main()
