# huberman-lab-rag

### Setup

> environment   
> &emsp; `.env`: &ensp; openai key  

> database   
> &emsp; `mongo`: &emsp;&emsp;&emsp;&ensp;&ensp;  port <u>**27017**</u>   
> &emsp; `redis-stack`: &ensp;  port <u>**6379**</u> and <u>**8001**</u>  

> directory  
> &emsp; `data/`

> dependencies  
> &emsp; `pip install -r requirements.txt`

> **ToDo:** permissions  
> &emsp; `iam`: &ensp; Cloud stuff `S3`, `DB keys`, `Docker deployment`


### Workflow  

> Scrape the URL for each podcast with `youtube_get_data.ipynb`  
&emsp; **- Note:** This script saves the scraped data to `huberman_videos.csv`  

<br>

> Generate transcripts by running `youtube_transcript_gen.ipynb`

<br>

> Chunk and Embed documents by running `document_embedding.ipynb`

<br>

> Create Mongo database by running `pymongo_get_database.py`  
> Add documnets to Mong by running `pymongo_test_insert_file.py`