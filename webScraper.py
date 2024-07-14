import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import validators
import html
import pandas as pd

def get_wikipedia_content(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
    except:
        st.write("Error Fetching data from URL.")
    
    # Extract text
    paragraphs = soup.find_all('p')
    text_content = "\n\n".join([html.escape(para.get_text()) for para in paragraphs if para.get_text().strip()])
    
    # Extract tables
    table_contents = pd.read_html(url)
    
    # Extract all Wikipedia links
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/wiki/') and not href.startswith('/wiki/File:'):
            linkName=href.replace("https://en.wikipedia.org/wiki/","").replace("/wiki/","")
            #To avoid Copies of the same link
            if linkName not in links: links.add(linkName)
            
            
    #Extract all images
    image_links = soup.find_all('a', class_='mw-file-description')
    images = []
    for link in image_links:
        # Extract the image URL from the 'img' tag's 'src' attribute
        images.append(link.find('img'))
    
    return text_content, table_contents, links, images

def main():
    
    st.set_page_config(
        page_title="Wiki GPT",
        page_icon="robot_face",
        layout = "wide",
        initial_sidebar_state="expanded"
    )
        
    st.title(':green_book: Query wikipedia articles')
    
    # Initialize session state to store selected URL
    session_state = st.session_state
    if 'selected_url' not in session_state:
        session_state.selected_url = None
    
    # User input for Wikipedia article link
    article_name = st.text_input('Enter Wikipedia article Name:', session_state.selected_url)
    url = "https://en.wikipedia.org/wiki/"+article_name.replace(" ","_")
    st.write(url)
    
    
    if url:
        if validators.url(url):
            try:
                with st.sidebar:
                    # Extract content from Wikipedia
                    text_content, table_contents, links, images = get_wikipedia_content(url)
                    
                    # Display Read more button for text
                    st.header('Extracted Text')
                    with st.expander("Read more"):
                        st.write(text_content)
                    
                    # Display Read more button for tables
                    st.header('Extracted Tables')
                    if table_contents:
                        with st.expander("Read more"):
                            for idx, table in enumerate(table_contents):
                                st.subheader(f'Table {idx + 1}')
                                try:
                                    st.write(table)
                                except SyntaxError as e:
                                    st.write(f"Error rendering table {idx + 1}: {e}")
                    else:
                        st.write("No tables found.")
                    
                    # Display other Wikipedia links
                    st.header('Other Wikipedia Links')
                    with st.expander("Show links"):
                        for idx, link in enumerate(links):
                            button_key = f"link_{idx}"  # Unique key for each link button
                            if st.button(link, key=button_key):
                                session_state.selected_url = "https://en.wikipedia.org/wiki/" +link
                                st.rerun()
                                
                                
                    # Display images
                    st.header("Images")
                    with st.expander("Show images"):
                        displayed=[]
                        for image in images:
                            try:
                                if image.get('alt') not in ["icon" , "flag" , "Edit this at Wikidata", ""] and image.get('src') not in displayed:
                                    st.image("https:"+image.get('src'), image.get('alt'))
                                    displayed.append(image.get('src'))
                                # st.write(image["src"])
                            except Exception as e:
                                # st.write(e)
                                pass
            except Exception as e:
                pass
                # st.error(f"Error fetching data from URL: {e}")
        else:
            st.error("URL invalid!")
    
    
if __name__ == "__main__":
    main()
