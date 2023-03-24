# llamaindex-lambda

LlamaIndex を AWS Lambda で動かすための PoC です。

# デプロイ

## 事前準備

- serverless.yml の custom > s3 > environment > IndexBucketName に、index.json を保存した S3 バケット名を記入する
- デプロイリージョンの AWS Systems Manager のパラメータストアで、/llamaindex-lambda/ステージ名/OPENAI_API_KEY という名前で、値に OpenAI の API キーを設定したパラメータを作成する

## パッケージやライブラリのインストール

- 下記のコマンドでパッケージやライブラリのインストールします。

```bash
npm ci
pipenv install
```

## Serverless Framework を使ってデプロイ

```bash
sls deploy --stage {ENV}
```
