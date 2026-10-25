"""Nexora browser walkthrough: visible UI -> real FastAPI -> PostgreSQL."""
from __future__ import annotations
import asyncio, json, os, re, time, uuid
from email import message_from_string
from pathlib import Path
from playwright.sync_api import sync_playwright
from sqlalchemy import select
from backend.core.security import get_password_hash
from backend.db.session import AsyncSessionLocal
from backend.models.client import UserModel
from backend.models.enums import RoleEnum
from backend.models.notification import NotificationOutboxModel
from backend.workers.tasks import dispatch_pending_notifications

BASE = os.getenv("NEXORA_FRONTEND_URL", "http://127.0.0.1:4173").rstrip("/")
API = os.getenv("NEXORA_API_URL", "http://127.0.0.1:8000").rstrip("/")
MAILBOX = Path(os.getenv("NEXORA_MAILBOX", "/tmp/nexora-mailbox.jsonl"))
SHOTS = Path("docs/walkthrough/screenshots")
EMAIL = "market-analyst@northstar.example.com"
PWD = "Nexora-Strong!2026"
CHANGED = "Nexora-Updated!2026"
RESET = "Nexora-Final!2026"
ROLE_PWD = "Nexora-Role!2026"
ORG = "Northstar Market Intelligence"
NAME = "Alex Morgan"
OFFERING = "Sony WH-1000XM5 Wireless Headphones"
DISCOVERED = "Sony WF-1000XM5 Truly Wireless Noise Canceling Earbuds"
HIGH = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-price-high.html"
LOW = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-price-low.html"
DISCOVERY = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-discovery-product.html"
JS_ERRORS: list[str] = []
SCREENS = [
("00-public-homepage.png","Public homepage","The public product entry point."),
("01-registration-form.png","Workspace registration","Organization, user and password fields."),
("02-verification-email-sent.png","Verification requested","The account awaits email confirmation."),
("03-email-verification-page.png","Verify email","The delivered one-time verification link."),
("04-email-verified.png","Email verified","Successful activation before sign-in."),
("05-login.png","Sign in","Workspace sign-in."),
("06-dashboard-empty-workspace.png","New workspace dashboard","Dashboard from the authenticated API."),
("07-competitors-empty.png","Competitor directory","An unconfigured market network."),
("08-competitor-created.png","Competitor saved","A persisted competitor row."),
("09-duplicate-domain-rejected.png","Duplicate domain guard","The server rejects a duplicate competitor domain."),
("10-source-creation-form.png","Add collection source","Connect a competitor to a page."),
("11-sources-created.png","Source connected","Saved collection source and health information."),
("12-source-configuration.png","Source configuration","Rate, delay, timeout, retries, headers and selectors."),
("13-source-configuration-saved.png","Configured source","Configuration read back after saving."),
("14-offering-creation-form.png","Add catalog offering","Product data and attributes."),
("15-catalog-offering-created.png","Catalog record","The offering appears in the catalog."),
("16-offering-detail-and-history.png","Offering detail","Details, match metrics and price-history surface."),
("17-catalog-monitoring-active.png","Monitoring enabled","Monitoring is paused and resumed."),
("18-dynamic-fields.png","Dynamic field definitions","Tenant-specific catalog schema."),
("19-dynamic-field-form.png","Create dynamic field","Field key, type, unit and category."),
("20-dynamic-field-created.png","Dynamic field saved","Saved definition."),
("21-bulk-import-form.png","Bulk catalog import","Structured JSON multi-item import."),
("22-bulk-imported-catalog.png","Imported catalog","Imported offerings available to search."),
("23-catalog-import-export-and-archive.png","Export and archive","CSV/JSON downloads and soft archive."),
("24-offering-match-form.png","Map an offering","Link an offering to a competitor URL."),
("25-offering-match-created.png","Offering match","The persisted mapping and confidence."),
("26-first-price-observation.png","First price observation","HTTP collection creates an observation and snapshot."),
("27-alert-rule-form.png","Configure an alert","Price-drop threshold and cooldown."),
("28-alert-rule-created.png","Alert rule saved","Rule bound to a catalog offering."),
("29-alert-generated-and-read.png","Alert event lifecycle","A lower observed price generates an alert."),
("30-collection-job-history.png","Collection jobs","Persisted execution history."),
("31-collection-job-detail.png","Collection job details","Job ID and collection metadata."),
("32-private-target-blocked.png","Private target protection","Loopback discovery is rejected."),
("33-discovery-product-created.png","Website discovery","Structured evidence becomes a saved offering."),
("34-discovery-upsert-history.png","Discovery update","A repeat scan updates instead of duplicating."),
("35-workspace-settings.png","Workspace settings","Organization and account controls."),
("36-workspace-profile-updated.png","Updated profile","Changes verified through a fresh read."),
("37-password-changed.png","Password changed","The previous credential no longer works."),
("38-password-reset-requested.png","Recovery requested","A one-time reset email is sent."),
("39-password-reset-form.png","Reset password","One-time reset link opens the form."),
("40-password-reset-complete.png","Password reset complete","The credential is changed."),
("41-dashboard-after-password-reset.png","Sign in after recovery","The new password reaches the dashboard."),
("42-analyst-workspace.png","Analyst role","Read access with restricted admin controls."),
("43-viewer-read-only-workspace.png","Viewer role","Read-only UI and backend-enforced writes."),
("44-mobile-homepage.png","Mobile homepage","Responsive public entry point."),
("45-alert-rule-lifecycle.png","Alert-rule administration","Pause, reactivate and remove an alert rule."),
("46-match-removed.png","Match removed","Remove a market mapping through the UI."),
("47-source-removed.png","Source removed","Delete the collection source."),
("48-competitor-removed.png","Competitor removed","Remove the competitor and dependent data."),
("49-offering-archived.png","Offering archived","Retain an archived catalogue record."),
]
def shot(page, filename):
    SHOTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SHOTS / filename), full_page=True, animations="disabled", caret="hide")
    print("Captured " + filename, flush=True)
def choose(page, label, option):
    field = page.locator("label.field").filter(has_text=label).last
    field.locator("button.select-trigger").click()
    page.get_by_role("option", name=option, exact=True).last.click()
def access_token(page):
    value = page.evaluate("() => localStorage.getItem('nexora.access')")
    assert value, "Expected authenticated browser token"
    return str(value)
def get_api(page, path):
    r = page.request.get(API + path, headers={"Authorization": "Bearer " + access_token(page)})
    assert r.status == 200, "GET " + path + ": " + r.text()
    return r.json()
def inbox():
    if not MAILBOX.exists(): return []
    rows=[]
    for line in MAILBOX.read_text(encoding="utf-8").splitlines():
        try:
            item=json.loads(line)
            if item.get("data"): rows.append(item)
        except json.JSONDecodeError: pass
    return rows
def mail_parts(item):
    msg=message_from_string(str(item["data"]))
    subject=str(msg.get("Subject",""))
    if msg.is_multipart():
        chunks=[]
        for part in msg.walk():
            if part.get_content_type()=="text/plain":
                raw=part.get_payload(decode=True)
                if raw: chunks.append(raw.decode(part.get_content_charset() or "utf-8","replace"))
        body="\n".join(chunks)
    else:
        raw=msg.get_payload(decode=True)
        body=raw.decode(msg.get_content_charset() or "utf-8","replace") if raw else str(msg.get_payload())
    return subject,body,[str(x).lower() for x in item.get("rcpt_tos",[])]
def wait_mail(subject, recipient, start, timeout=40):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        for item in inbox()[start:]:
            sub,body,recipients=mail_parts(item)
            if subject.lower() in sub.lower() and recipient.lower() in recipients: return item,body
        time.sleep(.25)
    raise AssertionError("No email " + subject + " for " + recipient)
def link_from(body, route):
    found=re.search(rf"https?://[^\s<>]+/{re.escape(route)}\?token=[^\s<>]+",body)
    assert found, "One-time " + route + " link was not present in email"
    return found.group(0).rstrip(".,);")
def sign_in(page,email,password):
    page.get_by_label("Work email").fill(email)
    page.get_by_label("Password").fill(password)
    with page.expect_response(lambda r:"/v1/auth/login" in r.url and r.request.method=="POST") as event:
        page.get_by_role("button",name=re.compile("Sign in")).click()
    assert event.value.status==200,event.value.text()
    page.get_by_role("heading",name="Dashboard",exact=True).wait_for(timeout=15000)
def sign_out(page):
    page.locator("button.profile-trigger").click()
    page.get_by_role("menuitem",name="Sign out",exact=True).click()
    page.get_by_label("Work email").wait_for(timeout=10000)
async def add_role_user(client_id, role, suffix):
    email=f"{role.value.lower()}-{suffix}@northstar.example.com"
    async with AsyncSessionLocal() as db:
        existing=await db.scalar(select(UserModel).where(UserModel.email==email))
        if not existing:
            db.add(UserModel(client_id=client_id,email=email,full_name="Northstar "+role.value.title(),
                hashed_password=get_password_hash(ROLE_PWD),role=role,is_active=True,email_verified=True))
            await db.commit()
    return email
async def mail_statuses(client_id):
    async with AsyncSessionLocal() as db:
        rows=await db.execute(select(NotificationOutboxModel.status).where(
            NotificationOutboxModel.client_id==client_id,NotificationOutboxModel.channel=="email"))
        return list(rows.scalars().all())

def main():
    if MAILBOX.exists(): MAILBOX.unlink()
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        ctx=browser.new_context(viewport={"width":1440,"height":1000},accept_downloads=True)
        page=ctx.new_page()
        page.set_default_timeout(12000)
        page.on("pageerror",lambda exc:JS_ERRORS.append(str(exc)))
        page.on("dialog",lambda dialog:dialog.accept())
        page.goto(BASE+"/welcome",wait_until="networkidle")
        page.get_by_role("heading",name=re.compile("Understand the market")).wait_for()
        shot(page,"00-public-homepage.png")
        page.get_by_role("link",name=re.compile("Create workspace")).click()
        page.get_by_label("Organization name").wait_for()
        shot(page,"01-registration-form.png")
        page.get_by_label("Organization name").fill(ORG)
        page.get_by_label("Your full name").fill(NAME)
        page.get_by_label("Work email").fill(EMAIL)
        page.get_by_label("Password").fill(PWD)
        before=len(inbox())
        with page.expect_response(lambda r:"/v1/auth/register" in r.url and r.request.method=="POST") as event:
            page.get_by_role("button",name=re.compile("Create workspace")).click()
        assert event.value.status==201,event.value.text()
        assert event.value.json()["email_verification_required"] is True
        page.get_by_role("heading",name="Verification required").wait_for()
        shot(page,"02-verification-email-sent.png")
        _,body=wait_mail("Verify your Nexora account",EMAIL,before)
        page.goto(link_from(body,"verify-email"),wait_until="networkidle")
        shot(page,"03-email-verification-page.png")
        with page.expect_response(lambda r:"/v1/auth/verify-email" in r.url and r.request.method=="GET") as event:
            page.get_by_role("button",name=re.compile("Verify email")).click()
        assert event.value.status==200,event.value.text()
        page.get_by_role("link",name="Continue to sign in",exact=True).wait_for()
        shot(page,"04-email-verified.png")
        page.get_by_role("link",name="Continue to sign in",exact=True).click()
        page.get_by_label("Work email").wait_for()
        shot(page,"05-login.png")
        sign_in(page,EMAIL,PWD)
        shot(page,"06-dashboard-empty-workspace.png")
        me=page.request.get(API+"/v1/auth/me",headers={"Authorization":"Bearer "+access_token(page)})
        assert me.status==200,me.text()
        assert me.json()["role"]=="ORG_ADMIN"
        client_id=uuid.UUID(me.json()["client_id"])

        # Competitors: creation, duplicate prevention, update and later deletion.
        page.get_by_role("link",name="Competitors",exact=True).click()
        page.get_by_role("heading",name="Competitors",exact=True).wait_for()
        shot(page,"07-competitors-empty.png")
        page.get_by_role("button",name="Add competitor",exact=True).click()
        page.get_by_label("Name").fill("Retail Product Reference")
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        with page.expect_response(lambda r:r.url.endswith("/v1/competitors") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Save competitor",exact=True).click()
        assert event.value.status==201,event.value.text()
        competitor_id=event.value.json()["id"]
        page.get_by_text("Retail Product Reference",exact=True).wait_for()
        shot(page,"08-competitor-created.png")
        page.get_by_role("button",name="Add competitor",exact=True).click()
        page.get_by_label("Name").fill("Duplicate Product Reference")
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        with page.expect_response(lambda r:r.url.endswith("/v1/competitors") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Save competitor",exact=True).click()
        assert event.value.status==403,event.value.text()
        page.get_by_text("already exists",exact=False).wait_for()
        shot(page,"09-duplicate-domain-rejected.png")
        page.get_by_role("button",name="Cancel",exact=True).click()
        row=page.locator("tbody tr").filter(has_text="Retail Product Reference").first
        row.locator("button").first.click()
        page.get_by_label("Name").fill("Retail Product Reference")
        with page.expect_response(lambda r:r.url.endswith(f"/v1/competitors/{competitor_id}") and r.request.method=="PATCH") as event:
            page.get_by_role("button",name="Save competitor",exact=True).click()
        assert event.value.status==200,event.value.text()
        assert any(x["id"]==competitor_id for x in get_api(page,"/v1/competitors"))

        # Source configuration is persisted and read back through the API.
        page.get_by_role("link",name="Sources",exact=True).click()
        page.get_by_role("button",name="Add source",exact=True).click()
        choose(page,"Competitor","Retail Product Reference")
        page.get_by_label("Source name").fill("Retail Product Listing")
        page.get_by_label("Base URL").fill(HIGH)
        choose(page,"Source type","OFFICIAL_STORE")
        choose(page,"Collection method","HTTP_FAST")
        shot(page,"10-source-creation-form.png")
        with page.expect_response(lambda r:r.url.endswith("/v1/sources") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Create source",exact=True).click()
        assert event.value.status==201,event.value.text()
        source_id=event.value.json()["id"]
        source_name="Retail Product Listing"
        shot(page,"11-sources-created.png")
        page.get_by_title("Configuration",exact=True).click()
        page.get_by_label("Rate / minute").fill("60")
        page.get_by_label("Delay seconds").fill("0.1")
        page.get_by_label("Timeout seconds").fill("25")
        page.get_by_label("Max retries").fill("1")
        page.get_by_label("Custom headers (JSON)").fill('{"Accept-Language":"en-US,en;q=0.9"}')
        page.get_by_label("Extraction selectors (JSON)").fill("{}")
        shot(page,"12-source-configuration.png")
        with page.expect_response(lambda r:r.url.endswith(f"/v1/sources/{source_id}/configuration") and r.request.method=="PATCH") as event:
            page.get_by_role("button",name="Save configuration",exact=True).click()
        assert event.value.status==200,event.value.text()
        cfg=next(x for x in get_api(page,"/v1/sources") if x["id"]==source_id)["configuration"]
        assert cfg["rate_limit_rpm"]==60 and cfg["max_retries"]==1,cfg
        page.get_by_title("Edit source",exact=True).click()
        page.get_by_label("Source name").fill(source_name+" (Structured)")
        with page.expect_response(lambda r:r.url.endswith(f"/v1/sources/{source_id}") and r.request.method=="PATCH") as event:
            page.get_by_role("button",name="Save changes",exact=True).click()
        assert event.value.status==200,event.value.text()
        source_name+=" (Structured)"
        shot(page,"13-source-configuration-saved.png")

        # Catalog create/update, dynamic fields, bulk ingestion/export and archive.
        page.get_by_role("link",name="Offerings",exact=True).click()
        page.get_by_role("button",name="Add offering",exact=True).click()
        page.get_by_label("Name").fill(OFFERING)
        choose(page,"Offering type","PRODUCT")
        page.get_by_label("SKU").fill("WH1000XM5-BLK")
        page.get_by_label("Current price").fill("449.99")
        page.get_by_label("Currency").fill("USD")
        page.get_by_label("Market").fill("US")
        page.get_by_label("Category").fill("Electronics > Audio")
        page.get_by_label("Product URL").fill("https://www.sony.com/electronics/headband-headphones/wh-1000xm5")
        page.get_by_label("Description").fill("Wireless over-ear headphones with active noise cancellation and multipoint Bluetooth.")
        page.get_by_label("Dynamic attributes (JSON)").fill('{"brand":"Sony","color":"Black","battery_life_hours":30,"noise_cancellation":true}')
        shot(page,"14-offering-creation-form.png")
        with page.expect_response(lambda r:r.url.endswith("/v1/offerings") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Create offering",exact=True).click()
        assert event.value.status==201,event.value.text()
        offering_id=event.value.json()["id"]
        shot(page,"15-catalog-offering-created.png")
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        row.get_by_role("button",name=OFFERING,exact=True).click()
        page.get_by_text("CURRENT PRICE",exact=True).wait_for()
        shot(page,"16-offering-detail-and-history.png")
        page.keyboard.press("Escape")
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        row.get_by_title("Edit",exact=True).click()
        page.get_by_label("Current price").fill("429.99")
        with page.expect_response(lambda r:r.url.endswith(f"/v1/offerings/{offering_id}") and r.request.method=="PATCH") as event:
            page.get_by_role("button",name="Save changes",exact=True).click()
        assert event.value.status==200,event.value.text()
        assert float(get_api(page,f"/v1/offerings/{offering_id}")["current_price"])==429.99
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r:r.url.endswith(f"/v1/offerings/{offering_id}/toggle-monitoring") and r.request.method=="POST") as event:
            row.get_by_title("Toggle monitoring",exact=True).click()
        assert event.value.status==200 and get_api(page,f"/v1/offerings/{offering_id}")["is_monitored"] is False
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r:r.url.endswith(f"/v1/offerings/{offering_id}/toggle-monitoring") and r.request.method=="POST") as event:
            row.get_by_title("Toggle monitoring",exact=True).click()
        assert event.value.status==200 and get_api(page,f"/v1/offerings/{offering_id}")["is_monitored"] is True
        shot(page,"17-catalog-monitoring-active.png")
        page.get_by_role("button",name="Dynamic fields",exact=True).click()
        page.get_by_text("Dynamic field definitions",exact=True).wait_for()
        shot(page,"18-dynamic-fields.png")
        page.get_by_role("button",name="Add field",exact=True).click()
        page.get_by_label("Machine name").fill("review_cycle_months")
        page.get_by_label("Display name").fill("Review Cycle")
        page.get_by_label("Data type").fill("NUMBER")
        page.get_by_label("Unit").fill("months")
        page.get_by_label("Category").fill("Commercial")
        shot(page,"19-dynamic-field-form.png")
        with page.expect_response(lambda r:r.url.endswith("/v1/offerings/fields") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Create field",exact=True).click()
        assert event.value.status==201,event.value.text()
        shot(page,"20-dynamic-field-created.png")
        fieldrow=page.locator("div.list-row").filter(has_text="Review Cycle").last
        with page.expect_response(lambda r:"/v1/offerings/fields/" in r.url and r.request.method=="DELETE") as event:
            fieldrow.locator("button.danger-icon").click()
        assert event.value.status==204,event.value.text()
        page.keyboard.press("Escape"); page.keyboard.press("Escape")
        page.get_by_role("button",name="Bulk import",exact=True).click()
        bulk=[
        {"name":"Sony ULT WEAR Wireless Headphones","offering_type":"PRODUCT","sku":"ULTWEAR-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/headband-headphones/ult-wear","category":"Electronics > Audio","attributes":{"brand":"Sony","color":"Black"}},
        {"name":"Sony LinkBuds S","offering_type":"PRODUCT","sku":"LINKBUDS-S-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/truly-wireless/linkbuds-s","category":"Electronics > Audio","attributes":{"brand":"Sony","fit":"In-ear"}}]
        page.get_by_label("Offering JSON").fill(json.dumps(bulk))
        shot(page,"21-bulk-import-form.png")
        with page.expect_response(lambda r:r.url.endswith("/v1/offerings/bulk") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Import offerings",exact=True).click()
        assert event.value.status==200,event.value.text()
        assert event.value.json()["successful_count"]==2,event.value.text()
        shot(page,"22-bulk-imported-catalog.png")
        for label,path in [("CSV","/tmp/nexora-catalog.csv"),("JSON","/tmp/nexora-catalog.json")]:
            with page.expect_download(timeout=15000) as dl:
                page.get_by_role("button",name=label,exact=True).click()
            dl.value.save_as(path)
            assert Path(path).is_file() and Path(path).stat().st_size>0
        page.get_by_placeholder("Search name, SKU, category…").fill("Sony ULT WEAR")
        page.get_by_text("Sony ULT WEAR Wireless Headphones",exact=True).wait_for()
        page.get_by_label("Select Sony ULT WEAR Wireless Headphones",exact=True).check()
        with page.expect_response(lambda r:r.url.endswith("/v1/offerings/bulk-archive") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Archive 1",exact=True).click()
        assert event.value.status==200,event.value.text()
        assert event.value.json()["archived_count"]==1
        archived=get_api(page,"/v1/offerings?q=Sony%20ULT%20WEAR&include_archived=true&page=1&page_size=20")
        assert any(x["is_archived"] for x in archived["items"])
        page.get_by_placeholder("Search name, SKU, category…").fill("")
        page.get_by_text(OFFERING,exact=True).wait_for()
        shot(page,"23-catalog-import-export-and-archive.png")

        # Map and collect an offering using real outbound HTTP requests.
        page.get_by_role("link",name="Matches",exact=True).click()
        page.get_by_role("button",name="Add match",exact=True).click()
        choose(page,"Offering",OFFERING)
        choose(page,"Source",source_name)
        page.get_by_label("Competitor target URL").fill(HIGH)
        choose(page,"Status","APPROVED")
        page.get_by_label("Confidence (0–1)").fill("0.98")
        shot(page,"24-offering-match-form.png")
        with page.expect_response(lambda r:r.url.endswith("/v1/offering-matches") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Create match",exact=True).click()
        assert event.value.status==201,event.value.text()
        match_id=event.value.json()["id"]
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        shot(page,"25-offering-match-created.png")
        with page.expect_response(lambda r:"/v1/collections/run" in r.url and r.request.method=="POST") as event:
            row.get_by_title("Run collection",exact=True).click()
        first=event.value
        assert first.status in (200,201),first.text()
        first_data=first.json()
        assert first_data["status"]=="COMPLETED",first_data
        assert first_data["observation"]["price"]=="399.99",first_data
        assert first_data["observation"]["http_status_code"]==200,first_data
        assert len(get_api(page,f"/v1/offerings/{offering_id}/history"))>=1
        shot(page,"26-first-price-observation.png")

        # Trigger, read and email a threshold event generated by a lower second observation.
        page.get_by_role("link",name="Alerts",exact=True).click()
        page.get_by_role("button",name="New rule",exact=True).click()
        page.get_by_label("Rule name").fill("Sony retail price drop")
        choose(page,"Alert type","PERCENTAGE_DROP")
        choose(page,"Offering scope",OFFERING)
        page.get_by_label("Threshold").fill("10")
        page.get_by_label("Cooldown (minutes)").fill("60")
        shot(page,"27-alert-rule-form.png")
        with page.expect_response(lambda r:r.url.endswith("/v1/alerts/rules") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Create rule",exact=True).click()
        assert event.value.status==201,event.value.text()
        rule_id=event.value.json()["id"]
        shot(page,"28-alert-rule-created.png")
        page.get_by_role("link",name="Matches",exact=True).click()
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        row.get_by_title("Edit",exact=True).click()
        page.get_by_label("Competitor target URL").fill(LOW)
        with page.expect_response(lambda r:r.url.endswith(f"/v1/offering-matches/{match_id}") and r.request.method=="PATCH") as event:
            page.get_by_role("button",name="Save changes",exact=True).click()
        assert event.value.status==200,event.value.text()
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r:"/v1/collections/run" in r.url and r.request.method=="POST") as event:
            row.get_by_title("Run collection",exact=True).click()
        second=event.value
        assert second.status in (200,201),second.text()
        second_data=second.json()
        assert second_data["observation"]["price"]=="349.99",second_data
        assert second_data["snapshot"]["previous_price"]=="399.99",second_data
        assert second_data["snapshot"]["percentage_difference"].startswith("-12.50%"),second_data
        page.get_by_role("link",name="Alerts",exact=True).click()
        page.get_by_text("Competitor price dropped",exact=True).wait_for(timeout=15000)
        logs=get_api(page,"/v1/alerts/logs")
        alert=next((x for x in logs if x["title"]=="Competitor price dropped"),None)
        assert alert and not alert["is_read"],logs
        page.get_by_title("Mark as read",exact=True).click()
        page.get_by_title("Read",exact=True).wait_for()
        assert any(x["id"]==alert["id"] and x["is_read"] for x in get_api(page,"/v1/alerts/logs"))
        shot(page,"29-alert-generated-and-read.png")
        mail_start=len(inbox())
        sent=dispatch_pending_notifications.run()
        assert int(sent.get("sent",0))>=1,sent
        _,alert_email=wait_mail("Nexora Competitive Alert: Competitor price dropped",EMAIL,mail_start)
        assert "Nexora detected a competitive intelligence event" in alert_email
        assert "SENT" in asyncio.run(mail_statuses(client_id))

        page.get_by_role("link",name="Jobs",exact=True).click()
        page.get_by_text("ON DEMAND REFRESH",exact=False).wait_for()
        shot(page,"30-collection-job-history.png")
        page.get_by_role("button",name="Details",exact=True).first.click()
        page.get_by_text("Job ID",exact=True).wait_for()
        shot(page,"31-collection-job-detail.png")
        page.keyboard.press("Escape")

        # SSRF protection plus structured discovery / upsert lifecycle.
        page.get_by_role("link",name="Discovery",exact=True).click()
        page.get_by_label("Website URL").fill("http://127.0.0.1:8000/v1/health")
        page.get_by_label("Max pages").fill("1")
        with page.expect_response(lambda r:r.url.endswith("/v1/discovery/run") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Run discovery",exact=True).click()
        assert event.value.status==422,event.value.text()
        shot(page,"32-private-target-blocked.png")
        page.get_by_label("Website URL").fill(DISCOVERY)
        with page.expect_response(lambda r:r.url.endswith("/v1/discovery/run") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Run discovery",exact=True).click()
        assert event.value.status==200,event.value.text()
        discovery=event.value.json()
        assert discovery["status"]=="COMPLETED",discovery
        assert discovery["created_offerings_count"]==1,discovery
        assert discovery["items"][0]["name"]==DISCOVERED,discovery
        page.get_by_text(DISCOVERED,exact=True).wait_for(timeout=15000)
        shot(page,"33-discovery-product-created.png")
        readback=get_api(page,f"/v1/discovery/jobs/{discovery['job_id']}")
        assert readback["items"][0]["sku"]=="WF1000XM5-BLK",readback
        with page.expect_response(lambda r:r.url.endswith("/v1/discovery/run") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Run discovery",exact=True).click()
        again=event.value.json()
        assert event.value.status==200,event.value.text()
        assert again["created_offerings_count"]==0 and again["updated_offerings_count"]==1,again
        items=get_api(page,"/v1/offerings?q=Sony%20WF-1000XM5&page=1&page_size=20")["items"]
        assert sum(x["sku"]=="WF1000XM5-BLK" for x in items)==1,items
        shot(page,"34-discovery-upsert-history.png")

        # Workspace settings and password lifecycle use actual API and mail tokens.
        page.locator("button.profile-trigger").click()
        page.get_by_role("menuitem",name="Account settings",exact=True).click()
        page.get_by_role("heading",name="Settings",exact=True).wait_for()
        shot(page,"35-workspace-settings.png")
        page.get_by_label("Company name").fill("Northstar Analytics")
        page.get_by_label("Country").fill("US")
        page.get_by_label("Default currency").fill("USD")
        page.get_by_label("Market").fill("US")
        page.get_by_label("Industry").fill("Consumer Electronics")
        page.get_by_label("Timezone").fill("America/New_York")
        with page.expect_response(lambda r:r.url.endswith("/v1/auth/profile") and r.request.method=="PATCH") as event:
            page.get_by_role("button",name="Save profile",exact=True).click()
        assert event.value.status==200,event.value.text()
        assert get_api(page,"/v1/auth/profile")["company_name"]=="Northstar Analytics"
        shot(page,"36-workspace-profile-updated.png")
        page.get_by_label("Current password").fill(PWD)
        page.get_by_label("New password").fill(CHANGED)
        with page.expect_response(lambda r:r.url.endswith("/v1/auth/change-password") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Update password",exact=True).click()
        assert event.value.status==200,event.value.text()
        assert page.request.post(API+"/v1/auth/login",json={"email":EMAIL,"password":PWD}).status==401
        assert page.request.post(API+"/v1/auth/login",json={"email":EMAIL,"password":CHANGED}).status==200
        shot(page,"37-password-changed.png")
        sign_out(page)
        page.get_by_role("link",name="Forgot password?",exact=True).click()
        page.get_by_label("Work email").fill(EMAIL)
        mail_start=len(inbox())
        with page.expect_response(lambda r:r.url.endswith("/v1/auth/forgot-password") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Send reset link",exact=True).click()
        assert event.value.status==200,event.value.text()
        page.get_by_role("heading",name="Check your inbox",exact=True).wait_for()
        shot(page,"38-password-reset-requested.png")
        _,reset_email=wait_mail("Reset your Nexora password",EMAIL,mail_start)
        page.goto(link_from(reset_email,"reset-password"),wait_until="networkidle")
        page.get_by_label("New password").wait_for()
        shot(page,"39-password-reset-form.png")
        page.get_by_label("New password").fill(RESET)
        with page.expect_response(lambda r:r.url.endswith("/v1/auth/reset-password") and r.request.method=="POST") as event:
            page.get_by_role("button",name="Update password",exact=True).click()
        assert event.value.status==200,event.value.text()
        page.get_by_role("heading",name="Password updated",exact=True).wait_for()
        shot(page,"40-password-reset-complete.png")
        page.get_by_role("link",name="Continue to sign in",exact=True).click()
        sign_in(page,EMAIL,RESET)
        shot(page,"41-dashboard-after-password-reset.png")

        viewer=asyncio.run(add_role_user(client_id,RoleEnum.VIEWER,"review"))
        analyst=asyncio.run(add_role_user(client_id,RoleEnum.ANALYST,"review"))
        sign_out(page)
        sign_in(page,analyst,ROLE_PWD)
        page.get_by_role("link",name="Competitors",exact=True).click()
        assert page.get_by_role("button",name="Add competitor",exact=True).count()==0
        denied=page.request.post(API+"/v1/competitors",headers={"Authorization":"Bearer "+access_token(page)},
            json={"name":"Not Allowed","domain":"forbidden.example"})
        assert denied.status==403,denied.text()
        page.get_by_role("link",name="Discovery",exact=True).click()
        assert page.get_by_role("button",name="Run discovery",exact=True).is_visible()
        shot(page,"42-analyst-workspace.png")
        sign_out(page)
        sign_in(page,viewer,ROLE_PWD)
        page.get_by_role("link",name="Offerings",exact=True).click()
        assert page.get_by_role("button",name="Add offering",exact=True).count()==0
        assert page.get_by_role("button",name="Bulk import",exact=True).count()==0
        denied=page.request.post(API+"/v1/competitors",headers={"Authorization":"Bearer "+access_token(page)},
            json={"name":"Viewer Write Attempt","domain":"viewer-write.example"})
        assert denied.status==403,denied.text()
        assert page.request.get(API+"/v1/offerings",headers={"Authorization":"Bearer "+access_token(page)}).status==200
        shot(page,"43-viewer-read-only-workspace.png")

        mobile_ctx=browser.new_context(viewport={"width":390,"height":844})
        mobile=mobile_ctx.new_page()
        mobile.goto(BASE+"/welcome",wait_until="networkidle")
        dims=mobile.evaluate("() => ({viewport:document.documentElement.clientWidth,content:document.documentElement.scrollWidth})")
        assert dims["content"]<=dims["viewport"],dims
        shot(mobile,"44-mobile-homepage.png")
        mobile_ctx.close()

        # Admin-only deletion and archive operations are performed through the visible UI.
        sign_out(page)
        sign_in(page,EMAIL,RESET)
        page.get_by_role("link",name="Alerts",exact=True).click()
        page.get_by_title("Pause rule",exact=True).click()
        page.get_by_text("PAUSED",exact=False).wait_for()
        page.get_by_title("Activate rule",exact=True).click()
        page.get_by_title("Delete rule",exact=True).click()
        page.get_by_text("No rules configured",exact=True).wait_for()
        assert not any(x["id"]==rule_id for x in get_api(page,"/v1/alerts/rules"))
        shot(page,"45-alert-rule-lifecycle.png")

        page.get_by_role("link",name="Matches",exact=True).click()
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r:r.url.endswith(f"/v1/offering-matches/{match_id}") and r.request.method=="DELETE") as event:
            row.locator("button.danger-icon").click()
        assert event.value.status==204,event.value.text()
        assert not any(x["id"]==match_id for x in get_api(page,"/v1/offering-matches"))
        shot(page,"46-match-removed.png")
        page.get_by_role("link",name="Sources",exact=True).click()
        row=page.locator("tbody tr").filter(has_text=source_name).first
        with page.expect_response(lambda r:r.url.endswith(f"/v1/sources/{source_id}") and r.request.method=="DELETE") as event:
            row.locator("button.danger-icon").click()
        assert event.value.status==204,event.value.text()
        assert not any(x["id"]==source_id for x in get_api(page,"/v1/sources"))
        shot(page,"47-source-removed.png")
        page.get_by_role("link",name="Competitors",exact=True).click()
        row=page.locator("tbody tr").filter(has_text="Retail Product Reference").first
        with page.expect_response(lambda r:r.url.endswith(f"/v1/competitors/{competitor_id}") and r.request.method=="DELETE") as event:
            row.locator("button.danger-icon").click()
        assert event.value.status==204,event.value.text()
        assert not any(x["id"]==competitor_id for x in get_api(page,"/v1/competitors"))
        shot(page,"48-competitor-removed.png")
        page.get_by_role("link",name="Offerings",exact=True).click()
        page.get_by_placeholder("Search name, SKU, category…").fill(OFFERING)
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r:r.url.endswith(f"/v1/offerings/{offering_id}") and r.request.method=="DELETE") as event:
            row.get_by_title("Archive",exact=True).click()
        assert event.value.status==204,event.value.text()
        archived=get_api(page,"/v1/offerings?q=Sony%20WH-1000XM5&include_archived=true&page=1&page_size=20")
        assert any(x["id"]==offering_id and x["is_archived"] for x in archived["items"]),archived
        shot(page,"49-offering-archived.png")

        assert not JS_ERRORS,"Browser JavaScript errors: "+" | ".join(JS_ERRORS)
        missing=[filename for filename,_,_ in SCREENS if not (SHOTS/filename).is_file()]
        assert not missing,"Screenshots missing: "+str(missing)
        manifest={"project":"Nexora","generated_by":"tests/e2e/nexora_journey.py",
            "evidence_scope":"isolated CI PostgreSQL, Redis, real browser/API calls and public HTTP product-page fixtures",
            "screenshots":[{"file":fn,"title":title,"description":desc} for fn,title,desc in SCREENS]}
        (SHOTS/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
        print(f"Nexora browser/API/PostgreSQL journey succeeded with {len(SCREENS)} screenshots.",flush=True)
        browser.close()
        ctx.close()

if __name__=="__main__":
    main()
