
# VANKI

Voice ANKI 是一款基于pyqt6的桌面应用，可以帮助用户使用答题卡快速记忆题目内容，目前答题卡支持填空题和选择题，为了提高记忆效果，应用还支持语音朗读。
[English version](https://github.com/Erickrus/vanki/blob/main/README.md)

## 安装

```shell
git clone https://github.com/Erickrus/vanki/
pip3 install -r requirements.txt
```

## 启动 vanki 应用
```shell
python3 anki_app.py
```

![demo](https://github.com/Erickrus/vanki/blob/main/demo.gif?raw=true)


## 答题卡 JSON 语法

支持填空题和多选题。所有答题卡都以JSON形式组织。每个答题卡片需要包含"question"和"answer"。注意，如果您希望某些内容显示为填空形式，请使用 `[#!` 和 `#!]` 来包住填空内容。

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
