# [Day30] specialist與Python3.12 f-strings in the grammar

今天我們推薦一個名為`specialist`的library，並試著了解Python3.12的`f-strings in the grammar`。有關於Python3.12的更新可以參考[What’s New In Python 3.12](https://docs.python.org/3.12/whatsnew/3.12.html)或是[Real Python的摘要](https://realpython.com/python312-new-features/)。這次更新最令我們開心的小功能是，`pathlib`終於有了[path.walk](https://realpython.com/python312-new-features/#pathwalk-list-files-and-subdirectories)，省去了當要列出所有資料夾及檔案時，需要呼叫`os.walk`的窘境。

## specialist
Python3.11相比於3.10，執行速度提高不少，有很大原因是因為微軟的`Fast CPython Team`，做了許多最佳化。詳細的內容可以參考[PEP 659 – Specializing Adaptive Interpreter](https://peps.python.org/pep-0659/)及`TalkPython`
的[381集-Python Perf: Specializing, Adaptive Interpreter](https://talkpython.fm/episodes/show/381/python-perf-specializing-adaptive-interpreter)和[388集-Python 3.11 is here and it's fast](https://talkpython.fm/episodes/show/388/python-3.11-is-here-and-its-fast)。

我們特別推薦大家看看[specialist](https://github.com/brandtbucher/specialist)這個由`Fast CPython Team`的成員`Brandt Bucher`所維護的library。`specialist`會用不同顏色，來標注程式中還有機會可以提升速度的地方。

說明文件中舉了一個淺顯易懂的攝式與華式溫度轉換的例子，下面是我們一般會寫出的程式。
![original_code](https://raw.githubusercontent.com/brandtbucher/specialist/main/examples/output-1.png)

下面是經過`specialist`建議所修改的程式。只需要將`int`改為`float`(`32`->`32.0`)及將`5/9`和`9/5`加上括號，即可以提升速度。
![specialized_code](https://raw.githubusercontent.com/brandtbucher/specialist/main/examples/output-4.png)

我們建議大家可以按照自己習慣的方式來寫code，等到大部份的邏輯寫好後，再使用`specialist`來幫忙看看有沒有可以改進的地方。

如果想快速了解Python3.11~Python3.12速度提升的關鍵，可以觀看`Brandt Bucher`於[PyCon US 2023](https://www.youtube.com/watch?v=shQtrn1v7sQ)的演講，裡面也有稍微提到`specialist`。

## f-strings in the grammar
[PEP-701 Syntactic formalization of f-strings](https://peps.python.org/pep-0701/)中，說明了這個變更，將可以大幅降低維護的難度，並讓`f-strings`的`parser`符合[official Python grammar](https://docs.python.org/3/reference/lexical_analysis.html#f-strings)。比較有趣的是`PEP-701`於`2022-11-15`提出，馬上就被接受並導入在Python3.12中，這開發速度著實有點驚人。因為Python3.12除了繼續使用各種策略進行速度提升外，也花費不少精力在[放寬Gil的限制](https://docs.python.org/3.12/whatsnew/3.12.html#pep-684-a-per-interpreter-gil)。

### Quote reuse
在Python3.11以前，四種表示`str`型態的符號，包括`'`、`"`、`'''`及`"""`在同一個`f-string`中只能使用一次，不能`nested`，所以最極限的`f-string`寫法會像是：
```
#python3.11
>>> f"""{f'''{f'{f"{1+1}"}'}'''}"""
2
```
但在Python3.12，我們可以：
```
#python3.12
>>> f"{f"{f"{f"{f"{f"{1+1}"}"}"}"}"}"
'2'
```
另外，這個變動讓我們可以在`f-string`中，重複使用同一種`str`型態的符號。
```
>>> songs = ['Take me back to Eden', 'Alkaline', 'Ascensionism']
#python3.11
>>> f"This is the playlist: {', '.join(songs)}"
'This is the playlist: Take me back to Eden, Alkaline, Ascensionism'

#python3.12
>>> f"This is the playlist: {", ".join(songs)}"
'This is the playlist: Take me back to Eden, Alkaline, Ascensionism'
```

### Multi-line expressions and comments
可以使用`Multi-line expression`及加入`comment`。
```
#python3.12
>>> f"This is the playlist: {", ".join([
...     'Take me back to Eden',  # My, my, those eyes like fire
...     'Alkaline',              # Not acid nor alkaline
...     'Ascensionism'           # Take to the broken skies at last
... ])}"
'This is the playlist: Take me back to Eden, Alkaline, Ascensionism'
```

### Backslashes and unicode characters
可以使用`Backslash`。所以可以在`f-string`內直接使用像`'\n'`或`'\t'`等符號來連接`str`。此外，也會連帶影響[unicode escape sequence](https://docs.python.org/3.12/reference/lexical_analysis.html#escape-sequences)。
```
#python3.12
>>> print(f"This is the playlist: {"\n".join(songs)}")
This is the playlist: Take me back to Eden
Alkaline
Ascensionism

>>> print(f"This is the playlist: {"\N{BLACK HEART SUIT}".join(songs)}")
This is the playlist: Take me back to Eden♥Alkaline♥Ascensionism
```
### 個人想法
自從`f-string`於Python3.6導入之後，一直都是它的愛用者。此次的變更，個人覺得不太習慣，感覺很不`pythonic`，可能得花些時間才能適應。因為綜合這三個特點來看，「好像」是在鼓勵我們於`f-string`中進行較冗長或是`nested`的操作，且因為`quote`可以重複使用，在沒有`IDE`顏色的提示下，我很懷疑自己是否能看得懂程式碼。但是從`pep-701`的討論中，可以看出開發者認為利遠大於弊，或許身為Python使用者的我們，得順應發展做出改變才是。


## 感謝時間
非常開心又完成一次充實的鐵人挑戰賽，請容我們用些許篇幅，感謝幫助我們完賽的兩位功臣。

1. 很少人的人生可以一帆風順，大部份的情況是在順境與逆境中不斷切換。如何在順境中感恩惜福，並在逆境中努力不餒，是我們一生的課題。傅佩榮教授對於易經內容的傳授，幫助我對人生有了更深的體悟。建議有興趣進入易經世界的朋友，可以參考傅教授的[YouTube傅佩榮國學官方頻道](https://www.youtube.com/c/%E5%82%85%E4%BD%A9%E6%A6%AE%E5%9C%8B%E5%AD%B8%E5%AE%98%E6%96%B9%E9%A0%BB%E9%81%93)或*傅佩榮解讀易經*（於YouTube內有相關購書連結）。
2. 第二位是超級好用的`Markdown`線上編輯平台[HackMD](https://hackmd.io/)。本系列文的所有編輯皆是在`HackMD`上完成，於發文前再直接貼過來，由衷感謝他們開發了這個好用的平台。

## Python交流
如果有同好想交流Python的原理或知識，可以透過[LinkedIn](https://cv.ycwu.space)或[E-mail](mailto:jerry@ycwu.space) 聯絡我。