# huberman-lab-rag

---
### Setup

> environment  
> &emsp; Create virtual python environment:  
> &emsp; - `python -m venv /path/to/new/virtual/environment`  
> &emsp; Install dependancies:  
> &emsp; - `pip install -r requirements.txt`

> directory  
> &emsp; Make directory for data  
> &emsp; `data/`

> secrets   
> &emsp; Create file and add api keys  
> &emsp; `.env`: &ensp; OPENAI_API_KEY  

> database   
> &emsp; Stand up Docker Images for databases (Mongo is Optional)  
> &emsp; `mongo`: &emsp;&emsp;&emsp;&ensp;&ensp;  port <u>**27017**</u>   
> &emsp; `redis-stack`: &ensp;  port <u>**6379**</u> and <u>**8001**</u>  

> directories  
> &emsp; `data/`: &ensp; Add `prompt.txt` file 
                  &emsp; nest `redis_data/dump.rdb` if available 

> dependencies  
> &emsp; `pip install -r requirements.txt`

> **ToDo:** permissions  
> &emsp; `iam`: &ensp; Cloud stuff `S3`, `DB keys`, `Docker deployment`
<!-- > **ToDo:** permissions  
> &emsp; `iam`: &ensp; Cloud stuff `S3`, `DB keys`, `Docker deployment` -->

---
### Workflow  

> #### 1) Data Collection  
>> Scrape the URL for each podcast with `youtube_get_data.ipynb`  
&emsp; **- Note:** This script saves the scraped data to `huberman_videos.csv`  
> 
>> Generate transcripts by running `youtube_transcript_gen.ipynb`  
&emsp; **- Note:** Saves scripts to the `data/documents` dicretory as `.txt`

<br>

> Optional: Only relevant for Document DB design  
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

---
### Run the Application

> Run the file `app.py`  
> With a browser go to http://127.0.0.1:5000/ on your local host  
> &emsp; **Note:** Workflow steps 1, 3, 4 must be completed and your redis database active otherwise the app will fail   