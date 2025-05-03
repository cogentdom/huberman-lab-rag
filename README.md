# huberman-lab-rag

---
### Setup

> environment   
> &emsp; `.env`: &ensp; OPENAI_API_KEY  

> database   
> &emsp; `mongo`: &emsp;&emsp;&emsp;&ensp;&ensp;  port <u>**27017**</u>   
> &emsp; `redis-stack`: &ensp;  port <u>**6379**</u> and <u>**8001**</u>  

> directory  
> &emsp; `data/`

> dependencies  
> &emsp; `pip install -r requirements.txt`

> **ToDo:** permissions  
> &emsp; `iam`: &ensp; Cloud stuff `S3`, `DB keys`, `Docker deployment`

---
### Workflow  

> #### 1) Data Collection  
>> Scrape the URL for each podcast with `youtube_get_data.ipynb`  
&emsp; **- Note:** This script saves the scraped data to `huberman_videos.csv`  
> 
>> Generate transcripts by running `youtube_transcript_gen.ipynb`  
&emsp; **- Note:** Saves scripts to the `data/documents` dicretory as `.txt`

<br>

> #### 2) Store Documents
>> Create Mongo database by running `pymongo_get_database.py`  
>
>> Add documnets to Mong0 by running `pymongo_test_insert_file.py`

<br>

> #### 3) Preprocessing
>> Chunk and Embed documents by running `document_embedding.ipynb`  
&emsp; **- Note:** Creates `embedding.csv`  

<br>

> #### 4) Index Vectors
>> Redis `redis_index_embeddings.ipynb`

<br>

> #### 5) Query with Context
>> Utilizes retrived documents to add context to LLM prompt `query_database.ipynb`
>
>> Abstracts using `utils.py` 

