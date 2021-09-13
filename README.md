# Traffic_accident_detection_from_VD

論文做的一些實驗

包含數據下載、整理

模型訓練、實際測試等

# 下載和轉換檔案

### 一開始請先匯入下載物件

```python
!git clone 'https://github.com/overred0704/Traffic_accident_detection_from_VD'
from Traffic_accident_detection_from_VD.Download_Function import VD_download
```

### 指定年份跟日期

```python
d = VD_download(2021, 4)
```

### 設定檔案儲存位置和起訖日期
colab預設的話是"/content/"

```python
d.set_path("/content/")
d.set_start_end(1,2)
```

### 開始下載並轉檔
```python
d.run()
```

### 最後可以把下載好的打包壓縮
```python
d.zip_file("檔名")
```
