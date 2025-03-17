# SummarizeHub

## Installation

1. **Redis**

   - [Install Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)

2. **Ollama**

   - [Install Ollama](https://ollama.com/)
   - Pull model: `ollama pull llama3-chatqa:8b` # 4.7 GB

3. **Build Frontend**

   ```bash
   npm install
   npm run build
   ```

4. **Python Environment**

   ```bash
   cd api
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   flask db upgrade
   ```

   Note: Developed with Python 3.9.19

## Running the App

You will need four separate processes running in different terminal windows: Ollama, Redis server, RQ worker, and Flask server.

1. **Redis**

   ```bash
   redis-server
   ```

2. **Ollama (llm)**

`ollama serve`

3. **Worker**

   ```bash
   # in ./api
   source venv/bin/activate
   export FLASK_APP=flaskapp.py

   # on mac only (for rq):
   export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

   rq worker flaskapp-tasks
   ```

4. **Flask**

   ```bash
   cd api
   source venv/bin/activate
   export FLASK_APP=flaskapp.py
   flask run
   ```

5. Navigate to http://127.0.0.1:5000/ in your web browser.

## Approach

SummarizeHub processes articles in two steps:

1. **Summarization**

   - Uses the Llama 3 Chat model (8B parameters) for high-quality summarization
   - Processes articles in parallel using Redis Queue for efficient handling
   - Generates concise 1-2 sentence summaries that capture the key points
   - Low temperature (0.1) setting ensures consistent, factual outputs

2. **Tag Generation**
   - Automatically extracts 3-5 key topics from each summary
   - Tags are normalized to lowercase for consistency
   - Helps with article categorization and search

## TODO

### Error Handling

- File issues
- Article length limits

### General

- Text chunking
- File cleanup

## Future Improvements

- Dynamic context window based on LLM
