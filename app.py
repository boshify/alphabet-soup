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
    st.title("Advanced Google Autosuggest Scraper with Extended Modifiers")

    st.markdown("""
    ## How It Works
    - **Enter a seed keyword**: The app will scrape Google Autosuggest results for that keyword.
    - **Alphabet Soup Method**: It repeats the operation for every letter of the alphabet (a-z) appended to the seed keyword.
    - **Wildcard Searches**: Wildcard searches are applied before, after, and sometimes in-between the keyword and its modifiers.
    - **Extended Content-Type and Negative Modifiers**: Added new modifiers like "calculator", "checklist", "how to", and more.
    """)

    seed_keyword = st.text_input("Enter your seed keyword:")

    if seed_keyword:
        if st.button('Scrape Suggestions'):
            st.write("Fetching suggestions...")

            # List to store keyword variations
            keywords = [seed_keyword]

            # Generate additional keywords by appending a-z and 0-9
            for c in ascii_lowercase:
                keywords.append(seed_keyword + ' ' + c)
                keywords.append(f'{seed_keyword} {c} *')  # Wildcard after
                keywords.append(f'* {seed_keyword} {c}')  # Wildcard before
            
            for i in range(0, 10):
                keywords.append(seed_keyword + ' ' + str(i))
                keywords.append(f'{seed_keyword} {str(i)} *')  # Wildcard after
                keywords.append(f'* {seed_keyword} {str(i)}')  # Wildcard before
            
            # Add common content-type, question, and negative modifiers
            modifiers = [
                'who', 'what', 'when', 'where', 'why', 'how', 
                'is', 'are', 'does', 'can', 'should', 'could', 
                'will', 'would', 'may', 'might', 'must', 
                'vs', 'comparison', 'advantages', 'disadvantages',
                'benefits', 'example', 'template', 'is ' + seed_keyword + ' worth it', 
                'reddit', 'services', 'review', 'contract', 'agreement', 'books', 
                'newsletters', 'podcasts', 'influencers', 'blogs', 'courses', 'training',
                'calculator', 'checklist', 'case study', 'interview', 'questions', 
                'research', 'statistics', 'trends', 'job', 'tips', 'strategies', 'techniques',
                'certifications', 'conferences', 'tools', 'software', 'platforms', 'apps',
                'events', 'reports', 'skills', 'troubleshooting', 'best practices', 'fix',
                'broken', 'not working', 'cant', "doesn't", "won't", 'stopped', 
                'how to', 'learn', 'alternatives'
            ]

            # Append modifiers with wildcard variations
            for modifier in modifiers:
                # Standard modifier without wildcards
                keywords.append(f'{modifier} {seed_keyword}')
                # Wildcard before and after
                keywords.append(f'* {modifier} {seed_keyword}')
                keywords.append(f'{modifier} {seed_keyword} *')
                # Wildcard in-between where applicable
                keywords.append(f'{modifier} * {seed_keyword}')
                keywords.append(f'* {seed_keyword} {modifier}')

            # List to store all suggestions
            sugg_all = []
            
            # Fetch suggestions for each keyword variation
            for kw in keywords:
                suggestions = get_google_autosuggest(kw)
                if suggestions:
                    for suggestion in suggestions:
                        # Renaming wildcards to their parent modifier
                        parent_modifier = kw.replace('*', '').replace(seed_keyword, '').strip() or 'Original'
                        sugg_all.append({'Modifier': parent_modifier, 'Query': suggestion})
            
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
