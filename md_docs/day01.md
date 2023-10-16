# [Day01] 緣起及Python學習資源分享
## 緣起
不知道諸位會不會常遇到一種情況，就是當您那陣子很常使用程式的某種功能，會非常熟練，也了解了大部份的坑要怎麼解，覺得自己已經掌握了這項技能。但是日子久了，又面臨差不多問題時，只回想起大概解決問題的流程，卻寫不出程式碼。此時，會不斷翻查零亂的code snippet，及憑印象去`Google`或`Stack Overflow`找出以前那幾篇幫助您想通問題的Q&A或是部落格文章。雖然在經過一陣子查找跟燒腦後，問題還是解決了。但時不時來這麼一次，也著實心累。

本系列文希望能以筆記的型式來代替上述的無限迴圈。在每次需要快速refresh的時候，只要看著筆記內的原理、幾個範例及要注意的坑，就能夠快速進入可以coding的狀態，就像是現在的自己在與未來的自己對話一般（`註1`）。

## 十翼預定內容
每翼規劃2~4篇不等。
* 初翼 - Tips
* 次翼 - Decorator
* 三翼 - Property
* 四翼 - Descriptor
* 五翼 - Metaclasses
* 六翼 - How `dot` works
* 七翼 - Protocols
* 八翼 - Scope
* 九翼 - New stuff
* 末翼 - Term Project

## Python學習資源
下面列出幾個，在我們學習Python時很有幫助的資源。

### Python 3:Deep Dive
此為`Dr. Fred Baptiste`於[udemy](https://www.udemy.com/user/fredbaptiste/)上的課程，共有part1~part4四個部份。講解清楚且內容紮實，個人極度推薦。另外，`Dr. Fred Baptiste`於YouTube上也建立了[MathByte Academy](https://www.youtube.com/@mathbyteacademy)頻道，進行Python教學。如果您不確定適不適合他的課程，可以先看幾部影片試試。但我相信看過之後，您應該會更迫不及待想要上完所有課程。

### Python Morsels
[Python Morsels](https://pym.dev/ref/forkind/)是由`Trey Hunner`建立的學習平台。一開始是每週經由E-mail寄出問題(含test)，並於幾天後寄出解答。現在已經進化成網站型式，且如果是年繳用戶的話，可以看到所有的問題（約有200多題），網站會依您自訂的程度給出建議的問題。問題一般有一個基本題，然後2~3個bonus問題，其難度即便是`novice`級別，也相當具有挑戰性，每題基本上都得解上好幾個小時。到後面的`advanced`級別更是會讓您題題都懷疑人生，因為其test相當全面，要想全部通過著實不易。但實力總是在苦難中累積，經過這200多道題的摧殘之後，終於覺得自己有一點點懂Python，具有探索這個世界的門票了。此外，`Trey`最近也針對不同的Python知識寫下較短的文章，及拍影片講解。

### Weekly Python Exercise
[Weekly Python Exercise](https://store.lerner.co.il/wpe)是由`Reuven Lerner`建立的學習系統。其共有`A1`、`A2`、`A3`、`B1`、`B2`及`B3`六個等級。每個等級是15週的課程，每週會寄出問題(含test)，下週會寄出答案。過程中有問題的話，可以上專屬的討論區詢問。每幾個星期會有線上Q&A環節，`Reuven`會當場講解，或是您想要先提供問題，之後再回看也可以。相比於`Python Morsels`，`Weekly Python Exercise`的問題屬於比較「親民」一點，我覺得比較適合初學到中等程度的朋友。`Reuven`是一個很樂於和人互動的老師，如果解題過程中需要幫助，可以直接在討論區tag他或是寫E-mail給他，一般來說，很快就會得到回覆。

### Talk Python
[Talk Python](https://talkpython.fm)是由`Michael Kennedy`建立的學習平台，裡面有付費的課程以及幾乎每週更新的[podcast](https://talkpython.fm/episodes/all)。其每集podcast約一個小時出頭，會針對單一主題訪問一到數位該領域的高手，連咱們的Python老爹`Guido`也曾經當過嘉賓。

### Python Bytes
[Python Bytes](https://pythonbytes.fm)是由`Michael Kennedy`及`Brian Okkan`一起經營的podcast，也幾乎是每週都有更新。相比於`Talk Python podcast`每集著重於一個主題，`Python Bytes`算是產業速報，每集約30~40分鐘，可以快速更新近來的Python大小事。

### Real Python
[Real Python](https://realpython.com)以提供高品質的Python tutorial著稱。許多Python開發者在面對不熟悉的功能或package時，都會優先尋找`Real Python`是否有tutorial可以幫忙快速進入狀況。其[podcast](https://realpython.com/podcasts/rpp/)也為每週更新，風格近似於`Talk Python`。

### PyBites
[PyBites](https://pybit.es/)是`Bob Belderbos`與 `Julian Sequeira`連手經營的學習平台，我特別推薦他們的[部落格文章](https://pybit.es/articles/)。他們的文章篇幅不會太長，但很多示例及說明都會發人深省。

### Corey Schafer
[Corey](https://www.youtube.com/@coreyms)的YouTube頻道上有許多講解清楚的Python影片，只可惜最近幾年他的重心移到別處，已不太更新了。

### Python Documentation
[Python Documentation](https://docs.python.org/3/index.html)有著豐富的資源，只是初學的時候可能有看沒懂。但當您有一些Python經驗後，會發現這真是一個寶庫啊。例如當您對`class`有任何問題時，我特別推薦[Reference中的Data Model](https://docs.python.org/3/reference/datamodel.html)及[Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html)。其中`Descriptor HowTo Guide`是由Python大神`Raymond Hettinger`所著，篇幅雖然不長，但句句精鍊，雖然已經拜讀多次，但每次閱讀總能有更深的體悟。

### Python PEP
[Python PEP(Python Enhancement Proposals)](https://peps.python.org/)是記錄Python各種規則及延伸功能是否被接受或拒絕的檔案庫。在這裡可以看到技術沿革的軌跡，了解諸位Python大神對於新功能或變動，所帶來各種利弊的看法。有時候對於新功能，也會於`PEP`發佈相關的tutorial。


## 文章慣用詞彙
* `object`: Python中被所有`class`繼承的那個`object`。
* `obj`: 代指任何Python物件。

## Disclaimer
* `Python Morsels`的`Trey Hunner`特地為我們建立了註冊連結。如果有朋友利用上述連結註冊，本人可能因此受益。

* 本系列文的絕大部份為整理各種Python學習資料而來。我們盡量在引用他人成果時，附上連結或出處，但是請原諒部份內容是由過往零散的筆記中翻出，出處實已不可考。

## 備註
註1：[十翼](https://zh.wikipedia.org/zh-tw/%E5%8D%81%E7%BF%BC)為輔助學習「易學」的十對翅膀，讓我們更有機會能略懂它的博大精深。本系列文藉此喻義，希望針對十個Python主題，寫下筆記，以便將來的自己在迷惘時，能有所參考。
