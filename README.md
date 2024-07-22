
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

Support both fill in the blanks and multiple choices. All questions are organized in the JSON file. You will need question and answer for each entry. Notice, you if want something appear as blank use `[#!` and `#!]` to enclose the text.

```json
{
  "questions": [
    {
      "question": "请回答中国地理之最相关的问题",
      "answer": "中国的面积约为[#!960万#!]平方公里，是世界上面积第三大的国家。"
    },
    {
      "question": "有5张卡片，上面的数字分别是0、4、5、6、7，从中抽出3张所组成的三位数中能被4整除的有（ ）个。",
      "choices": [
        "A 11",
        "B 12",
        "C 10",
        "D 15"
      ],
      "answer": "D"
    }
  ]
}
```
