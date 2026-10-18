import io
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from urllib.parse import urlencode
from wsgiref.util import setup_testing_defaults

from app import Application, db_connect, hash_password, handle_ussd, request_model, utcnow


class WSGIClient:
    def __init__(self, app):
        self.app = app
        self.cookies = {}
        self.csrf = ""

    def request(self, path, method="GET", payload=None, query=""):
        body = json.dumps(payload or {}).encode() if method in {"POST", "PUT", "DELETE"} else b""
        env = {}
        setup_testing_defaults(env)
        env.update({"REQUEST_METHOD":method,"PATH_INFO":path,"QUERY_STRING":query,"CONTENT_LENGTH":str(len(body)),"wsgi.input":io.BytesIO(body),"REMOTE_ADDR":"127.0.0.1"})
        if self.cookies:
            env["HTTP_COOKIE"] = "; ".join(f"{k}={v}" for k,v in self.cookies.items())
        if method in {"POST","PUT","DELETE"} and self.csrf:
            env["HTTP_X_CSRF_TOKEN"] = self.csrf
        output = {}
        def start_response(status, headers):
            output["status"] = int(status.split()[0])
            output["headers"] = headers
        raw = b"".join(self.app(env, start_response))
        for name, value in output.get("headers", []):
            if name.lower() == "set-cookie":
                pair = value.split(";",1)[0]
                key, _, val = pair.partition("=")
                if val:
                    self.cookies[key] = val
                else:
                    self.cookies.pop(key, None)
        try:
            data = json.loads(raw.decode())
        except Exception:
            data = raw
        if path == "/api/bootstrap" and isinstance(data, dict):
            self.csrf = data["csrf_token"]
        return output.get("status"), data

    def login(self, email, password):
        status, data = self.request("/api/bootstrap")
        assert status == 200
        return self.request("/api/admin/login", "POST", {"email":email,"password":password})


class SafeSpacesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "app.sqlite3"
        self.app = Application(self.db, bootstrap_admin=False)

    def tearDown(self):
        self.temp.cleanup()

    def add_admin(self, email, role, password="A-unique-test-password-123"):
        with db_connect(self.db) as conn:
            conn.execute("INSERT INTO admins(email,password_hash,role,created_at) VALUES(?,?,?,?)", (email,hash_password(password),role,utcnow()))
        return WSGIClient(self.app), password

    def test_idempotent_seed_and_quiz_volume(self):
        with db_connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM content_items WHERE category='lesson'").fetchone()[0], 90)
            self.assertEqual(conn.execute("SELECT count(*) FROM content_items WHERE category='faq'").fetchone()[0], 15)
            quiz_count = sum(len(json.loads(row[0])) for row in conn.execute("SELECT quiz_json FROM content_items WHERE category='lesson'"))
            self.assertEqual(quiz_count, 450)
        from app import init_db
        init_db(self.db, bootstrap_admin=False)
        with db_connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT count(*) FROM content_items WHERE category='lesson'").fetchone()[0], 90)

    def test_public_bootstrap_does_not_leak_draft_lesson_body_or_quiz(self):
        status, data = WSGIClient(self.app).request("/api/bootstrap")
        self.assertEqual(status, 200)
        self.assertEqual(data["content"], [])
        lesson = data["tracks"][0]["lessons"][0]
        self.assertIn("title", lesson)
        self.assertNotIn("body", lesson)
        self.assertNotIn("quiz", lesson)
        self.assertEqual(len(data["resource_candidates"]), 3)
        for lang in ("rw", "fr"):
            translated_status, translated = WSGIClient(self.app).request("/api/bootstrap", query=f"lang={lang}")
            self.assertEqual(translated_status, 200)
            self.assertEqual(len(translated["tracks"]), 6)
            self.assertIn("privacy", translated["pages"])

    def test_public_search_excludes_draft_text(self):
        status, data = WSGIClient(self.app).request("/api/search", query=urlencode({"lang":"en","q":"pressure"}))
        self.assertEqual(status, 200)
        self.assertFalse(any("coercion" in item["slug"] for item in data["results"]))

    def test_auth_and_team_api_enforces_ceo_president_only(self):
        editor, password = self.add_admin("editor@example.test", "content_editor")
        self.assertEqual(editor.login("editor@example.test", password)[0], 200)
        status, data = editor.request("/api/admin/team", "POST", {"full_name":"Test Editor","position":"Editor"})
        self.assertEqual(status, 403)
        president, password = self.add_admin("president@example.test", "President")
        self.assertEqual(president.login("president@example.test", password)[0], 200)
        status, data = president.request("/api/admin/team", "POST", {"full_name":"Approved Person","position":"President","biography":"Confirmed profile","display_order":1})
        self.assertEqual(status, 200)
        public_status, public = WSGIClient(self.app).request("/api/bootstrap")
        self.assertEqual(public_status, 200)
        self.assertEqual(public["team"][0]["full_name"], "Approved Person")

    def test_only_ceo_or_president_can_publish_and_review_is_required(self):
        ceo, password = self.add_admin("ceo@example.test", "CEO")
        self.assertEqual(ceo.login("ceo@example.test", password)[0], 200)
        with db_connect(self.db) as conn:
            item = conn.execute("SELECT * FROM content_items WHERE slug='body-awareness' AND language='en'").fetchone()
        body = {"id":item["id"],"title":item["title"],"summary":item["summary"],"body":item["body"],"status":"published"}
        status, err = ceo.request("/api/admin/content/save", "POST", body)
        self.assertEqual(status, 409)
        body["status"] = "approved"
        self.assertEqual(ceo.request("/api/admin/content/save", "POST", body)[0], 200)
        body["status"] = "published"
        self.assertEqual(ceo.request("/api/admin/content/save", "POST", body)[0], 200)
        public_status, public = WSGIClient(self.app).request("/api/bootstrap")
        self.assertEqual(public_status, 200)
        published = next(x for x in public["content"] if x["slug"]=="body-awareness")
        self.assertTrue(published["body"])
        self.assertEqual(published["review_status"], "approved")
        search_status, search_data = WSGIClient(self.app).request("/api/search", query="lang=en&q=body&category=lesson&age=ages-6-9")
        self.assertEqual(search_status,200)
        self.assertTrue(any(item["slug"]=="body-awareness" for item in search_data["results"]))

    def test_ai_emergency_response_and_unavailable_ai(self):
        client = WSGIClient(self.app)
        status, data = client.request("/api/ai", "POST", {"language":"en","message":"I am in immediate danger"})
        self.assertEqual(status, 200)
        self.assertTrue(data["urgent"])
        self.assertIn("112", data["answer"])
        status, data = client.request("/api/ai", "POST", {"language":"en","message":"Tell me about puberty"})
        self.assertEqual(status, 503)

    def test_feature_status_update_requires_admin_and_persists_status(self):
        editor, password = self.add_admin("tech@example.test", "technical_administrator")
        editor.login("tech@example.test", password)
        status, data = editor.request("/api/admin/features", "POST", {"key":"ai_assistant","status":"testing","description":"Configured in test","expected_period":""})
        self.assertEqual(status, 200)
        with db_connect(self.db) as conn:
            self.assertEqual(conn.execute("SELECT status FROM feature_status WHERE key='ai_assistant'").fetchone()[0], "testing")

    def test_help_support_and_contact_are_not_falsely_accepted(self):
        client = WSGIClient(self.app)
        self.assertEqual(client.request("/api/contact","POST",{"message":"Hello"})[0],503)
        self.assertEqual(client.request("/api/support","POST",{"message":"Please help"})[0],503)

    def test_ussd_menu_is_non_sensitive_and_language_aware(self):
        self.assertEqual(handle_ussd("s-123","","en")["status"],"CON")
        rw = handle_ussd("s-123","2","rw")
        self.assertEqual(rw["status"],"END")
        self.assertIn("112",rw["message"])
        self.assertIn("Ntutange amakuru bwite",rw["message"])
        self.assertEqual(handle_ussd("../../bad","1")["status"],"END")

    def test_csrf_required_for_admin_login(self):
        admin, password = self.add_admin("csrf@example.test", "CEO")
        status, data = admin.request("/api/admin/login","POST",{"email":"csrf@example.test","password":password})
        self.assertEqual(status,403)

    def test_health(self):
        status, data = WSGIClient(self.app).request("/api/health")
        self.assertEqual(status,200)
        self.assertEqual(data["database"],"connected")
        self.assertEqual(data["deployment_status"],"not_verified")

    def test_gemini_key_is_sent_in_header_not_url(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return json.dumps({"candidates":[{"content":{"parts":[{"text":"Grounded answer"}]}}]}).encode()
        observed = {}
        def fake_open(request, timeout):
            observed["url"] = request.full_url
            observed["key"] = request.get_header("X-goog-api-key")
            return Response()
        with patch("urllib.request.urlopen", side_effect=fake_open):
            result = request_model("gemini","gemini-test","private-key", "system", "question", [{"slug":"lesson-a","title":"Title","body":"Approved body"}], "en")
        self.assertEqual(result,"Grounded answer")
        self.assertEqual(observed["key"],"private-key")
        self.assertNotIn("private-key",observed["url"])


if __name__ == "__main__":
    unittest.main()
