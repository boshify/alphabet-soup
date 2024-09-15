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

# Main Streamlit app
def main():
    st.title("Enhanced Google Autosuggest Scraper")

    st.markdown("""
    ## How It Works
    - **Enter a seed keyword**: The app will scrape Google Autosuggest results for that keyword.
    - **Alphabet Soup Method**: It repeats the operation for every letter of the alphabet (a-z) appended to the seed keyword.
    - **Question Modifiers**: It also applies common question words like "is," "are," "does," and comparative forms like "vs."
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
            for i in range(0, 10):
                keywords.append(seed_keyword + ' ' + str(i))
            
            # Add modifiers for questions and comparisons
            modifiers = ['who', 'what', 'when', 'where', 'why', 'how', 
                         'is', 'are', 'does', 'can', 'should', 'could', 
                         'will', 'would', 'may', 'might', 'must', 
                         'vs', 'comparison', 'advantages', 'disadvantages']
            
            # Append modifiers to the seed keyword
            for modifier in modifiers:
                keywords.append(f'{modifier} {seed_keyword}')
            
            # List to store all suggestions
            sugg_all = []
            
            # Fetch suggestions for each keyword variation
            for kw in keywords:
                suggestions = get_google_autosuggest(kw)
                if suggestions:
                    for suggestion in suggestions:
                        sugg_all.append({'Modifier': kw.replace(seed_keyword, '').strip() or 'Original', 'Query': suggestion})
            
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
