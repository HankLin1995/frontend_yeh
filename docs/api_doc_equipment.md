# 機具借用與歸還 API 文檔

## 概述

本文檔描述了機具借用和歸還的 API 接口。這些接口允許前端應用程序執行機具的借用和歸還操作。

## 基本資訊

- **Base URL**: `/equipments`
- **Content-Type**: `application/json`

## 1. 機具借用

### 請求

```
POST /equipments/borrow
```

### 請求參數

| 參數名稱 | 類型 | 必填 | 描述 |
|---------|------|------|------|
| EquipmentID | Integer | 是 | 機具 ID |
| UserID | String | 是 | 借用人 ID |
| CaseID | Integer | 否 | 相關案件 ID (如適用) |
| ActionType | String | 是 | 必須為 "借用" (BORROW) |
| Quantity | Integer | 否 | 借用數量 (預設為 1，必須大於 0) |
| Note | String | 否 | 備註說明 |

### 請求範例

```json
{
  "EquipmentID": 1,
  "UserID": "user123",
  "CaseID": 456,
  "ActionType": "借用",
  "Quantity": 1,
  "Note": "用於現場勘查"
}
```

### 回應

成功時返回 HTTP 狀態碼 200 和借用記錄詳情：

```json
{
  "LogID": 123,
  "EquipmentID": 1,
  "UserID": "user123",
  "CaseID": 456,
  "ActionType": "借用",
  "Quantity": 1,
  "Note": "用於現場勘查",
  "ActionTime": "2025-08-09T09:50:23"
}
```

### 錯誤回應

- **404 Not Found**: 找不到指定的機具
  ```json
  {
    "detail": "Equipment not found"
  }
  ```

- **400 Bad Request**: 機具不可借用
  ```json
  {
    "detail": "Equipment is not available for borrowing"
  }
  ```

## 2. 機具歸還

### 請求

```
POST /equipments/borrow
```

### 請求參數

| 參數名稱 | 類型 | 必填 | 描述 |
|---------|------|------|------|
| EquipmentID | Integer | 是 | 機具 ID |
| UserID | String | 是 | 歸還人 ID |
| CaseID | Integer | 否 | 相關案件 ID (如適用) |
| ActionType | String | 是 | 必須為 "歸還" (RETURN) |
| Quantity | Integer | 否 | 歸還數量 (預設為 1，必須大於 0) |
| Note | String | 否 | 備註說明 |

### 請求範例

```json
{
  "EquipmentID": 1,
  "UserID": "user123",
  "CaseID": 456,
  "ActionType": "歸還",
  "Quantity": 1,
  "Note": "設備狀況良好"
}
```

### 回應

成功時返回 HTTP 狀態碼 200 和歸還記錄詳情：

```json
{
  "LogID": 124,
  "EquipmentID": 1,
  "UserID": "user123",
  "CaseID": 456,
  "ActionType": "歸還",
  "Quantity": 1,
  "Note": "設備狀況良好",
  "ActionTime": "2025-08-09T10:15:45"
}
```

### 錯誤回應

- **404 Not Found**: 找不到指定的機具
  ```json
  {
    "detail": "Equipment not found"
  }
  ```

- **400 Bad Request**: 機具目前未被借出
  ```json
  {
    "detail": "Equipment is not currently borrowed"
  }
  ```

## 3. 查詢機具借用記錄

### 請求

```
GET /equipments/{equipment_id}/borrow_logs
```

### 請求參數

| 參數名稱 | 類型 | 必填 | 描述 |
|---------|------|------|------|
| equipment_id | Integer | 是 | 機具 ID (路徑參數) |
| skip | Integer | 否 | 跳過的記錄數 (預設為 0) |
| limit | Integer | 否 | 返回的最大記錄數 (預設為 100) |

### 回應

成功時返回 HTTP 狀態碼 200 和借用/歸還記錄列表：

```json
[
  {
    "LogID": 124,
    "EquipmentID": 1,
    "UserID": "user123",
    "CaseID": 456,
    "ActionType": "歸還",
    "Quantity": 1,
    "Note": "設備狀況良好",
    "ActionTime": "2025-08-09T10:15:45"
  },
  {
    "LogID": 123,
    "EquipmentID": 1,
    "UserID": "user123",
    "CaseID": 456,
    "ActionType": "借用",
    "Quantity": 1,
    "Note": "用於現場勘查",
    "ActionTime": "2025-08-09T09:50:23"
  }
]
```

## 4. 查詢單一借用/歸還記錄

### 請求

```
GET /equipments/borrow/{log_id}
```

### 請求參數

| 參數名稱 | 類型 | 必填 | 描述 |
|---------|------|------|------|
| log_id | Integer | 是 | 借用/歸還記錄 ID (路徑參數) |

### 回應

成功時返回 HTTP 狀態碼 200 和記錄詳情：

```json
{
  "LogID": 123,
  "EquipmentID": 1,
  "UserID": "user123",
  "CaseID": 456,
  "ActionType": "借用",
  "Quantity": 1,
  "Note": "用於現場勘查",
  "ActionTime": "2025-08-09T09:50:23"
}
```

### 錯誤回應

- **404 Not Found**: 找不到指定的記錄
  ```json
  {
    "detail": "Borrow log not found"
  }
  ```

## 注意事項

1. 機具借用時，該機具的狀態必須為 "可用" (`AVAILABLE`)，借用後狀態會自動變更為 "借出中" (`BORROWED`)。
2. 機具歸還時，該機具的狀態必須為 "借出中" (`BORROWED`)，歸還後狀態會自動變更為 "可用" (`AVAILABLE`)。
3. 所有時間戳記都是以 UTC 時間表示。
4. 借用和歸還操作都使用相同的 API 端點，僅通過 `ActionType` 參數區分操作類型。

## 機具狀態說明

- `AVAILABLE` (可用): 機具可以被借用
- `BORROWED` (借出中): 機具已被借出，不可再次借用
- `MAINTENANCE` (維修中): 機具正在維修，不可借用
- `RETIRED` (報廢): 機具已報廢，不可借用
