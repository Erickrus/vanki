
# VANKI

Voice ANKI is a Desktop application based on pyqt6. It can help users use answer sheets to quickly memorize the content of questions. Currently, answer sheets support fill-in-the-blank questions and multiple-choice questions. In order to improve the memory effect, the application also supports a voice reading. [中文版](https://github.com/Erickrus/vanki/blob/main/README_CN.md)

## Installation

```shell
git clone https://github.com/Erickrus/vanki/
pip3 install -r requirements.txt
```

## Launch vanki
```shell
python3 anki_app.py
```

![demo](https://github.com/Erickrus/vanki/blob/main/demo.gif?raw=true)


## JSON Grammar

Support both fill in the blanks and multiple choices. All questions are organized in the JSON file. You will need question and answer for each entry. Notice, you if want something appear as blank use `[#!` and `#!]` to enclose the text.

```json
{
  "questions": [
    {
      "question": "Please answer the most relevant questions about US geography",
      "answer": "With an area of almost [#!3,800,000#!] square miles ([#!9,840,000#!] square km), the United States is the [#!fourth#!] largest country in the world"
    },
    {
      "question": "There are 5 cards with numbers 0, 4, 5, 6, and 7 on them. How many three-digit numbers can be divided by 4 when 3 cards are drawn?",
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
