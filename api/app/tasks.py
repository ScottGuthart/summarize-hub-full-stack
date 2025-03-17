from rq import get_current_job
from app import create_app, db
from app.models import Task
from datetime import datetime
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
import pandas as pd
from filelock import FileLock
from pyarrow.parquet import ParquetFile
from app.datafile_utils import append_column
import sys

app = create_app()
app.app_context().push()


def _get_task_filename():
    job = get_current_job()
    task_id = job.get_id()
    task = Task.query.get(task_id)
    return task.filename

def _set_task_progress(
    progress, progress_message=None, task_id=None, **kwargs
):

    if task_id is None:
        job = get_current_job()
        task_id = job.get_id()
    else:
        task = Task.query.get(task_id)
        job = task.get_rq_job()

    if job: 
        job.meta["progress"] = progress
        if progress_message is not None:
            job.meta["progress_message"] = progress_message
        job.save_meta()
        task = Task.query.get(task_id)
        for k, v in kwargs.items():
            setattr(task, k, v)

        payload = {
            "task_id": task_id,
            "progress": progress,
            "progress_message": progress_message,
            "name": task.name,
            "description": task.description,
            "succeeded": task.succeeded,
        }
        app.logger.debug(f"Task: {payload}")
        if progress >= 0 and task.started_at is None:
            task.started_at = datetime.utcnow()
            print("task.started_at: ", task.started_at)
        else:
            task.last_updated = datetime.utcnow()
            print("task.last_updated: ", task.last_updated)
        if progress >= 100:
            task.complete = True
        db.session.commit()


def summarize():
    def run_batch(
        llm,
        template,
        inputs,
        content_only=True,
        progress_start=0,
        progress_end=100,
        progress_message=None
    ):
        """
        Takes a list of inputs and evaluates the templated prompts on each.
        
        Args:
            llm: The language model to use
            template: The prompt template string
            inputs: List of input texts to process
            content_only: returns only LLM response content
            progress_start: starting progress percentage
            progress_end: ending progress percentage
            progress_message: message to display during progress updates
        
        Returns:
            List of results in the same order as inputs
        """
        # Create chain
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | llm
        
        # Process in parallel
        total = len(inputs)
        results = [None] * total
        
        for i, result in chain.batch_as_completed(inputs):
            results[i] = result
            # Calculate progress based on number of completed results
            completed = sum(1 for r in results if r is not None)
            progress = progress_start + int(
                completed / total * (progress_end - progress_start)
            )
            _set_task_progress(progress, progress_message)
            
        if content_only:
            return [result.content.strip() for result in results]
        
        return results
    
    _set_task_progress(0, progress_message="Reading file...")
    try:
        fn = _get_task_filename()
        # Initialize the model
        llm_model = app.config['LLM_MODEL']
        llm = ChatOllama(model=llm_model, temperature=0.1)

        is_csv = fn.lower().endswith('.csv')
        if is_csv:
            df = pd.read_csv(fn)
        else:
            df = pd.read_excel(fn)

        _set_task_progress(10)

        # Load Content
        articles = df['Article Content'].tolist()

        # Define templates
        summary_template = "Summarize the following article:\n\n{content}"
        tag_template = """
        Extract 3-5 key topics as comma-separated tags from this summary.
        Respond with ONLY the tags:

        {content}
        """

        # Process summaries and tags
        summaries = run_batch(
            llm, 
            summary_template, 
            articles,
            progress_start=10,
            progress_end=60,
            progress_message="Generating article summaries..."
        )

        tags = run_batch(
            llm, 
            tag_template, 
            summaries,
            progress_start=60,
            progress_end=90,
            progress_message="Extracting tags from summaries..."
        )
        df['Summary'] = summaries
        df['Tags'] = tags

        # Requirements specify to append columns to the original file
        # Useful for excel files to preserve formatting
        append_column(fn, 'Summary', summaries)
        append_column(fn, 'Tags', tags)

        _set_task_progress(
            100,
            succeeded=True,
            progress_message="Processing complete!"
        )

    except Exception as e:
        exception_string = str(e)
        if "Max retries exceeded with url: /api/chat" in exception_string:
            error_message = "LLM server not responding."
        else:
            error_message = f"Error processing file: {str(e)}"
        _set_task_progress(
            100,
            progress_message=error_message,
            succeeded=False
        )
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
