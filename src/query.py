import copy
import os
import random
from datetime import datetime
from typing import Dict

import boto3
import openai
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from langchain import OpenAI
from llama_index import GPTSimpleVectorIndex, LLMPredictor

logger = Logger()
tracer = Tracer()

"""
- 回答を早く返すために、コールドスタンバイで、インデックスをロードしておく
    - デプロイ前に、環境変数 INDEX_BUCKER_NAME の S3バケットに index.json を配置する必要あり
    - インデックスの更新の度に再デプロイが必要
"""
openai.api_key = os.environ["OPENAI_API_KEY"]

# Lambdaの/tmp配下にインデックスを格納
tmp_index_file_name = (
    "/tmp/index-"
    + datetime.now().strftime("%Y-%m-%d-%H-%M-%S-")
    + str(random.randint(0, 999999))
    + ".json"
)
s3 = boto3.client("s3")
s3.download_file(os.environ["INDEX_BUCKER_NAME"], "index.json", tmp_index_file_name)
# index.jsonをロード
llm_predictor = LLMPredictor(
    llm=OpenAI(temperature=0.7, model_name="gpt-3.5-turbo", max_tokens=512)
)
loaded_index = GPTSimpleVectorIndex.load_from_disk(
    save_path=tmp_index_file_name,
    llm_predictor=llm_predictor,
)
# Lambdaの/tmp配下に格納したインデックスを削除
os.remove(tmp_index_file_name)


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def handler(event: Dict, context: LambdaContext) -> Dict:
    """
    LlamaIndexで作成済みのインデックスにクエリを投げて、質問に対する回答を返す

    event:
    {
        "input": {
            "question": "hoge"
        },
        "execution": {
            "Execution":{
                ..snip..
            },
            "StateMachine":{
                ..snip..
            },
            "State":{
                ..snip..
            }
        }
    }

    return:
    {
        "question": "hoge",
        "answer": "fuga"
    }
    """
    try:
        _input: Dict = copy.deepcopy(event["input"])

        question = event["input"]["question"]
        answer = str(loaded_index.query(question))
        _input["answer"] = answer

        return _input

    except Exception as e:
        logger.exception("throw exception in query")
        raise e
