"""Direct Spark API test via langchain."""
import sys
import os
import time

sys.path.insert(0, '.')
os.chdir(r'D:\ZYY Project\marketing-council\backend')

from dotenv import load_dotenv
load_dotenv()

print('1. Loading SparkChatModel...')
t0 = time.time()
from app.core.llm_spark import SparkChatModel
t1 = time.time()
print(f'   Import done in {t1-t0:.1f}s')

print('2. Creating model...')
model = SparkChatModel(
    spark_app_id=os.getenv('SPARK_APP_ID'),
    spark_api_key=os.getenv('SPARK_API_KEY'),
    spark_api_secret=os.getenv('SPARK_API_SECRET'),
    spark_model_version='generalv3.5',
    max_tokens=50,
)
t2 = time.time()
print(f'   Model created in {t2-t1:.1f}s')

print('3. Testing _generate...')
from langchain_core.messages import HumanMessage
try:
    result = model._generate([HumanMessage(content='Say hello in 3 words')])
    print(f'   Result: {result.generations[0].message.content}')
    print(f'   Total time: {time.time()-t2:.1f}s')
except Exception as e:
    print(f'   Error: {e}')
    import traceback
    traceback.print_exc()
