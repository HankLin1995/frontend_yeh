# Leave Management API Documentation

本文檔提供請假管理系統 API 的詳細說明，包括年度假別配額管理和請假申請流程。

## 目錄

1. [年度假別配額管理](#年度假別配額管理)
   - [建立員工年度假別配額](#建立員工年度假別配額)
   - [取得特定假別配額](#取得特定假別配額)
   - [取得特定使用者的假別配額](#取得特定使用者的假別配額)
   - [更新假別配額](#更新假別配額)
   - [根據年資自動計算特別休假天數](#根據年資自動計算特別休假天數)
2. [請假申請管理](#請假申請管理)
   - [提交請假申請](#提交請假申請)
   - [取得特定請假申請](#取得特定請假申請)
   - [查詢請假申請](#查詢請假申請)
   - [審核請假申請](#審核請假申請)
   - [查詢假別餘額](#查詢假別餘額)

## 年度假別配額管理

### 建立員工年度假別配額

建立員工特定年度的假別配額，包括特別休假、事假和病假天數。

**URL:** `/leave/entitlements`

**Method:** `POST`

**請求參數:**

```json
{
  "UserID": "string",
  "Year": "integer",
  "AnnualSpecialLeave": "decimal",
  "PersonalLeave": "decimal",
  "SickLeave": "decimal"
}
```

**參數說明:**
- `UserID`: 員工ID
- `Year`: 年度
- `AnnualSpecialLeave`: 特別休假天數
- `PersonalLeave`: 事假天數
- `SickLeave`: 病假天數

**回應:**

```json
{
  "EntitlementID": "integer",
  "UserID": "string",
  "Year": "integer",
  "AnnualSpecialLeave": "decimal",
  "PersonalLeave": "decimal",
  "SickLeave": "decimal",
  "UpdateTime": "datetime"
}
```

**錯誤情況:**
- 400: 年度配額已存在
- 404: 使用者不存在
- 500: 伺服器錯誤

### 取得特定假別配額

根據配額ID取得特定假別配額資訊。

**URL:** `/leave/entitlements/{entitlement_id}`

**Method:** `GET`

**URL 參數:**
- `entitlement_id`: 配額ID

**回應:**

```json
{
  "EntitlementID": "integer",
  "UserID": "string",
  "Year": "integer",
  "AnnualSpecialLeave": "decimal",
  "PersonalLeave": "decimal",
  "SickLeave": "decimal",
  "UpdateTime": "datetime"
}
```

**錯誤情況:**
- 404: 假別配額不存在

### 取得特定使用者的假別配額

取得特定使用者的所有年度假別配額或特定年度的假別配額。

**URL:** `/leave/entitlements/user/{user_id}`

**Method:** `GET`

**URL 參數:**
- `user_id`: 使用者ID

**查詢參數:**
- `year`: 年度 (選填)

**回應:**

```json
[
  {
    "EntitlementID": "integer",
    "UserID": "string",
    "Year": "integer",
    "AnnualSpecialLeave": "decimal",
    "PersonalLeave": "decimal",
    "SickLeave": "decimal",
    "UpdateTime": "datetime"
  }
]
```

### 更新假別配額

更新特定假別配額的資訊。

**URL:** `/leave/entitlements/{entitlement_id}`

**Method:** `PUT`

**URL 參數:**
- `entitlement_id`: 配額ID

**請求參數:**

```json
{
  "AnnualSpecialLeave": "decimal (optional)",
  "PersonalLeave": "decimal (optional)",
  "SickLeave": "decimal (optional)"
}
```

**回應:**

```json
{
  "EntitlementID": "integer",
  "UserID": "string",
  "Year": "integer",
  "AnnualSpecialLeave": "decimal",
  "PersonalLeave": "decimal",
  "SickLeave": "decimal",
  "UpdateTime": "datetime"
}
```

**錯誤情況:**
- 404: 假別配額不存在

### 根據年資自動計算特別休假天數

根據員工年資自動計算特別休假天數，依照勞基法規定。

**URL:** `/leave/entitlements/auto-calculate/{user_id}/{year}`

**Method:** `POST`

**URL 參數:**
- `user_id`: 使用者ID
- `year`: 年度

**回應:**

```json
{
  "EntitlementID": "integer",
  "UserID": "string",
  "Year": "integer",
  "AnnualSpecialLeave": "decimal",
  "PersonalLeave": "decimal",
  "SickLeave": "decimal",
  "UpdateTime": "datetime"
}
```

**錯誤情況:**
- 404: 使用者不存在

## 請假申請管理

### 提交請假申請

提交新的請假申請。

**URL:** `/leave/requests`

**Method:** `POST`

**請求參數:**

```json
{
  "UserID": "string",
  "LeaveType": "string (annual_special/personal/sick)",
  "StartDate": "date",
  "EndDate": "date",
  "StartTime": "time (optional)",
  "EndTime": "time (optional)",
  "LeaveHours": "decimal",
  "Reason": "string (optional)"
}
```

**參數說明:**
- `UserID`: 員工ID
- `LeaveType`: 假別類型 (annual_special: 特別休假, personal: 事假, sick: 病假)
- `StartDate`: 請假開始日期
- `EndDate`: 請假結束日期
- `StartTime`: 請假開始時間 (選填)
- `EndTime`: 請假結束時間 (選填)
- `LeaveHours`: 請假時數
- `Reason`: 請假原因 (選填)

**回應:**

```json
{
  "RequestID": "integer",
  "UserID": "string",
  "EntitlementID": "integer",
  "LeaveType": "string",
  "StartDate": "date",
  "EndDate": "date",
  "StartTime": "time (optional)",
  "EndTime": "time (optional)",
  "LeaveHours": "decimal",
  "Reason": "string (optional)",
  "Status": "string",
  "ApproverID": "string (optional)",
  "ApprovedTime": "datetime (optional)",
  "CreateTime": "datetime"
}
```

**錯誤情況:**
- 400: 結束日期不能早於開始日期
- 400: 請假時數必須大於0
- 400: 假別餘額不足
- 404: 使用者不存在
- 404: 找不到該年度的假別配額

### 取得特定請假申請

根據請假申請ID取得特定請假申請資訊。

**URL:** `/leave/requests/{request_id}`

**Method:** `GET`

**URL 參數:**
- `request_id`: 請假申請ID

**回應:**

```json
{
  "RequestID": "integer",
  "UserID": "string",
  "EntitlementID": "integer",
  "LeaveType": "string",
  "StartDate": "date",
  "EndDate": "date",
  "StartTime": "time (optional)",
  "EndTime": "time (optional)",
  "LeaveHours": "decimal",
  "Reason": "string (optional)",
  "Status": "string",
  "ApproverID": "string (optional)",
  "ApprovedTime": "datetime (optional)",
  "CreateTime": "datetime"
}
```

**錯誤情況:**
- 404: 請假申請不存在

### 查詢請假申請

根據多種條件查詢請假申請。

**URL:** `/leave/requests`

**Method:** `GET`

**查詢參數:**
- `user_id`: 使用者ID (選填)
- `status`: 狀態 (選填)
- `start_date`: 開始日期 (選填)
- `end_date`: 結束日期 (選填)
- `leave_type`: 假別類型 (選填)
- `skip`: 跳過筆數 (預設: 0)
- `limit`: 回傳筆數上限 (預設: 100)

**回應:**

```json
[
  {
    "RequestID": "integer",
    "UserID": "string",
    "EntitlementID": "integer",
    "LeaveType": "string",
    "StartDate": "date",
    "EndDate": "date",
    "StartTime": "time (optional)",
    "EndTime": "time (optional)",
    "LeaveHours": "decimal",
    "Reason": "string (optional)",
    "Status": "string",
    "ApproverID": "string (optional)",
    "ApprovedTime": "datetime (optional)",
    "CreateTime": "datetime",
    "UserName": "string",
    "ApproverName": "string (optional)"
  }
]
```

### 審核請假申請

審核特定請假申請。

**URL:** `/leave/requests/{request_id}/approve`

**Method:** `PUT`

**URL 參數:**
- `request_id`: 請假申請ID

**請求參數:**

```json
{
  "Status": "string (approved/rejected)",
  "ApproverID": "string"
}
```

**回應:**

```json
{
  "RequestID": "integer",
  "UserID": "string",
  "EntitlementID": "integer",
  "LeaveType": "string",
  "StartDate": "date",
  "EndDate": "date",
  "StartTime": "time (optional)",
  "EndTime": "time (optional)",
  "LeaveHours": "decimal",
  "Reason": "string (optional)",
  "Status": "string",
  "ApproverID": "string",
  "ApprovedTime": "datetime",
  "CreateTime": "datetime"
}
```

**錯誤情況:**
- 400: 只能審核待審核的請假申請
- 404: 請假申請不存在
- 404: 審核人員不存在

### 查詢假別餘額

查詢特定使用者特定年度的假別餘額。

**URL:** `/leave/balance/{user_id}`

**Method:** `GET`

**URL 參數:**
- `user_id`: 使用者ID

**查詢參數:**
- `year`: 年度

**回應:**

```json
{
  "UserID": "string",
  "Year": "integer",
  "AnnualSpecialLeaveTotal": "decimal",
  "AnnualSpecialLeaveUsed": "decimal",
  "AnnualSpecialLeaveRemaining": "decimal",
  "PersonalLeaveTotal": "decimal",
  "PersonalLeaveUsed": "decimal",
  "PersonalLeaveRemaining": "decimal",
  "SickLeaveTotal": "decimal",
  "SickLeaveUsed": "decimal",
  "SickLeaveRemaining": "decimal"
}
```

**錯誤情況:**
- 404: 使用者不存在
- 404: 找不到該年度的假別配額
