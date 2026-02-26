# Huberman Lab Youtube Extraction

### Setup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os
import pickle
from youtube_transcript_api import YouTubeTranscriptApi
from loguru import logger

from os import getenv, makedirs 
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
from semantic_text_splitter import TextSplitter
from tokenizers import Tokenizer

class ETL_pipeline:

    playlist_url = "https://www.youtube.com/playlist?list=PLPNW_gerXa4Pc8S2qoUQc5e8Ir97RLuVW"

    def __init__(self):
        logger.info("Initializing ETL pipeline...")
        self.openai_api_key = getenv("OPENAI_API_KEY")
        logger.info("ETL pipeline initialized successfully")

    def fetch_new_data(self):
        logger.info("Starting data fetching process...")
        driver = webdriver.Chrome()
        driver.get(self.playlist_url)
        ytt_api = YouTubeTranscriptApi()
        df_videos = pd.DataFrame()
        title_dict = {}
        def scrape_youtube_playlist(self):
            logger.info("Scraping YouTube playlist...")
            # Function to scroll to bottom of page
            def scroll_to_bottom():
                # Loop to scroll to bottom of page
                last_height = driver.execute_script("return document.documentElement.scrollHeight")
                scroll_count = 0
                while True:
                    # Scroll down
                    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                    # Wait for new videos to load
                    time.sleep(2)
                    # Calculate new scroll height
                    new_height = driver.execute_script("return document.documentElement.scrollHeight")
                    scroll_count += 1
                    logger.info(f"Scroll iteration {scroll_count} completed")
                    if new_height == last_height:
                        break
                    last_height = new_height

            # Scroll to load all videos
            scroll_to_bottom()

            # Wait for the video elements to load
            logger.info("Waiting for video elements to load...")
            wait = WebDriverWait(driver, 30)
            video_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-playlist-video-renderer")))

            # Extract video information
            logger.info("Extracting video information...")
            video_data = []
            for element in video_elements:
                # Get URL and title
                video_link = element.find_element(By.CSS_SELECTOR, "a#video-title").get_attribute('href')
                title = element.find_element(By.CSS_SELECTOR, "a#video-title").text
                
                if video_link and '/watch?v=' in video_link:
                    video_data.append({
                        'url': video_link,
                        'title': title
                    })

            driver.quit()
            logger.info(f"Successfully scraped {len(video_data)} videos from playlist")

            df_videos = pd.DataFrame(video_data)

            # Extract video key from URL by splitting on '=' and taking everything after it
            df_videos['video_key'] = df_videos['url'].str.split('=').str[1].str.split('&').str[0]

            df_videos.reset_index(inplace=True)
            df_videos.sort_values('index', ascending=False, inplace=True)
            df_videos.reset_index(drop=True, inplace=True)
            df_videos.drop(columns=['index'], inplace=True)
            df_videos.reset_index(inplace=True)
            df_videos.rename(columns={'index': 'id'}, inplace=True)

            os.makedirs('data', exist_ok=True)
            df_videos.to_csv('data/huberman_videos.csv', index=False)
            logger.info(f"DataFrame created with {len(df_videos)} video entries")

        def generate_transcripts_df(self):
            logger.info("Generating transcripts DataFrame...")
            # Create DataFrame
            data = pd.read_csv('data/huberman_videos.csv', encoding='latin1', index_col=False)
            title_dict = data.set_index('video_key')['title'].to_dict()
            with open('data/title_dict.pkl', 'wb') as f:
                pickle.dump(title_dict, f)
            os.makedirs('data/documents', exist_ok=True)

            for idx, video_key in enumerate(data['video_key']):
                filename = f'data/documents/{video_key}.txt'
                logger.info(f"Processing transcript {idx + 1}/{len(data)}: {video_key}")

                try:
                    fetched_transcript = ytt_api.get_transcript(video_key, languages=['en', 'en-US'])
                    
                    with open(filename, 'a', encoding='utf-8') as file:
                        for snippet in fetched_transcript:
                            file.write(snippet['text'] + '\n')  # Add newline after each snippet
                    logger.info(f"Successfully saved transcript for {video_key}")
                            
                except Exception as e:
                    logger.error(f"Error processing video {video_key}: {str(e)}")

        scrape_youtube_playlist(self)
        generate_transcripts_df(self)

    def make_chunks(self):
        client = OpenAI(api_key=self.openai_api_key)
        logger.info("Starting chunk creation process...")
        max_tokens = 1023 # 8191 is max length for text-embedding-3-large
        tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
        splitter = TextSplitter.from_huggingface_tokenizer(tokenizer, max_tokens)
        logger.info("Text splitter initialized with max_tokens={max_tokens}")

        # Create lists to store the data
        chunk_embeddings = []
        title_embeddings = []
        ids = []
        video_keys = []
        chunk_keys = []
        chunk_dict = {}
        
        # Iterates through a list of video IDs, where each ID corresponds to a podcast episode transcript.
        # Each transcript will be split into chunks and embedded along with its title for semantic search.
        with open('data/title_dict.pkl', 'rb') as f:
            title_dict = pickle.load(f)
        documents = list(title_dict.keys())  # ToDo: process using full dataset 
        # documents = ['4b6bwcWK6GE', 'H-XfCl-HpRM']
        logger.info(f"Processing {len(documents)} documents for chunking and embedding")
        
        for idx, video_key in enumerate(documents):
            logger.info(f"Processing document {idx + 1}/{len(documents)}: {video_key}")

            # Create Title Embeddings
            logger.info(f"Creating title embedding for {video_key}")
            title_vector = client.embeddings.create(
                input=title_dict[video_key],
                model="text-embedding-3-small"
            )

            # Load document and split into semantic chunks
            try:
                with open(f'data/documents/{video_key}.txt', 'r', encoding='utf-8') as file:
                    text_content = file.read()
            except FileNotFoundError:
                logger.warning(f"Document file not found for video ID: {video_key}")
                continue
                
            # ToDo: validate or rework so chunks are topical sentiments with varying lengths
            chunks = splitter.chunks(text_content) 
            logger.info(f"Created {len(chunks)} chunks for {video_key}")

            # Create data record of embeddings for each chunk of the transcript
            for chunk_idx, chunk in enumerate(chunks):
                # Create chunks directory if it doesn't exist 
                makedirs('data/chunks', exist_ok=True)
                
                # Write chunk to file with video ID and chunk number
                # Use a more filesystem-friendly naming convention
                chunk_key = f'{video_key}_chunk_{chunk_idx}'
                chunk_filename = f'data/chunks/{chunk_key}.txt'
                
                # Write chunk directly to file
                with open(chunk_filename, 'w', encoding='utf-8') as f:
                    f.write(chunk)
                
                # Add chunk to utility dictionary
                chunk_dict[chunk_key] = chunk

                # Create Chunk Embeddings
                logger.info(f"Creating embedding for chunk {chunk_idx + 1}/{len(chunks)} of document {idx + 1}/{len(documents)}: {video_key}")
                chunk_vector = client.embeddings.create(
                    input=chunk,
                    model="text-embedding-3-small"
                )

                # Append values of this record to column list
                chunk_embeddings.append(chunk_vector.data[0].embedding)
                title_embeddings.append(title_vector.data[0].embedding)
                ids.append(idx)
                video_keys.append(video_key)
                chunk_keys.append(chunk_key)

        with open('data/chunk_dict.pkl', 'wb') as f:
            pickle.dump(chunk_dict, f)
        logger.info("Chunk dictionary saved to data/chunk_dict.pkl")

        df = pd.DataFrame({
            'id': ids,
            'video_key': video_keys, 
            'chunk_key': chunk_keys,
            'content_vector': chunk_embeddings,
            'title_vector': title_embeddings,
        })
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'vector_id'}, inplace=True)
        df.to_csv('data/embeddings.csv', index=False)  

if __name__ == "__main__":
    
    # Initialize the ETL pipeline
    etl = ETL_pipeline()
    # Run the complete pipeline
    # etl.fetch_new_data()
    etl.make_chunks()