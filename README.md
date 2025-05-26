# chat-with-llm

## TODO
* ~~Move message composition logic to `Message`~~
* ~~Move message rendering logic to `Message` (e.g. icon from severity)~~
* ~~Add option to include `OPENAI_KEY`~~
* Text summarization
* RAG

## Install and Run the sample ChatBot
- Install package
```
python -m venv venv
source venv/bin/activate
pip install -r requirements
```

- Configure python environment in VSCode
- Run the app
```
make run-app
```

Connect Ollama:
```
> /o
> /c localhost
```

Connect OpenAI (default, no host needed):
```
> /c
```