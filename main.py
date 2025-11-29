# -*- coding: utf-8 -*-
import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException, Cookie
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError # <-- เพิ่ม ValidationError
from typing import Optional, Dict, Any
from contextlib import contextmanager
import os
import json
from datetime import datetime, date, timedelta

# Import DB functions และ Logic Handlers
import database
import api_router
from psycopg2.extras import DictCursor

# --- START: PHASE 2 (Security) ---
import models
# --- END: PHASE 2 ---

class ApiRequest(BaseModel):
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class SessionData(BaseModel):
    username: str
    role: str
    department: str
    created_at: datetime
    token: str

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, timedelta):
            return str(obj)
        return super().default(obj)

app = FastAPI()

# --- START: PHASE 2 (Validation Map) ---
VALIDATION_MAP = {
    "login": models.LoginPayload,
    "list_users": models.ListPayload,
    "add_user": models.AddUserPayload,
    "update_user": models.UpdateUserPayload,
    "delete_user": models.SimpleUsernamePayload,
    
    "list_personnel": models.ListPayload,
    "get_personnel_details": models.SimpleIdPayload,
    "add_personnel": models.AddPersonnelPayload,
    "update_personnel": models.UpdatePersonnelPayload,
    "delete_personnel": models.SimpleIdPayload,
    "import_personnel": models.ImportPersonnelPayload,
    
    "submit_status_report": models.SubmitStatusReportPayload,
    "archive_reports": models.ArchiveReportPayload,
    "get_report_for_editing": models.SimpleIdPayload,

    "get_daily_personnel_for_submission": models.ListPayload,
    "submit_daily_report": models.SubmitDailyReportPayload,
    "archive_daily_reports": models.ArchiveDailyReportPayload,

    "add_holiday": models.HolidayPayload,
    "delete_holiday": models.SimpleDatePayload,
}
# --- END: PHASE 2 ---

@contextmanager
def get_db_cursor():
    conn = None
    cursor = None
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        yield conn, cursor
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def get_session(session_token: Optional[str] = Cookie(None)) -> Optional[SessionData]:
    if not session_token:
        return None
    
    with get_db_cursor() as (conn, cursor):
        expiry_limit = datetime.now() - timedelta(seconds=api_router.SESSION_TIMEOUT_SECONDS)
        cursor.execute("DELETE FROM sessions WHERE created_at < %s", (expiry_limit,))
        conn.commit()
        cursor.execute("SELECT u.username, u.role, u.department, s.created_at FROM sessions s JOIN users u ON s.username = u.username WHERE s.token = %s", (session_token,))
        session_data = cursor.fetchone()
        
        if session_data:
            session_dict = dict(session_data)
            session_dict['token'] = session_token
            return SessionData(**session_dict)
    return None

@app.post("/api")
async def handle_api_request(request_data: ApiRequest, request: Request, response: Response):
    
    action_name = request_data.action
    payload = request_data.payload
    action_config = api_router.ACTION_MAP.get(action_name)

    if not action_config:
        raise HTTPException(status_code=404, detail="ไม่รู้จักคำสั่งนี้")

    session = get_session(request.cookies.get("session_token"))
    
    if action_config.get("auth_required") and not session:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Unauthorized"})
        
    if action_config.get("admin_only") and (not session or session.role != "admin"):
        return JSONResponse(status_code=403, content={"status": "error", "message": "คุณไม่มีสิทธิ์ดำเนินการ"})

    # --- START: PHASE 2 (Validate Payload) ---
    validator_model = VALIDATION_MAP.get(action_name)
    if validator_model:
        try:
            validated_payload = validator_model(**payload)
            payload = validated_payload.dict(exclude_unset=True) 
        except ValidationError as e:
            print(f"Validation Error on action '{action_name}': {e.errors()}")
            return JSONResponse(
                status_code=422, 
                content={"status": "error", "message": "ข้อมูลที่ส่งมาไม่ถูกต้อง", "details": e.errors()}
            )
    # --- END: PHASE 2 ---

    try:
        with get_db_cursor() as (conn, cursor):
            handler_kwargs = {"payload": payload, "conn": conn, "cursor": cursor}
            
            if action_name == "login":
                handler_kwargs["client_address"] = (request.client.host, request.client.port)
            
            if session and action_name in [
                "logout", "list_personnel", "submit_status_report",
                "get_submission_history", "get_active_statuses",
                "get_personnel_details",
                "get_daily_personnel_for_submission", "submit_daily_report",
                "get_daily_dashboard_summary", "get_daily_submission_history",
                "get_daily_final_report", "archive_daily_reports",
                "get_archived_daily_reports", "archive_reports",
                "list_holidays", "add_holiday", "delete_holiday"
            ]:
                handler_kwargs["session"] = session.dict()

            response_data = action_config["handler"](**handler_kwargs)
            
            cookie_data = None
            if isinstance(response_data, tuple):
                response_data, cookie_data = response_data

            json_compatible_data = json.loads(json.dumps(response_data, cls=CustomJSONEncoder))
            
            if cookie_data:
                response.set_cookie(
                    key=cookie_data["key"],
                    value=cookie_data["value"],
                    httponly=cookie_data.get("httponly", True),
                    path=cookie_data.get("path", "/"),
                    samesite=cookie_data.get("samesite", "strict"),
                    max_age=cookie_data.get("max_age"),
                    expires=cookie_data.get("expires")
                )
            return json_compatible_data

    except Exception as e:
        print(f"API Error on action '{action_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Server error: {e}")

# --- Static File Serving (เสิร์ฟ HTML/JS/CSS) ---
PATH_MAP = {
    '/': 'login.html',
    '/main': 'main.html',
    '/daily': 'daily.html',
    '/selection': 'selection.html',
    '/app.js': 'app.js',
    '/api.js': 'api.js',
    '/login.js': 'login.js',
    '/style.css': 'style.css',
    '/ui.js': 'ui.js',
    '/utils.js': 'utils.js',
    '/handlers.js': 'handlers.js',
    '/app_daily.js': 'app_daily.js',
    '/daily.js': 'daily.js',
    '/admin.js': 'admin.js',
    '/admin.html': 'admin.html',
    '/main.html': 'main.html',
    '/main_daily.html': 'main_daily.html',
    '/login.html': 'login.html',
    '/selection.html': 'selection.html',
    '/weekly.html': 'weekly.html',
}

@app.get("/{path:path}")
async def serve_static_or_route(path: str):
    request_path = f"/{path}"
    
    file_name = PATH_MAP.get(request_path)
    
    if not file_name:
        if os.path.exists(path) and os.path.isfile(path):
            file_name = path
        else:
            if request_path == "/":
                return FileResponse("login.html")
            safe_path = os.path.join(".", path).replace("\\", "/")
            if os.path.commonprefix((os.path.abspath(safe_path), os.path.abspath("."))) != os.path.abspath("."):
                 return Response(status_code=404)
            if os.path.exists(safe_path) and os.path.isfile(safe_path):
                return FileResponse(safe_path)
            
            return Response(status_code=404)

    file_path = os.path.join(".", file_name)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
        
    return Response(status_code=404)

@app.on_event("startup")
def on_startup():
    try:
        database.init_db()
    except psycopg2.OperationalError as e:
        print(f"!!! ไม่สามารถเชื่อมต่อ PostgreSQL ได้: {e}")
        print("!!! กรุณาตรวจสอบว่า Docker Container 'ps_postgres_db' ทำงานอยู่หรือไม่")
        exit(1)

if __name__ == "__main__":
    print("--- 🚀 กำลังสตาร์ทเซิร์ฟเวอร์ FastAPI ด้วย Uvicorn ---")
    print(f"--- 🌐 เข้าใช้งานได้ที่: http://localhost:9999 ---")
    uvicorn.run("main:app", host="0.0.0.0", port=9999, reload=True)