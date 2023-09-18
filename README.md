# 생성 AI 이해와 LLM 적용 및 실습

## 사용 방법
```
// 가상 환경 구성. root 디렉토리에서 실행
$ pyenv local
$ nvm use
$ pipenv install

// 앱 구동을 위해 각 app 디렉토리에 .env 파일 생성 필요. 파일 안에 key 기록
OPENAI_API_KEY=...

// 각 web app 디렉토리에서 실행(project_helper_bot, example_marketingEx, example_news_service 등)
$ pc init
$ pc run
```

## project_helper_bot 앱

- 카카오 싱크 api에 대해 설명해주는 앱
