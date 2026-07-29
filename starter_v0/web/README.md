# React Research Command Center

UI chính của lab dùng React + TypeScript; FastAPI phục vụ API, SSE tool trace và production assets trên cùng một URL. Streamlit đã được thay thế hoàn toàn.

## Yêu cầu

- Python virtual environment đã cài `starter_v0/requirements.txt`
- Node.js 24 LTS trở lên
- `.env` trong `starter_v0/` có API key của provider cần dùng

## Chạy development

`npm run dev` tự kiểm tra/sửa dependencies trong `.venv`, sau đó khởi động đồng thời FastAPI và Vite:

```bash
cd starter_v0/web/frontend
npm install
npm run dev
```

Mở `http://localhost:5173`. Muốn chỉ chạy Vite khi backend đã có sẵn, dùng `npm run dev:ui`.

## Chạy production / demo một URL

```bash
cd starter_v0/web/frontend
npm install
npm run build
cd ../..
./.venv/bin/python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000
```

Mở `http://localhost:8000`. Không commit `dist/`, `node_modules/`, `.env` hoặc browser test output.

## Kiểm thử

```bash
cd starter_v0
./.venv/bin/python -m pytest -q
cd web/frontend
npm test
npm run build
npm run test:e2e
```

E2E dùng Chromium của Playwright; cài browser lần đầu bằng `npx playwright install chromium`.

## API

- `GET /api/config`
- `POST /api/sessions`
- `GET /api/sessions`
- `GET /api/sessions/{id}`
- `POST /api/sessions/{id}/messages` (`text/event-stream`)
- `GET /api/health`

Transcript tiếp tục được lưu trong `starter_v0/transcripts/*.transcript.json` để giữ evidence tương thích với CLI/eval.
