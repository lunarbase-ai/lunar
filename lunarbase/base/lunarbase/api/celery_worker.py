from celery import Celery
import os
import logging
import asyncio
from dotenv import load_dotenv

from lunarbase.api import api_context
from lunarbase.api.utils import initialize_api_context

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)


celery_app.conf.enable_utc = False

@celery_app.task(name="run_lunarbase_workflow", bind=True)
def run_lunarbase_workflow(self, workflow_id, user_id, payload):
    unique_id = self.request.id 
    logging.info(f"WORKER: Starting workflow {workflow_id} for user {user_id}\nREQUEST_ID: {unique_id}")

    try:
        body = {
            "inputs": [
                {
                    "label": "PYTHONCODER-0",
                    "key": "code",
                    "value": f'result={payload}'
                }
            ],
        }

        
        initialize_api_context(api_context)
        asyncio.run(api_context.workflow_api.run_workflow_by_id(workflow_id, body["inputs"], user_id, execution_id=unique_id))

        logging.info(f"WORKER: Workflow {workflow_id} finished successfully.")

        return {"status": "success"}

    except Exception as e:
        logging.error(f"WORKER: Error processing workflow {workflow_id}: {e}")
        raise