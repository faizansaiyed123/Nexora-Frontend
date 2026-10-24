"""Browser-level Nexora journey: real UI, FastAPI, PostgreSQL, Redis and email."""
from __future__ import annotations
import asyncio, json, re, time, uuid
from email import message_from_string
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import Page, sync_playwright
from sqlalchemy import select
from backend.core.security import get_password_hash
from backend.db.session import AsyncSessionLocal
from backend.models.client import UserModel
from backend.models.enums import RoleEnum
from backend.models.notification import NotificationOutboxModel
from backend.workers.tasks import dispatch_pending_notifications

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "docs/walkthrough/screenshots"
MAILBOX = Path("/tmp/nexora-mailbox.jsonl")
WEB, API = "http://127.0.0.1:4173", "http://127.0.0.1:8000"
RAW = "https://raw.githubusercontent.com/faizansaiyed123/Nexora-backend/main/tests/fixtures"
HIGH, LOW, DISCOVERY = (f"{RAW}/retail-price-{x}.html" for x in ("high","low")), None, None
HIGH_URL = f"{RAW}/retail-price-high.html"
LOW_URL = f"{RAW}/retail-price-low.html"
DISCOVERY_URL = f"{RAW}/retail-discovery-product.html"
ORG, NAME = f"Northstar Intelligence {uuid.uuid4().hex[:6]}", "Alex Morgan"
EMAIL = f"nexora-owner-{uuid.uuid4().hex[:10]}@example.com"
PASSWORD, CHANGED, RESET, ROLE_PASSWORD = "Nexora-Strong!2026", "Nexora-Updated!2026", "Nexora-Final!2026", "Nexora-Role!2026"
OFFERING = "Sony WH-1000XM5 Wireless Noise Canceling Headphones"
DISCOVERED = "Sony WF-1000XM5 Truly Wireless Noise Canceling Earbuds"
COMPETITOR, SOURCE = "Retail Product Reference", "Structured Retail Listing"
captured, js_errors = [], []

def snap(page: Page, name: str):
    SHOTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SHOTS/name), full_page=True, animations="disabled", caret="hide")
    captured.append(name); print(f"Screenshot: {name}", flush=True)

def choose(page: Page, label: str, option: str):
    field = page.locator("label.field").filter(has_text=label).last
    field.locator("button.select-trigger").click()
    page.get_by_role("option", name=option, exact=True).last.click()

def token(page: Page) -> str:
    value = page.evaluate("() => localStorage.getItem('nexora.access')")
    assert value, "No signed-in access token"
    return str(value)

def get(page: Page, path: str, expected=200):
    r=page.request.get(API+path,headers={"Authorization":f"Bearer {token(page)}"})
    assert r.status==expected, f"GET {path}: {r.status} {r.text()}"
    return r.json()

def wait_api(page: Page, fragment: str, method: str, action):
    with page.expect_response(lambda r: fragment in r.url and r.request.method==method) as event:
        action()
    return event.value

def mails():
    if not MAILBOX.exists(): return []
    out=[]
    for line in MAILBOX.read_text(encoding="utf-8").splitlines():
        try:
            row=json.loads(line)
            if row.get("data"): out.append(row)
        except json.JSONDecodeError: pass
    return out

def parse_mail(row):
    m=message_from_string(str(row["data"])); subject=str(m.get("Subject",""))
    if m.is_multipart():
        body="\n".join(p.get_payload(decode=True).decode(p.get_content_charset() or "utf-8","replace")
                       for p in m.walk() if p.get_content_type()=="text/plain" and p.get_payload(decode=True))
    else:
        payload=m.get_payload(decode=True); body=payload.decode(m.get_content_charset() or "utf-8","replace") if payload else str(m.get_payload())
    return subject,body,[str(x).lower() for x in row.get("rcpt_tos",[])]

def wait_mail(subject, recipient, start=0, timeout=40):
    until=time.monotonic()+timeout
    while time.monotonic()<until:
        for row in mails()[start:]:
            s,b,rcpt=parse_mail(row)
            if subject.lower() in s.lower() and recipient.lower() in rcpt: return b
        time.sleep(.2)
    raise AssertionError(f"Email {subject!r} not delivered; recent subjects={[parse_mail(x)[0] for x in mails()[start:]]}")

def link_from(body, route):
    m=re.search(rf"https?://[^\s<>]+/{re.escape(route)}\?token=[^\s<>]+",body)
    assert m, f"Missing {route} URL in delivered email"
    return m.group(0).rstrip(".,);")

def login(page,email,password):
    page.get_by_label("Work email").fill(email); page.get_by_label("Password").fill(password)
    r=wait_api(page,"/v1/auth/login","POST",lambda:page.get_by_role("button",name=re.compile("Sign in")).click())
    assert r.status==200,r.text()
    page.get_by_role("heading",name="Dashboard",exact=True).wait_for(timeout=15000)

def signout(page):
    page.locator("button.profile-trigger").click(); page.get_by_text("Sign out",exact=True).click()
    page.get_by_label("Work email").wait_for(timeout=12000)

async def make_user(client_id, role, suffix):
    email=f"{role.value.lower()}-{suffix}@example.com"
    async with AsyncSessionLocal() as db:
        existing=await db.scalar(select(UserModel).where(UserModel.email==email))
        if not existing:
            db.add(UserModel(client_id=client_id,email=email,full_name=f"Northstar {role.value.title()}",
                hashed_password=get_password_hash(ROLE_PASSWORD),role=role,is_active=True,email_verified=True))
            await db.commit()
    return email

async def outbox(client_id):
    async with AsyncSessionLocal() as db:
        result=await db.execute(select(NotificationOutboxModel.status).where(
            NotificationOutboxModel.client_id==client_id,NotificationOutboxModel.channel=="email"))
        return list(result.scalars().all())

def run():
    SHOTS.mkdir(parents=True,exist_ok=True); MAILBOX.unlink(missing_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch()
        context=browser.new_context(viewport={"width":1440,"height":1000},accept_downloads=True,device_scale_factor=1)
        page=context.new_page(); page.set_default_timeout(12000)
        page.on("pageerror",lambda err:js_errors.append(str(err)))
        page.on("dialog",lambda d:d.accept())

        # Account creation and email verification.
        page.goto(WEB+"/welcome",wait_until="networkidle")
        assert page.get_by_role("heading",name=re.compile("Understand the market")).is_visible()
        snap(page,"01-public-homepage.png")
        page.get_by_role("link",name=re.compile("Create workspace")).first.click()
        page.get_by_label("Organization name").fill(ORG); page.get_by_label("Your full name").fill(NAME)
        page.get_by_label("Work email").fill(EMAIL); page.get_by_label("Password").fill(PASSWORD)
        mail_start=len(mails())
        r=wait_api(page,"/v1/auth/register","POST",lambda:page.get_by_role("button",name=re.compile("Create workspace")).click())
        assert r.status==201 and r.json()["email_verification_required"] is True,r.text()
        page.get_by_role("heading",name="Verification required",exact=True).wait_for()
        snap(page,"02-account-created-verification-required.png")
        page.goto(link_from(wait_mail("Verify your Nexora account",EMAIL,mail_start),"verify-email"),wait_until="networkidle")
        snap(page,"03-email-verification.png")
        r=wait_api(page,"/v1/auth/verify-email","GET",lambda:page.get_by_role("button",name=re.compile("Verify email")).click())
        assert r.status==200,r.text(); page.get_by_role("link",name="Continue to sign in",exact=True).wait_for()
        snap(page,"04-email-verified.png"); page.get_by_role("link",name="Continue to sign in",exact=True).click()
        login(page,EMAIL,PASSWORD); snap(page,"05-first-workspace-dashboard.png")
        me=get(page,"/v1/auth/me"); assert me["role"]=="ORG_ADMIN"; client_id=uuid.UUID(me["client_id"])

        # Competitor creation, duplicate protection and update.
        page.get_by_role("link",name="Competitors",exact=True).click(); page.get_by_role("heading",name="Competitors",exact=True).wait_for()
        snap(page,"06-competitors.png"); page.get_by_role("button",name="Add competitor",exact=True).click()
        page.get_by_label("Name").fill(COMPETITOR); page.get_by_label("Domain").fill("raw.githubusercontent.com")
        r=wait_api(page,"/v1/competitors","POST",lambda:page.get_by_role("button",name="Save competitor",exact=True).click())
        assert r.status==201,r.text(); competitor_id=r.json()["id"]; page.get_by_text(COMPETITOR,exact=True).wait_for()
        snap(page,"07-competitor-created.png")
        page.get_by_role("button",name="Add competitor",exact=True).click()
        page.get_by_label("Name").fill("Duplicate Retail Reference"); page.get_by_label("Domain").fill("raw.githubusercontent.com")
        duplicate=wait_api(page,"/v1/competitors","POST",lambda:page.get_by_role("button",name="Save competitor",exact=True).click())
        assert duplicate.status==403,duplicate.text(); page.get_by_role("button",name="Cancel",exact=True).click()
        row=page.locator("tbody tr").filter(has_text=COMPETITOR).first; row.locator("button").first.click()
        page.get_by_label("Name").fill("Structured Product Reference")
        edited=wait_api(page,f"/v1/competitors/{competitor_id}","PATCH",lambda:page.get_by_role("button",name="Save competitor",exact=True).click())
        assert edited.status==200,edited.text(); competitor_name="Structured Product Reference"
        assert any(x["id"]==competitor_id and x["name"]==competitor_name for x in get(page,"/v1/competitors"))
        snap(page,"08-competitor-edited.png")

        # Source creation and persisted request/extraction settings.
        page.get_by_role("link",name="Sources",exact=True).click(); page.get_by_role("heading",name="Sources",exact=True).wait_for()
        page.get_by_role("button",name="Add source",exact=True).click()
        choose(page,"Competitor",competitor_name); page.get_by_label("Source name").fill(SOURCE)
        page.get_by_label("Base URL").fill(HIGH_URL); choose(page,"Source type","OFFICIAL_STORE"); choose(page,"Collection method","HTTP_FAST")
        snap(page,"09-source-creation-form.png")
        r=wait_api(page,"/v1/sources","POST",lambda:page.get_by_role("button",name="Create source",exact=True).click())
        assert r.status==201,r.text(); source_id=r.json()["id"]; page.get_by_text(SOURCE,exact=True).wait_for()
        page.get_by_title("Configuration",exact=True).click()
        page.get_by_label("Rate / minute").fill("60"); page.get_by_label("Delay seconds").fill("0.1")
        page.get_by_label("Timeout seconds").fill("25"); page.get_by_label("Max retries").fill("1")
        page.get_by_label("Custom headers (JSON)").fill('{"Accept-Language":"en-US,en;q=0.9"}')
        snap(page,"10-source-configuration-form.png")
        r=wait_api(page,f"/v1/sources/{source_id}/configuration","PATCH",lambda:page.get_by_role("button",name="Save configuration",exact=True).click())
        assert r.status==200,r.text()
        assert any(x["id"]==source_id and x["configuration"]["max_retries"]==1 for x in get(page,"/v1/sources"))
        page.get_by_title("Edit source",exact=True).click(); page.get_by_label("Source name").fill(SOURCE+" (Structured)")
        r=wait_api(page,f"/v1/sources/{source_id}","PATCH",lambda:page.get_by_role("button",name="Save changes",exact=True).click())
        assert r.status==200,r.text(); source_name=SOURCE+" (Structured)"; snap(page,"11-source-created-configured.png")

        # Catalog CRUD, attributes, dynamic definitions, bulk import/export/archive.
        page.get_by_role("link",name="Offerings",exact=True).click(); page.get_by_role("heading",name="Offerings",exact=True).wait_for()
        page.get_by_role("button",name="Add offering",exact=True).click()
        page.get_by_label("Name").fill(OFFERING); choose(page,"Offering type","PRODUCT")
        page.get_by_label("SKU").fill("WH1000XM5-BLK"); page.get_by_label("Current price").fill("449.99")
        page.get_by_label("Currency").fill("USD"); page.get_by_label("Market").fill("US")
        page.get_by_label("Category").fill("Electronics > Audio")
        page.get_by_label("Product URL").fill("https://www.sony.com/electronics/headband-headphones/wh-1000xm5")
        page.get_by_label("Description").fill("Wireless over-ear headphones with active noise cancellation and multipoint Bluetooth.")
        page.get_by_label("Dynamic attributes (JSON)").fill('{"brand":"Sony","color":"Black","battery_life_hours":30,"noise_cancellation":true}')
        snap(page,"12-offering-creation-form.png")
        r=wait_api(page,"/v1/offerings","POST",lambda:page.get_by_role("button",name="Create offering",exact=True).click())
        assert r.status==201,r.text(); offering_id=r.json()["id"]
        page.get_by_text(OFFERING,exact=True).wait_for()
        page.locator("tbody tr").filter(has_text=OFFERING).get_by_role("button",name=OFFERING,exact=True).click()
        page.get_by_text("CURRENT PRICE",exact=True).wait_for(); snap(page,"13-offering-details.png"); page.keyboard.press("Escape")
        row=page.locator("tbody tr").filter(has_text=OFFERING).first; row.get_by_title("Edit",exact=True).click()
        page.get_by_label("Current price").fill("429.99")
        r=wait_api(page,f"/v1/offerings/{offering_id}","PATCH",lambda:page.get_by_role("button",name="Save changes",exact=True).click())
        assert r.status==200,r.text(); assert float(get(page,f"/v1/offerings/{offering_id}")["current_price"])==429.99
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        wait_api(page,f"/v1/offerings/{offering_id}/toggle-monitoring","POST",lambda:row.get_by_title("Toggle monitoring",exact=True).click())
        assert get(page,f"/v1/offerings/{offering_id}")["is_monitored"] is False
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        wait_api(page,f"/v1/offerings/{offering_id}/toggle-monitoring","POST",lambda:row.get_by_title("Toggle monitoring",exact=True).click())
        assert get(page,f"/v1/offerings/{offering_id}")["is_monitored"] is True
        snap(page,"14-offering-edited-and-monitoring.png")
        page.get_by_role("button",name="Dynamic fields",exact=True).click(); page.get_by_text("Dynamic field definitions",exact=True).wait_for()
        snap(page,"15-dynamic-fields.png"); page.get_by_role("button",name="Add field",exact=True).click()
        page.get_by_label("Machine name").fill("review_cycle_months"); page.get_by_label("Display name").fill("Review Cycle")
        page.get_by_label("Data type").fill("NUMBER"); page.get_by_label("Unit").fill("months"); page.get_by_label("Category").fill("Commercial")
        r=wait_api(page,"/v1/offerings/fields","POST",lambda:page.get_by_role("button",name="Create field",exact=True).click())
        assert r.status==201,r.text(); field_id=r.json()["id"]; snap(page,"16-dynamic-field-created.png")
        page.keyboard.press("Escape"); page.keyboard.press("Escape")
        page.get_by_role("button",name="Bulk import",exact=True).click()
        imports=[
          {"name":"Sony ULT WEAR Wireless Headphones","offering_type":"PRODUCT","sku":"ULTWEAR-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/headband-headphones/ult-wear","category":"Electronics > Audio","attributes":{"brand":"Sony","color":"Black"}},
          {"name":"Sony LinkBuds S","offering_type":"PRODUCT","sku":"LINKBUDS-S-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/truly-wireless/linkbuds-s","category":"Electronics > Audio","attributes":{"brand":"Sony","fit":"In-ear"}}]
        page.get_by_label("Offering JSON").fill(json.dumps(imports)); snap(page,"17-bulk-import-form.png")
        r=wait_api(page,"/v1/offerings/bulk","POST",lambda:page.get_by_role("button",name="Import offerings",exact=True).click())
        assert r.status==200 and r.json()["successful_count"]==2,r.text(); page.get_by_text(imports[0]["name"],exact=True).wait_for()
        snap(page,"18-bulk-imported-catalog.png")
        for kind, path in [("CSV","/tmp/nexora-catalog.csv"),("JSON","/tmp/nexora-catalog.json")]:
            with page.expect_download(timeout=15000) as ev: page.get_by_role("button",name=kind,exact=True).click()
            ev.value.save_as(path); assert Path(path).stat().st_size>0
        page.get_by_placeholder("Search name, SKU, category…").fill("Sony ULT WEAR")
        page.get_by_text(imports[0]["name"],exact=True).wait_for()
        page.get_by_label("Select Sony ULT WEAR Wireless Headphones",exact=True).check()
        r=wait_api(page,"/v1/offerings/bulk-archive","POST",lambda:page.get_by_role("button",name="Archive 1",exact=True).click())
        assert r.status==200 and r.json()["archived_count"]==1,r.text()
        assert any(x["is_archived"] for x in get(page,"/v1/offerings?q=Sony%20ULT%20WEAR&include_archived=true&page=1&page_size=20")["items"])
        page.get_by_placeholder("Search name, SKU, category…").fill(""); page.get_by_text(OFFERING,exact=True).wait_for()
        snap(page,"19-catalog-import-export-and-archive.png")

        # Match creation and two real HTTP collections with a deterministic retail price movement.
        page.get_by_role("link",name="Matches",exact=True).click(); page.get_by_role("heading",name="Offering matches",exact=True).wait_for()
        page.get_by_role("button",name="Add match",exact=True).click(); choose(page,"Offering",OFFERING); choose(page,"Source",source_name)
        page.get_by_label("Competitor target URL").fill(HIGH_URL); choose(page,"Status","APPROVED"); page.get_by_label("Confidence (0–1)").fill("0.98")
        snap(page,"20-offering-match-form.png")
        r=wait_api(page,"/v1/offering-matches","POST",lambda:page.get_by_role("button",name="Create match",exact=True).click())
        assert r.status==201,r.text(); match_id=r.json()["id"]; row=page.locator("tbody tr").filter(has_text=OFFERING).first
        page.get_by_text(HIGH_URL,exact=False).wait_for(); snap(page,"21-offering-match-created.png")
        r=wait_api(page,"/v1/collections/run","POST",lambda:row.get_by_title("Run collection",exact=True).click())
        assert r.status in (200,201),r.text(); result=r.json()
        assert result["status"]=="COMPLETED" and result["observation"]["price"]=="399.99",result
        assert len(get(page,f"/v1/offerings/{offering_id}/history"))>=1
        snap(page,"22-first-price-observation.png")

        # Alert rules, price-change snapshot, persistent log, and real outbox delivery.
        page.get_by_role("link",name="Alerts",exact=True).click(); page.get_by_role("heading",name="Alerts",exact=True).wait_for()
        page.get_by_role("button",name="New rule",exact=True).click(); page.get_by_label("Rule name").fill("Sony retail price drop")
        choose(page,"Alert type","PERCENTAGE_DROP"); choose(page,"Offering scope",OFFERING)
        page.get_by_label("Threshold").fill("10"); page.get_by_label("Cooldown (minutes)").fill("60")
        snap(page,"23-alert-rule-form.png")
        r=wait_api(page,"/v1/alerts/rules","POST",lambda:page.get_by_role("button",name="Create rule",exact=True).click())
        assert r.status==201,r.text(); rule_id=r.json()["id"]; snap(page,"24-alert-rule-created.png")
        page.get_by_role("link",name="Matches",exact=True).click(); row=page.locator("tbody tr").filter(has_text=OFFERING).first
        row.get_by_title("Edit",exact=True).click(); page.get_by_label("Competitor target URL").fill(LOW_URL)
        r=wait_api(page,f"/v1/offering-matches/{match_id}","PATCH",lambda:page.get_by_role("button",name="Save changes",exact=True).click())
        assert r.status==200,r.text(); row=page.locator("tbody tr").filter(has_text=OFFERING).first
        r=wait_api(page,"/v1/collections/run","POST",lambda:row.get_by_title("Run collection",exact=True).click())
        assert r.status in (200,201),r.text(); result=r.json()
        assert result["observation"]["price"]=="349.99" and result["snapshot"]["previous_price"]=="399.99",result
        assert result["snapshot"]["percentage_difference"].startswith("-12.50%"),result
        page.get_by_role("link",name="Alerts",exact=True).click(); page.get_by_text("Competitor price dropped",exact=True).wait_for(timeout=15000)
        logs=get(page,"/v1/alerts/logs"); log=next((x for x in logs if x["title"]=="Competitor price dropped"),None)
        assert log and not log["is_read"],logs; page.get_by_title("Mark as read",exact=True).click(); page.get_by_title("Read",exact=True).wait_for()
        assert any(x["id"]==log["id"] and x["is_read"] for x in get(page,"/v1/alerts/logs"))
        snap(page,"25-alert-triggered-and-read.png")
        sent=dispatch_pending_notifications.run(); assert int(sent.get("sent",0))>=1,sent
        assert "Nexora detected a competitive intelligence event" in wait_mail("Nexora Competitive Alert: Competitor price dropped",EMAIL)
        assert "SENT" in asyncio.run(outbox(client_id))

        # Jobs history/detail and structured discovery with server-side SSRF rejection.
        page.get_by_role("link",name="Jobs",exact=True).click(); page.get_by_role("heading",name="Jobs",exact=True).wait_for()
        page.get_by_text("COLLECTION",exact=False).wait_for(); snap(page,"26-collection-job-history.png")
        page.get_by_role("button",name="Details",exact=True).first.click(); page.get_by_text("Job ID",exact=True).wait_for()
        snap(page,"27-collection-job-detail.png"); page.keyboard.press("Escape")
        page.get_by_role("link",name="Discovery",exact=True).click(); page.get_by_role("heading",name="Website discovery",exact=True).wait_for()
        page.get_by_label("Website URL").fill("http://127.0.0.1:8000/v1/health"); page.get_by_label("Max pages").fill("1")
        blocked=wait_api(page,"/v1/discovery/run","POST",lambda:page.get_by_role("button",name="Run discovery",exact=True).click())
        assert blocked.status==422,blocked.text(); snap(page,"28-private-target-blocked.png")
        page.get_by_label("Website URL").fill(DISCOVERY_URL); choose(page,"Default type","PRODUCT")
        r=wait_api(page,"/v1/discovery/run","POST",lambda:page.get_by_role("button",name="Run discovery",exact=True).click())
        assert r.status==200,r.text(); data=r.json()
        assert data["status"]=="COMPLETED" and data["created_offerings_count"]==1 and data["items"][0]["name"]==DISCOVERED,data
        snap(page,"29-discovered-catalog-item.png")
        assert get(page,f"/v1/discovery/jobs/{data['job_id']}")["items"][0]["sku"]=="WF1000XM5-BLK"
        r=wait_api(page,"/v1/discovery/run","POST",lambda:page.get_by_role("button",name="Run discovery",exact=True).click())
        assert r.status==200 and r.json()["created_offerings_count"]==0 and r.json()["updated_offerings_count"]==1,r.text()
        assert sum(x["sku"]=="WF1000XM5-BLK" for x in get(page,"/v1/offerings?q=Sony%20WF-1000XM5&page=1&page_size=20")["items"])==1
        snap(page,"30-discovery-history-and-upsert.png")

        # Workspace profile, password change, one-time reset email and login.
        page.locator("button.profile-trigger").click(); page.get_by_text("Account settings",exact=True).click()
        page.get_by_role("heading",name="Settings",exact=True).wait_for()
        page.get_by_label("Company name").fill("Northstar Analytics"); page.get_by_label("Country").fill("US")
        page.get_by_label("Default currency").fill("USD"); page.get_by_label("Market").fill("US")
        page.get_by_label("Industry").fill("Consumer Electronics"); page.get_by_label("Timezone").fill("America/New_York")
        r=wait_api(page,"/v1/auth/profile","PATCH",lambda:page.get_by_role("button",name="Save profile",exact=True).click())
        assert r.status==200 and get(page,"/v1/auth/profile")["company_name"]=="Northstar Analytics",r.text()
        snap(page,"31-workspace-profile.png")
        page.get_by_label("Current password").fill(PASSWORD); page.get_by_label("New password").fill(CHANGED)
        r=wait_api(page,"/v1/auth/change-password","POST",lambda:page.get_by_role("button",name="Update password",exact=True).click())
        assert r.status==200,r.text()
        assert page.request.post(API+"/v1/auth/login",data=json.dumps({"email":EMAIL,"password":PASSWORD}),headers={"Content-Type":"application/json"}).status==401
        assert page.request.post(API+"/v1/auth/login",data=json.dumps({"email":EMAIL,"password":CHANGED}),headers={"Content-Type":"application/json"}).status==200
        snap(page,"32-password-changed.png")

        signout(page); page.get_by_role("link",name="Forgot password?",exact=True).click()
        page.get_by_label("Work email").fill(EMAIL); reset_start=len(mails())
        r=wait_api(page,"/v1/auth/forgot-password","POST",lambda:page.get_by_role("button",name="Send reset link",exact=True).click())
        assert r.status==200,r.text(); page.get_by_role("heading",name="Check your inbox",exact=True).wait_for()
        snap(page,"33-password-reset-requested.png")
        page.goto(link_from(wait_mail("Reset your Nexora password",EMAIL,reset_start),"reset-password"),wait_until="networkidle")
        page.get_by_label("New password").fill(RESET); snap(page,"34-password-reset-form.png")
        r=wait_api(page,"/v1/auth/reset-password","POST",lambda:page.get_by_role("button",name="Update password",exact=True).click())
        assert r.status==200,r.text(); page.get_by_role("heading",name="Password updated",exact=True).wait_for()
        snap(page,"35-password-reset-complete.png"); page.get_by_role("link",name="Continue to sign in",exact=True).click()
        login(page,EMAIL,RESET); snap(page,"36-dashboard-after-recovery.png")

        # Persisted role users: Analyst can work with intelligence; Viewer is read-only.
        suffix=uuid.uuid4().hex[:8]
        viewer=asyncio.run(make_user(client_id,RoleEnum.VIEWER,suffix))
        analyst=asyncio.run(make_user(client_id,RoleEnum.ANALYST,suffix))
        signout(page); login(page,analyst,ROLE_PASSWORD); page.get_by_role("link",name="Competitors",exact=True).click()
        assert page.get_by_role("button",name="Add competitor",exact=True).count()==0
        denied=page.request.post(API+"/v1/competitors",data=json.dumps({"name":"Unauthorized Analyst","domain":"analyst-forbidden.example"}),
            headers={"Content-Type":"application/json","Authorization":f"Bearer {token(page)}"})
        assert denied.status==403,denied.text(); page.get_by_role("link",name="Discovery",exact=True).click()
        assert page.get_by_role("button",name="Run discovery",exact=True).is_visible(); snap(page,"37-analyst-workspace.png")
        signout(page); login(page,viewer,ROLE_PASSWORD); page.get_by_role("link",name="Offerings",exact=True).click()
        assert page.get_by_role("button",name="Add offering",exact=True).count()==0
        assert page.get_by_role("button",name="Bulk import",exact=True).count()==0
        denied=page.request.post(API+"/v1/competitors",data=json.dumps({"name":"Unauthorized Viewer","domain":"viewer-forbidden.example"}),
            headers={"Content-Type":"application/json","Authorization":f"Bearer {token(page)}"})
        assert denied.status==403,denied.text()
        assert page.request.get(API+"/v1/offerings",headers={"Authorization":f"Bearer {token(page)}"}).status==200
        snap(page,"38-viewer-read-only-workspace.png")

        mobile=context.new_page(); mobile.set_viewport_size({"width":390,"height":844})
        mobile.on("pageerror",lambda err:js_errors.append(str(err))); mobile.goto(WEB+"/welcome",wait_until="networkidle")
        dims=mobile.evaluate("() => ({viewport:document.documentElement.clientWidth,page:document.documentElement.scrollWidth})")
        assert dims["page"]<=dims["viewport"],dims; snap(mobile,"39-mobile-homepage.png")
        assert not js_errors,"Browser JavaScript errors: "+" | ".join(js_errors)
        manifest={"product":"Nexora","captured_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
          "viewport":{"width":1440,"height":1000},"screenshot_count":len(captured),"screenshots":captured}
        (SHOTS.parent/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
        print(f"Connected browser journey complete: {len(captured)} screenshots.",flush=True)
        context.close(); browser.close()

if __name__=="__main__": run()
