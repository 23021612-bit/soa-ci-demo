"""Task API - a tiny REST service used to practice CI/CD with GitHub Actions."""
from flask import Flask, jsonify, request


def create_app() -> Flask:
    app = Flask(__name__)
    store: dict = {}
    counter = {"next": 1}

    def error(status: int, message: str):
        return jsonify({"error": {"code": status, "message": message}}), status

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.get("/api/v1/tasks")
    def list_tasks():
        items = list(store.values())
        done = request.args.get("done")
        if done is not None:
            if done.lower() not in ("true", "false"):
                return error(400, "done must be 'true' or 'false'")
            wanted = done.lower() == "true"
            items = [t for t in items if t["done"] == wanted]
        return jsonify({"items": items, "total": len(items)}), 200

    @app.post("/api/v1/tasks")
    def create_task():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error(400, "JSON body is required")
        title = data.get("title")
        done = data.get("done", False)
        if not isinstance(title, str) or not title.strip():
            return error(400, "title is required")
        if not isinstance(done, bool):
            return error(400, "done must be a boolean")

        task = {"id": counter["next"], "title": title.strip(), "done": done}
        store[task["id"]] = task
        counter["next"] += 1

        resp = jsonify(task)
        resp.status_code = 201
        resp.headers["Location"] = f"/api/v1/tasks/{task['id']}"
        return resp

    @app.get("/api/v1/tasks/<int:task_id>")
    def get_task(task_id: int):
        task = store.get(task_id)
        if task is None:
            return error(404, "task not found")
        return jsonify(task), 200

    @app.put("/api/v1/tasks/<int:task_id>")
    def update_task(task_id: int):
        task = store.get(task_id)
        if task is None:
            return error(404, "task not found")
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error(400, "JSON body is required")
        title = data.get("title")
        done = data.get("done")
        if not isinstance(title, str) or not title.strip():
            return error(400, "title is required")
        if not isinstance(done, bool):
            return error(400, "done must be a boolean")
        task["title"] = title.strip()
        task["done"] = done
        return jsonify(task), 200

    @app.delete("/api/v1/tasks/<int:task_id>")
    def delete_task(task_id: int):
        if task_id not in store:
            return error(404, "task not found")
        del store[task_id]
        return "", 204

    @app.errorhandler(404)
    def not_found(_):
        return error(404, "resource not found")

    @app.errorhandler(405)
    def method_not_allowed(_):
        return error(405, "method not allowed")

    return app


app = create_app()
