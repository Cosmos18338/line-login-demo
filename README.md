# LINE Login Demo — FastAPI JWT Authentication

一個以 **FastAPI** 實作的第三方登入（LINE Login）與 JWT 驗證機制範例專案，展示從 OAuth2 授權流程、使用者資料寫入、JWT 簽發，到受保護路由驗證的完整後端實作。

## 專案背景

本專案抽離自個人開發中的分帳應用程式（AABro）,獨立整理出其中的 **Auth 模組**,聚焦展示第三方登入與權限驗證機制的完整實作，不包含分帳相關業務邏輯。

## 技術棧

| 類別 | 使用技術 |
|---|---|
| 後端框架 | FastAPI |
| 資料庫 | PostgreSQL 15 |
| ORM | SQLAlchemy 2.0 |
| 身份驗證 | LINE Login (OAuth2) + JWT (PyJWT) |
| 容器化 | Docker、Docker Compose |
| Session 管理 | Starlette SessionMiddleware（防 CSRF state 驗證用） |

## 功能特色

- **LINE OAuth2 登入流程**：實作 `state` 參數產生與驗證，防止 CSRF 攻擊。
- **使用者資料自動建立/查詢（upsert）**：首次登入自動建立使用者與第三方帳號綁定紀錄，重複登入則查詢既有帳號。
- **JWT 簽發與驗證**：登入成功後簽發帶有效期限的 JWT，並實作對應的過期、格式錯誤例外處理。
- **受保護路由範例（`/api/auth/me`）**：展示如何透過 FastAPI 的 Dependency Injection（`Depends`）保護需要登入才能存取的端點。

## 專案架構

```
app/
├── api/
│   ├── auth.py      # LINE 登入與 callback 路由
│   └── deps.py      # 驗證用 Dependency（get_current_user）
├── models/
│   └── db/
│       └── user.py  # User / UserOAuthBinding 資料表定義
├── services/
│   └── auth_service.py  # OAuth 交換、JWT 簽發解碼等核心邏輯
├── db.py
└── main.py
postgres/
└── init.sql          # 資料庫初始化建表腳本
```

**分層設計說明**：`api/` 負責處理 HTTP 請求與框架整合（路由、Dependency），`services/` 存放不依賴 FastAPI 框架、可獨立測試的純業務邏輯，兩者職責分離。

## 環境需求

- Docker / Docker Compose
- LINE Developers 帳號（申請 LINE Login Channel，取得 Channel ID / Secret）

## 啟動方式

1. 複製環境變數範本並填入實際值：

```bash
cp .env.example .env
```

編輯 `.env`，填入 `LINE_CHANNEL_ID`、`LINE_CHANNEL_SECRET`、`JWT_SECRET` 等變數。

2. 建置並啟動容器：

```bash
docker compose up --build
```

3. 開啟瀏覽器前往 `http://localhost:8000/docs` 查看互動式 API 文件。

## API 端點

| 方法 | 路徑 | 說明 | 是否需要驗證 |
|---|---|---|---|
| GET | `/api/health` | 服務健康檢查 | 否 |
| GET | `/api/db-check` | 資料庫連線檢查 | 否 |
| GET | `/api/auth/line` | 導向 LINE 授權頁 | 否 |
| GET | `/api/auth/line/redirect` | LINE 授權完成後的 callback，簽發 JWT | 否 |
| GET | `/api/auth/me` | 回傳目前登入使用者資料 | **是（Bearer Token）** |

## 測試方式

**方式一：Swagger UI**
1. 完成 LINE 登入流程，從導回網址取得 JWT。
2. 於 `/docs` 頁面點擊右上角「Authorize」，貼上 JWT。
3. 呼叫 `/api/auth/me`，確認回傳使用者資料。

**方式二：命令列**

```bash
curl -H "Authorization: Bearer <你的JWT>" http://localhost:8000/api/auth/me
```

**驗證涵蓋情境**：
- 帶有效 token → 回傳 `200` 與使用者資料
- 未帶 token → 回傳 `401`
- 帶無效/竄改 token → 回傳 `401`
- token 過期 → 回傳 `401` 並提示需重新登入

## 已知限制與未來改進方向

本專案為技術展示用途，以下為刻意簡化、但已知的技術債：

- **LINE id_token 未驗證簽章**：目前僅解碼 payload（`verify_signature=False`），正式環境應改用 LINE 公開的 JWKS 金鑰驗證簽章。
- **JWT 透過 URL query string 傳遞給前端**：目前 callback 完成後將 token 附加於導回網址，屬於demo 階段的簡化做法；正式產品建議改用 `httpOnly` + `secure` cookie 搭配 CSRF token，避免 token 暴露於瀏覽器歷史紀錄或伺服器日誌中。
- **JWT_SECRET 有預設值**：正式部署時務必於 `.env` 中覆寫為隨機生成的高強度密鑰。

## License

MIT
