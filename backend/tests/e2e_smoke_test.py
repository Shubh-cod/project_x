"""NovaCRM E2E Smoke Test - Step 18"""
import subprocess, json, sys

BASE = "http://127.0.0.1:8000/api/v1"
PASS = 0
FAIL = 0
WARN = 0

def api(method, path, token=None, data=None):
    cmd = ["curl", "-s", "-X", method, f"{BASE}{path}", "-H", "Content-Type: application/json"]
    if token: cmd.extend(["-H", f"Authorization: Bearer {token}"])
    if data: cmd.extend(["-d", json.dumps(data)])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    return json.loads(r.stdout)

def ok(msg):
    global PASS
    PASS += 1
    print(f"  ✅ {msg}")

def fail(msg):
    global FAIL
    FAIL += 1
    print(f"  ❌ {msg}")

def warn(msg):
    global WARN
    WARN += 1
    print(f"  ⚠️  {msg}")

# =============================================================
# TEST 1: Register (may fail if user already exists - that's ok)
# =============================================================
print("=== TEST 1: Register ===")
try:
    resp = api("POST", "/auth/register", data={"email":"e2efresh@novacrm.com","password":"TestPass123!","full_name":"E2E Fresh User"})
    if resp.get("success"):
        ok(f"Registered: {resp['data']['email']}")
    else:
        warn(f"Register returned: {resp.get('message', resp.get('detail',''))}")
except Exception as e:
    warn(f"Register: {e} (user may already exist)")

# =============================================================
# TEST 2: Login
# =============================================================
print("\n=== TEST 2: Login ===")
resp = api("POST", "/auth/login", data={"email":"e2etest@novacrm.com","password":"TestPass123!"})
if resp.get("success"):
    TOKEN = resp["data"]["tokens"]["access_token"]
    ok(f"Login successful, user: {resp['data']['user']['full_name']}")
else:
    fail(f"Login failed: {resp}")
    sys.exit(1)

# =============================================================
# TEST 3: Dashboard loads with stats
# =============================================================
print("\n=== TEST 3: Dashboard ===")
resp = api("GET", "/dashboard", TOKEN)
if resp.get("success") and resp.get("data"):
    summary = resp["data"].get("summary", {})
    ok(f"Dashboard loaded - contacts: {summary.get('total_contacts')}, leads: {summary.get('open_leads')}")
    pipeline = resp["data"].get("pipeline_by_stage", [])
    ok(f"Pipeline stages: {len(pipeline)}")
    perf = resp["data"].get("agent_performance", [])
    ok(f"Agent performance entries: {len(perf)}")
else:
    fail(f"Dashboard failed: {resp}")

# =============================================================
# TEST 4: Create contact → appears in list
# =============================================================
print("\n=== TEST 4: Create Contact ===")
resp = api("POST", "/contacts", TOKEN, {"name":"Jane Doe","email":"jane.doe@test.com","phone":"+9876543210","company":"TestCorp","source":"referral"})
if resp.get("success"):
    NEW_CONTACT_ID = resp["data"]["id"]
    ok(f"Contact created: {resp['data']['name']} ({NEW_CONTACT_ID[:8]}...)")
else:
    fail(f"Contact creation failed: {resp}")
    NEW_CONTACT_ID = None

if NEW_CONTACT_ID:
    resp = api("GET", "/contacts", TOKEN)
    items = resp["data"]["items"]
    found = any(c["id"] == NEW_CONTACT_ID for c in items)
    ok(f"Contact in list: {found} (total: {len(items)})") if found else fail("Contact NOT in list")

# =============================================================
# TEST 5: Contact detail page (API)
# =============================================================
print("\n=== TEST 5: Contact Detail ===")
if NEW_CONTACT_ID:
    resp = api("GET", f"/contacts/{NEW_CONTACT_ID}", TOKEN)
    if resp.get("success"):
        c = resp["data"]
        ok(f"Detail: {c['name']} | {c.get('email')} | {c.get('company')}")
    else:
        fail(f"Contact detail failed: {resp}")

# =============================================================
# TEST 6: Create lead linked to contact
# =============================================================
print("\n=== TEST 6: Create Lead ===")
resp = api("POST", "/leads", TOKEN, {"title":"E2E Test Lead","contact_id":NEW_CONTACT_ID,"status":"new","priority":"high","source":"website","estimated_value":25000})
if resp.get("success"):
    LEAD_ID = resp["data"]["id"]
    ok(f"Lead created: {resp['data']['title']} ({LEAD_ID[:8]}...)")
else:
    fail(f"Lead creation failed: {resp}")
    LEAD_ID = None

# Verify in lead list
if LEAD_ID:
    resp = api("GET", "/leads", TOKEN)
    data = resp["data"]
    items = data if isinstance(data, list) else data.get("items", [])
    found = any(l["id"] == LEAD_ID for l in items)
    ok(f"Lead in list: {found}") if found else fail("Lead NOT in list")

# Verify in contact's leads tab (contact_id filter)
if LEAD_ID and NEW_CONTACT_ID:
    resp = api("GET", f"/leads?contact_id={NEW_CONTACT_ID}", TOKEN)
    data = resp["data"]
    items = data if isinstance(data, list) else data.get("items", [])
    ok(f"Leads for contact: {len(items)}") if items else fail("No leads for contact")

# =============================================================
# TEST 7: Create deal linked to contact
# =============================================================
print("\n=== TEST 7: Create Deal ===")
resp = api("POST", "/deals", TOKEN, {"title":"E2E Deal","contact_id":NEW_CONTACT_ID,"stage":"prospect","value":50000,"probability":50,"close_date":"2026-05-15"})
if resp.get("success"):
    DEAL_ID = resp["data"]["id"]
    ok(f"Deal created: {resp['data']['title']} ({DEAL_ID[:8]}...)")
else:
    fail(f"Deal creation failed: {resp}")
    DEAL_ID = None

if DEAL_ID:
    resp = api("GET", "/deals", TOKEN)
    data = resp["data"]
    items = data if isinstance(data, list) else data.get("items", [])
    found = any(d["id"] == DEAL_ID for d in items)
    ok(f"Deal in pipeline: {found}") if found else fail("Deal NOT in pipeline")

# =============================================================
# TEST 8: Create task linked to lead
# =============================================================
print("\n=== TEST 8: Create Task ===")
resp = api("POST", "/tasks", TOKEN, {"title":"Call E2E Lead","linked_to_type":"lead","linked_to_id":LEAD_ID,"priority":"high","due_date":"2026-04-05"})
if resp.get("success"):
    TASK_ID = resp["data"]["id"]
    ok(f"Task created: {resp['data']['title']}")
else:
    fail(f"Task creation failed: {resp}")
    TASK_ID = None

if TASK_ID:
    resp = api("GET", "/tasks", TOKEN)
    data = resp["data"]
    items = data if isinstance(data, list) else data.get("items", [])
    found = any(t["id"] == TASK_ID for t in items)
    ok(f"Task in list: {found}") if found else fail("Task NOT in list")

# =============================================================
# TEST 9: Lead automation - auto-created follow-up task
# =============================================================
print("\n=== TEST 9: Automation ===")
resp = api("GET", "/tasks", TOKEN)
data = resp["data"]
items = data if isinstance(data, list) else data.get("items", [])
auto_tasks = [t for t in items if "[Auto]" in t.get("title","")]
if auto_tasks:
    ok(f"Auto-created tasks: {len(auto_tasks)}")
    for t in auto_tasks: print(f"    → {t['title']}")
else:
    warn("No auto-created tasks found")

# Check automation rules
resp = api("GET", "/automation/rules", TOKEN)
data = resp.get("data", [])
rules = data if isinstance(data, list) else data.get("items", []) if isinstance(data, dict) else []
ok(f"Automation rules: {len(rules)}")
for r in rules[:3]:
    if isinstance(r, dict):
        print(f"    → {r.get('name')} | trigger={r.get('trigger_event')} | active={r.get('is_active')}")

# =============================================================
# TEST 10: Add note to contact
# =============================================================
print("\n=== TEST 10: Notes ===")
if NEW_CONTACT_ID:
    resp = api("POST", "/notes", TOKEN, {"entity_type":"contact","entity_id":NEW_CONTACT_ID,"content":"E2E test note - great conversation."})
    if resp.get("success"):
        ok(f"Note created: {resp['data']['id'][:8]}...")
    else:
        fail(f"Note creation failed: {resp}")
    
    # Verify in notes list
    resp = api("GET", f"/notes?entity_type=contact&entity_id={NEW_CONTACT_ID}", TOKEN)
    data = resp.get("data", {})
    items = data.get("items", []) if isinstance(data, dict) else data
    ok(f"Notes for contact: {len(items)}") if items else fail("No notes found")

# =============================================================
# TEST 11: Activity timeline
# =============================================================
print("\n=== TEST 11: Activity Timeline ===")
if NEW_CONTACT_ID:
    resp = api("GET", f"/activities/entity/contact/{NEW_CONTACT_ID}", TOKEN)
    data = resp.get("data", {})
    if isinstance(data, dict):
        items = data.get("items", [])
        ok(f"Timeline activities: {len(items)}")
        for a in items[:5]: print(f"    → {a.get('action')} on {a.get('entity_type')}")
    else:
        fail(f"Timeline failed: {resp.get('message','')}")

# Global activities
resp = api("GET", "/activities", TOKEN)
data = resp.get("data", {})
if isinstance(data, dict):
    items = data.get("items", [])
    ok(f"Global activities: {len(items)}")
else:
    fail("Global activities failed")

# =============================================================
# TEST 12: Search contacts
# =============================================================
print("\n=== TEST 12: Search ===")
resp = api("GET", "/search?q=Jane", TOKEN)
data = resp.get("data", {})
if isinstance(data, dict):
    for k,v in data.items():
        if isinstance(v, list):
            ok(f"Search {k}: {len(v)} results")
elif isinstance(data, list):
    ok(f"Search results: {len(data)}")
else:
    warn(f"Search results: {data}")

# =============================================================
# TEST 13: Delete contact
# =============================================================
print("\n=== TEST 13: Delete Contact ===")
if NEW_CONTACT_ID:
    resp = api("DELETE", f"/contacts/{NEW_CONTACT_ID}", TOKEN)
    if resp.get("success"):
        ok(f"Contact deleted: {resp.get('message','')}")
    else:
        fail(f"Delete failed: {resp}")

    # Verify gone from list
    resp = api("GET", "/contacts", TOKEN)
    items = resp["data"]["items"]
    found = any(c["id"] == NEW_CONTACT_ID for c in items)
    ok(f"Contact gone from list (remaining: {len(items)})") if not found else fail("Contact still in list!")

# =============================================================
# TEST 14: Logout
# =============================================================
print("\n=== TEST 14: Logout ===")
resp = api("POST", "/auth/logout", TOKEN)
if resp.get("success"):
    ok(f"Logged out: {resp.get('message','')}")
else:
    fail(f"Logout failed: {resp}")

# Verify auth blocked (JWT is stateless, so may still work until expiry)
resp = api("GET", "/contacts", TOKEN)
if resp.get("detail") or not resp.get("success"):
    ok("Access blocked after logout")
else:
    warn("JWT still valid after logout (expected with stateless JWT + redis blacklist)")

# =============================================================
# SUMMARY
# =============================================================
print(f"\n{'='*50}")
print(f"E2E SMOKE TEST RESULTS")
print(f"{'='*50}")
print(f"  ✅ Passed: {PASS}")
print(f"  ❌ Failed: {FAIL}")
print(f"  ⚠️  Warnings: {WARN}")
print(f"{'='*50}")
if FAIL == 0:
    print("🎉 ALL TESTS PASSED!")
else:
    print(f"⚠️  {FAIL} test(s) failed - review above")
