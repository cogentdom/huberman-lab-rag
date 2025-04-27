# Follow up Issues

- Chunks have `\n` derived from the `.txt` files  

- Create some util function to pull the text of a `video_id` (`.txt` or `mongo` workflow?)  

<br>

---  
From `document_embedding`  
> 
> Potential design options:  
>     1. create a list of dictionaries and store the data in a dataframe using columns: 'embedding', 'rank', 'chunk_id', 'video_id'  
>     2. redis  
>     3. vector db  
>     4. mongo collections  
>     5. pickle  
>
>
> ToDo:
> - Add chunks to Mongo
> - Make Query embedding function
> - Rank Query to embedding with chunks
>     - Will need to engineer a data object to handle this 
>         - Add a secondary "key" object?
> - Generate response using top chunks  

---