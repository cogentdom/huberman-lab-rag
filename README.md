# huberman-lab-rag

### Setup
environment `.env`  
database `mongo`  

Create a new directory and name it `data`  
Add the file `youtube-extract-huberman.csv` to the `data` directory

Generate transcripts by running `youtube_transcript_gen.ipynb`

Chunk and Embed documents by running `document_embedding.ipynb`


Create Mongo database by running `pymongo_get_database.py`
Add documnets to Mong by running `pymongo_test_insert_file.py`