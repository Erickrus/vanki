
# VANKI

## Installation

```shell
git clone https://github.com/Erickrus/vanki/
pip3 install -r requirements.txt
```

## Launch vanki
```shell
python3 anki_app.py
```

## JSON Grammar

All questions are organized in the JSON file. You will need question and answer for each entry. Notice, you if want something appear as blank use `[#!` and `#!]` to enclose the text.

```json
{
  "questions": [{
    "question":"请回答中国地理之最相关的问题",
    "answer":"中国的面积约为[#!960万#!]平方公里，是世界上面积第三大的国家。"
  }]
}
```
