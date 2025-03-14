# API Documentation

## Overview
| Module | Description | Base Endpoint |
|--------|-------------|---------------|
| Attendance | 出勤管理相關 API | `/attendance` |
| Case | 案件管理相關 API | `/cases` |
| Group | 群組管理相關 API | `/groups` |
| Material | 材料管理相關 API | `/materials` |
| Photo | 照片管理相關 API | `/photos` |
| User | 使用者管理相關 API | `/users` |
| Worklog | 工作日誌相關 API | `/worklogs` |

## Detailed API Documentation

### Attendance API (`/attendance`)

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|-----------|
| `/clock-in` | POST | 打卡上班 | `AttendanceClockIn`: {<br>- UserID: int<br>- CaseID: int<br>- IsTrained: bool<br>- ClockInPhoto: str } | `Attendance` object |
| `/{attendance_id}/clock-out` | POST | 打卡下班 | `AttendanceClockOut`: {<br>- ClockOutPhoto: str } | `Attendance` object |
| `/query` | GET | 查詢出勤記錄 | Query Parameters:<br>- start_date: date<br>- end_date: date<br>- user_id: int<br>- case_id: int | List of `Attendance` objects |
| `/incomplete` | GET | 取得未打卡下班的記錄 | - | List of `Attendance` objects |
| `/{attendance_id}` | GET | 取得特定出勤記錄 | - | `Attendance` object |

### Case API (`/cases`)

| Endpoint | Method | Description | Request Body/Parameters | Response |
|----------|--------|-------------|--------------|-----------|
| `/` | POST | 建立新案件 | `CaseCreate`: {<br>- Name: str<br>- GroupID: str<br>- Location: str<br>- Content: str } | `Case` object |
| `/` | GET | 取得案件列表 | Query Parameters:<br>- skip: int (default: 0)<br>- limit: int (default: 100)<br>- group_id: str (optional)<br>- status: CaseStatus (optional) | List of `Case` objects |
| `/{case_id}` | GET | 取得特定案件 | - | `Case` object |
| `/{case_id}` | PATCH | 更新案件資訊 | `CaseUpdate`: {<br>- Name: str (optional)<br>- Location: str (optional)<br>- Content: str (optional)<br>- Status: CaseStatus (optional) } | `Case` object |

### Group API (`/groups`)

| Endpoint | Method | Description | Request Body/Parameters | Response |
|----------|--------|-------------|--------------|-----------|
| `/` | POST | 建立新群組 | `GroupCreate`: {<br>- GroupID: str<br>- Name: str } | `Group` object |
| `/` | GET | 取得群組列表 | Query Parameters:<br>- skip: int (default: 0)<br>- limit: int (default: 100) | List of `Group` objects |
| `/{group_id}` | GET | 取得特定群組 | - | `Group` object |
| `/{group_id}` | PATCH | 更新群組資訊 | `GroupUpdate`: {<br>- Name: str (optional) } | `Group` object |

### Material API (`/materials`)

| Endpoint | Method | Description | Request Body/Parameters | Response |
|----------|--------|-------------|--------------|-----------|
| `/` | POST | 建立新材料 | `MaterialCreate`: {<br>- Name: str<br>- Unit: str<br>- UnitPrice: float<br>- Content: str<br>- StockQuantity: float<br>- SafetyStock: float } | `Material` object |
| `/` | GET | 取得材料列表 | Query Parameters:<br>- skip: int (default: 0)<br>- limit: int (default: 100)<br>- name: str (optional)<br>- unit: str (optional) | List of `Material` objects |
| `/{material_id}` | GET | 取得特定材料 | - | `Material` object |
| `/{material_id}` | PUT | 更新材料資訊 | `MaterialUpdate`: {<br>- Name: str (optional)<br>- Unit: str (optional)<br>- UnitPrice: float (optional)<br>- Content: str (optional)<br>- StockQuantity: float (optional)<br>- SafetyStock: float (optional) } | `Material` object |
| `/{material_id}` | DELETE | 刪除材料 | - | Success message |

#### Material Inventory API (`/materials/inventory`)

| Endpoint | Method | Description | Request Body/Parameters | Response |
|----------|--------|-------------|--------------|-----------|
| `/` | POST | 建立庫存異動記錄 | `MaterialInventoryLogCreate`: {<br>- MaterialID: int<br>- Quantity: float<br>- Status: str (IN/OUT)<br>- CaseID: int (optional)<br>- UserID: str (optional) } | `MaterialInventoryLog` object |
| `/{log_id}` | GET | 取得特定庫存異動記錄 | - | `MaterialInventoryLog` object |
| `/material/{material_id}` | GET | 取得特定材料的庫存異動記錄 | Query Parameters:<br>- skip: int (default: 0)<br>- limit: int (default: 100)<br>- start_date: datetime (optional)<br>- end_date: datetime (optional)<br>- status: str (optional) | List of `MaterialInventoryLog` objects |

### Photo API (`/photos`)

| Endpoint | Method | Description | Request Body/Parameters | Response |
|----------|--------|-------------|--------------|-----------|
| `/upload` | POST | 上傳照片 | Form Data:<br>- file: File (jpg, jpeg, png, gif)<br>- user_id: str<br>- group_id: str<br>- case_id: int (optional) | `Photo` object |
| `/` | POST | 建立照片記錄 | `PhotoCreate`: {<br>- UserID: str<br>- GroupID: str<br>- CaseID: int (optional)<br>- ImageHash: str<br>- Phase: str (optional) } | `Photo` object |
| `/{photo_id}/status` | PATCH | 更新照片狀態 | `PhotoUpdate`: {<br>- Status: str } | `Photo` object |
| `/{photo_id}` | GET | 取得特定照片 | - | `Photo` object |

### User API (`/users`)

| Endpoint | Method | Description | Request Body/Parameters | Response |
|----------|--------|-------------|--------------|-----------|
| `/` | GET | 取得使用者列表 | Query Parameters:<br>- skip: int (default: 0)<br>- limit: int (default: 100) | List of `User` objects |
| `/{user_id}` | GET | 取得特定使用者 | - | `User` object |
| `/` | POST | 建立新使用者 | `UserCreate`: {<br>- UserID: str<br>- UserName: str<br>- UserPic: str<br>- NickName: str } | `User` object |
| `/{user_id}/role` | PATCH | 更新使用者角色 | `UserRoleUpdate`: {<br>- Role: str } | `User` object |

### Worklog API (`/worklogs`)

| Endpoint | Method | Description | Request Body/Parameters | Response |
|----------|--------|-------------|--------------|-----------|
| `/` | POST | 建立工作日誌 | `WorkLogCreate`: {<br>- CaseID: int<br>- UserID: str<br>- Content: str } | `WorkLog` object |
| `/` | GET | 取得工作日誌列表 | Query Parameters:<br>- skip: int (default: 0)<br>- limit: int (default: 100) | List of `WorkLog` objects |
| `/{worklog_id}` | GET | 取得特定工作日誌 | - | `WorkLog` object |
| `/{worklog_id}` | PUT | 更新工作日誌 | `WorkLogUpdate`: {<br>- Content: str } | `WorkLog` object |
| `/{worklog_id}` | DELETE | 刪除工作日誌 | - | Success message |
