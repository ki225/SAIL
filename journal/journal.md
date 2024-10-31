# SAIL progress
### 2024/10/20
Task
- 發想題目，設計流程
- https://hackmd.io/jW4y_P1jRaKeHQek8peqZw?both

### 2024/10/22
Task
- 寫了一堆函數，他們可以從 s3 裡面撈表格來分析
- 花一堆時間在處理 JSON format error handler
- 試圖用 coze 把這坨東西流程化，但我不會用迴圈 22

TO-DO
- 把s3檔案讀取改成從 Google Sheet 讀取，要辦 Google Cloud Acc
- 讓整體流程更自動化

Wish
- 有個介面可以顯示特定資料夾下所有的表單，點選該表單後就會開始執行分析
- 但應該不可能

### 2024/10/13
Task
- 建 GCP 帳號跟相關 API 與權限設定
- 試了一大堆方法包括 Google App Script 和 Coze API，但 Coze API 免費次數只有三十次超少
- 在最後找到這個教程 https://www.analyticsvidhya.com/blog/2020/07/read-and-update-google-spreadsheets-with-python/

### 2024/10/29
Problem
- 怎麼一個禮拜回來後，Bedrock 就爆掉了....
- link: 
  - https://www.reddit.com/r/aws/comments/1gb2zx2/amazon_bedrock_prompt_management_error_too_many/
  - https://repost.aws/questions/QUK8qnLwJRQhOPV58H0sC41Q/bedrock-too-many-requests-please-wait-before-trying-again

Task
- 用 SDK 跟 API 拿 Google Sheet
- 拿 Gemini 先墊當作 bedrock ...
- 今天寫的在 function/v3
- 建了 AWS API gateway 和 lambda 拿來呼叫，不然直接把金鑰什麼的直接寫進程式再跑超級危險 TAT

### 2024/10/30
Task
- Gemini 也用到上限了 QWQ
- 聽了老師建議用 Dify 看看，所以裝了 Docker, Ollema 那些的
- 結果就是 Dify 比 Coze 還難用，原地回去 Coze

### 2024/10/31
Task
- 用 Coze 吧，一直修 prompt，還有想辦法用有限的工具去實現我要的功能
- 寫一點點 code 去做功能