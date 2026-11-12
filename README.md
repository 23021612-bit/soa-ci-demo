# soa-ci-demo

Project Flask nhỏ (REST API quản lý task, lưu trong bộ nhớ) để thực hành **CI/CD với GitHub Actions**.

## Cấu trúc

```
soa-ci-demo/
├── app/main.py                    # Flask app (app factory) + /health + CRUD /api/v1/tasks
├── tests/                         # pytest
├── openapi.yaml                   # hợp đồng API (OpenAPI 3.0.3)
├── .spectral.yaml                 # luật lint cho OpenAPI
├── Dockerfile                     # gunicorn, chạy user không phải root
├── requirements*.txt
└── .github/workflows/ci.yml       # pipeline CI
```

## Endpoint

| Method | URL | Mô tả |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/v1/tasks?done=true\|false` | Danh sách task (lọc tùy chọn) |
| POST | `/api/v1/tasks` | Tạo task (`201` + header `Location`) |
| GET | `/api/v1/tasks/{id}` | Xem 1 task |
| PUT | `/api/v1/tasks/{id}` | Thay thế `title` + `done` |
| DELETE | `/api/v1/tasks/{id}` | Xóa task (`204`) |

## Chạy local

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

flake8 app tests                 # lint
pytest --cov=app                 # test
flask --app app.main run --port 8000   # chạy thử API

docker build -t soa-ci-demo .
docker run --rm -p 8000:8000 soa-ci-demo
```

## Pipeline CI (`.github/workflows/ci.yml`)

Chạy khi push lên `main`, mở pull request, hoặc bấm tay (**Actions → CI → Run workflow**).

| Job | Việc làm |
|---|---|
| `lint` | flake8 |
| `test` | pytest + coverage, matrix Python 3.11 / 3.12, upload `junit.xml` + `coverage.xml` làm artifact |
| `api-lint` | Spectral lint `openapi.yaml` |
| `docker` | Build image, chạy container, smoke test bằng curl (chỉ chạy khi 3 job trên pass) |

## Đưa lên GitHub

```bash
git init -b main
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<user>/soa-ci-demo.git
git push -u origin main
```

Vào tab **Actions** để xem pipeline chạy.

## Gợi ý thí nghiệm

1. **Làm test fail:** sửa `{"status": "ok"}` thành `{"status": "down"}` trong `app/main.py`, push và xem job `test` + `docker` đỏ/bị bỏ qua.
2. **Làm lint fail:** thêm một import không dùng vào `app/main.py`, xem job `lint` fail.
3. **Làm OpenAPI fail:** xóa `operationId` hoặc để `$ref` trỏ sai, xem job `api-lint` fail.
4. **Pull request:** tạo nhánh mới, sửa code, mở PR để thấy pipeline chạy trên PR.
5. **Thêm bước của bạn:** thêm job/step mới vào `ci.yml` (ví dụ Newman, Locust, push image lên GHCR) để test script CI/CD riêng.
