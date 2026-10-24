"""Real browser → FastAPI → PostgreSQL walkthrough for Nexora."""
from __future__ import annotations
import asyncio, json, os, re, time, uuid
from email import message_from_string
from pathlib import Path

from playwright.sync_api import Page, sync_playwright
from sqlalchemy import select
from backend.core.security import get_password_hash
from backend.db.session import AsyncSessionLocal
from backend.models.client import UserModel
from backend.models.enums import RoleEnum
from backend.models.notification import NotificationOutboxModel
from backend.workers.tasks import dispatch_pending_notifications

FRONT = os.getenv("NEXORA_FRONTEND_URL", "http://127.0.0.1:4173").rstrip("/")
API = os.getenv("NEXORA_API_URL", "http://127.0.0.1:8000").rstrip("/")
MAILBOX = Path(os.getenv("NEXORA_MAILBOX", "/tmp/nexora-mailbox.jsonl"))
OUT = Path("docs/walkthrough/screenshots")
EMAIL, PASSWORD = "market-analyst@northstar.example.com", "Nexora-Strong!2026"
CHANGED, RESET, ROLE_PASSWORD = "Nexora-Updated!2026", "Nexora-Final!2026", "Nexora-Role!2026"
OFFERING = "Sony WH-1000XM5 Wireless Headphones"
DISCOVERED = "Sony WF-1000XM5 Truly Wireless Noise Canceling Earbuds"
HIGH = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-price-high.html"
LOW = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-price-low.html"
DISCOVERY = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures/retail-discovery-product.html"
SHOTS = [
"00-public-homepage.png","01-registration-form.png","02-verification-email-sent.png","03-email-verified.png",
"04-workspace-dashboard.png","05-competitor-created.png","06-duplicate-domain-blocked.png","07-source-config-saved.png",
"08-offering-created.png","09-offering-detail.png","10-monitoring-control.png","11-dynamic-fields.png",
"12-bulk-import-export-archive.png","13-offering-match-created.png","14-first-price-observation.png",
"15-alert-rule-created.png","16-price-alert-triggered.png","17-collection-jobs.png","18-private-target-rejected.png",
"19-discovery-created.png","20-discovery-upsert.png","21-workspace-profile.png","22-password-changed.png",
"23-password-reset-requested.png","24-password-reset-completed.png","25-dashboard-after-recovery.png",
"26-analyst-access.png","27-viewer-read-only.png","28-super-admin-access.png","29-mobile-homepage.png"]
JS_ERRORS: list[str] = []

def shot(page: Page, name: str):
    OUT.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(OUT / name), full_page=True, animations="disabled", caret="hide")
    print("SCREENSHOT " + name, flush=True)

def choose(page: Page, label: str, value: str):
    page.locator("label.field").filter(has_text=label).last.locator("button.select-trigger").click()
    page.get_by_role("option", name=re.compile(re.escape(value))).last.click()

def call(page: Page, part: str, method: str, action, codes=(200,)):
    with page.expect_response(lambda r: part in r.url and r.request.method == method) as ctx:
        action()
    res = ctx.value
    assert res.status in codes, f"{method} {part}: {res.status} {res.text()}"
    return res

def access(page: Page) -> str:
    value = page.evaluate("() => localStorage.getItem('nexora.access')")
    assert value, "No access token after actual UI sign-in"
    return value

def get(page: Page, path: str):
    res = page.request.get(API + path, headers={"Authorization": "Bearer " + access(page)})
    assert res.status == 200, f"GET {path}: {res.status} {res.text()}"
    return res.json()

def post_as(page: Page, path: str, body: dict, status: int):
    res = page.request.post(API + path,
        headers={"Authorization": "Bearer " + access(page), "Content-Type": "application/json"},
        data=json.dumps(body))
    assert res.status == status, f"POST {path}: {res.status} {res.text()}"
    return res

def mailbox():
    if not MAILBOX.exists(): return []
    result=[]
    for line in MAILBOX.read_text(encoding="utf-8").splitlines():
        try:
            row=json.loads(line)
            if row.get("data"): result.append(row)
        except (json.JSONDecodeError, AttributeError): pass
    return result

def parse_mail(row):
    msg=message_from_string(str(row["data"]))
    parts=[]
    if msg.is_multipart():
        for p in msg.walk():
            if p.get_content_type()=="text/plain" and p.get_payload(decode=True):
                parts.append(p.get_payload(decode=True).decode(p.get_content_charset() or "utf-8","replace"))
    else:
        raw=msg.get_payload(decode=True)
        parts.append(raw.decode(msg.get_content_charset() or "utf-8","replace") if raw else str(msg.get_payload()))
    return str(msg.get("Subject","")), "\n".join(parts), [str(x).lower() for x in row.get("rcpt_tos",[])]

def wait_mail(subject, recipient, start, timeout=40):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        for row in mailbox()[start:]:
            s,b,rcpts=parse_mail(row)
            if subject.casefold() in s.casefold() and recipient.casefold() in rcpts: return b
        time.sleep(.25)
    raise AssertionError(f"Expected email {subject!r} to {recipient!r}")

def extract_token(body, route):
    m=re.search(rf"https?://[^\s<>]+/{re.escape(route)}\?token=([^\s<>]+)",body)
    assert m, f"Missing {route} link in email"
    return m.group(1).rstrip(".,);")

def login(page, email, password):
    page.get_by_label("Work email").fill(email)
    page.locator("label.field").filter(has_text=re.compile(r"^Password")).locator("input[type=password]").fill(password)
    call(page,"/v1/auth/login","POST",lambda:page.get_by_role("button",name=re.compile("Sign in")).click())
    page.get_by_role("heading",name="Dashboard",exact=True).wait_for(timeout=15000)

def logout(page):
    page.locator("button.profile-trigger").click()
    page.get_by_text("Sign out",exact=True).click()
    page.get_by_label("Work email").wait_for(timeout=12000)

async def seed_role(client_id, role, suffix):
    email=f"{role.value.lower()}-{suffix}@northstar.example.com"
    async with AsyncSessionLocal() as s:
        s.add(UserModel(client_id=client_id,email=email,full_name="Northstar "+role.value.title(),
            hashed_password=get_password_hash(ROLE_PASSWORD),role=role,is_active=True,email_verified=True))
        await s.commit()
    return email

async def outbox_states(client_id):
    async with AsyncSessionLocal() as s:
        rows=await s.execute(select(NotificationOutboxModel.status).where(
            NotificationOutboxModel.client_id==client_id,NotificationOutboxModel.channel=="email"))
        return list(rows.scalars().all())

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if MAILBOX.exists(): MAILBOX.unlink()
    with sync_playwright() as p:
        browser=p.chromium.launch()
        context=browser.new_context(viewport={"width":1440,"height":1000},accept_downloads=True)
        page=context.new_page()
        page.set_default_timeout(12000)
        page.on("pageerror",lambda e:JS_ERRORS.append(str(e)))
        page.on("dialog",lambda d:d.accept())

        # Registration, actual email delivery, verification, sign-in.
        page.goto(FRONT+"/welcome",wait_until="domcontentloaded")
        page.get_by_role("heading",level=1).wait_for()
        shot(page,SHOTS[0])
        page.get_by_role("link",name=re.compile("Start your workspace")).click()
        page.get_by_label("Organization name").fill("Northstar Market Intelligence")
        page.get_by_label("Your full name").fill("Alex Morgan")
        page.get_by_label("Work email").fill(EMAIL)
        page.locator("label.field").filter(has_text=re.compile(r"^Password")).locator("input[type=password]").fill(PASSWORD)
        shot(page,SHOTS[1])
        start=len(mailbox())
        reg=call(page,"/v1/auth/register","POST",lambda:page.get_by_role("button",name=re.compile("Create workspace")).click(),(201,))
        assert reg.json()["email_verification_required"] is True
        page.get_by_role("heading",name="Verification required",exact=True).wait_for()
        shot(page,SHOTS[2])
        body=wait_mail("Verify your Nexora account",EMAIL,start)
        vt=extract_token(body,"verify-email")
        page.goto(f"{FRONT}/verify-email?token={vt}",wait_until="domcontentloaded")
        call(page,"/v1/auth/verify-email","GET",lambda:page.get_by_role("button",name=re.compile("Verify email")).click())
        page.get_by_role("link",name="Continue to sign in",exact=True).wait_for()
        shot(page,SHOTS[3])
        page.get_by_role("link",name="Continue to sign in",exact=True).click()
        login(page,EMAIL,PASSWORD)
        shot(page,SHOTS[4])
        me=get(page,"/v1/auth/me")
        assert me["role"]=="ORG_ADMIN"
        client_id=uuid.UUID(me["client_id"])

        # Competitor creation, duplicate-domain rejection and edit.
        page.get_by_role("link",name="Competitors",exact=True).click()
        page.get_by_role("button",name="Add competitor",exact=True).click()
        page.get_by_label("Name").fill("Retail Product Reference")
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        cr=call(page,"/v1/competitors","POST",lambda:page.get_by_role("button",name="Save competitor",exact=True).click(),(201,))
        competitor_id=cr.json()["id"]
        shot(page,SHOTS[5])
        page.get_by_role("button",name="Add competitor",exact=True).click()
        page.get_by_label("Name").fill("Duplicate Market Reference")
        page.get_by_label("Domain").fill("cdn.jsdelivr.net")
        call(page,"/v1/competitors","POST",lambda:page.get_by_role("button",name="Save competitor",exact=True).click(),(403,))
        shot(page,SHOTS[6])
        page.get_by_role("button",name="Cancel",exact=True).click()
        page.locator("tbody tr").filter(has_text="Retail Product Reference").first.locator("button").first.click()
        page.get_by_label("Name").fill("Retail Product Reference Official")
        with page.expect_response(lambda r:f"/v1/competitors/{competitor_id}" in r.url and r.request.method=="PATCH") as ev:
            page.get_by_role("button",name="Save competitor",exact=True).click()
        assert ev.value.status==200,ev.value.text()
        assert any(x["id"]==competitor_id and x["name"]=="Retail Product Reference Official" for x in get(page,"/v1/competitors"))

        # Source creation and source-configuration persistence.
        page.get_by_role("link",name="Sources",exact=True).click()
        page.get_by_role("button",name="Add source",exact=True).click()
        choose(page,"Competitor","Retail Product Reference Official")
        page.get_by_label("Source name").fill("Retail Product Listing")
        page.get_by_label("Base URL").fill(HIGH)
        choose(page,"Source type","OFFICIAL_STORE")
        choose(page,"Collection method","HTTP_FAST")
        src=call(page,"/v1/sources","POST",lambda:page.get_by_role("button",name="Create source",exact=True).click(),(201,))
        source_id=src.json()["id"]
        page.get_by_title("Configuration",exact=True).click()
        page.get_by_label("Rate / minute").fill("60")
        page.get_by_label("Delay seconds").fill("0.1")
        page.get_by_label("Timeout seconds").fill("25")
        page.get_by_label("Max retries").fill("1")
        page.get_by_label("Custom headers (JSON)").fill('{"Accept-Language":"en-US,en;q=0.9"}')
        page.get_by_label("Extraction selectors (JSON)").fill("{}")
        call(page,f"/v1/sources/{source_id}/configuration","PATCH",lambda:page.get_by_role("button",name="Save configuration",exact=True).click())
        source=get(page,f"/v1/sources/{source_id}")
        assert source["configuration"]["rate_limit_rpm"]==60 and source["configuration"]["max_retries"]==1
        page.get_by_title("Edit source",exact=True).click()
        page.get_by_label("Source name").fill("Retail Product Listing (Configured)")
        call(page,f"/v1/sources/{source_id}","PATCH",lambda:page.get_by_role("button",name="Save changes",exact=True).click())
        shot(page,SHOTS[7])

        # Catalog entry, detail and monitoring toggles.
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
        page.get_by_label("Description").fill("Wireless over-ear headphones with active noise cancellation.")
        page.get_by_label("Dynamic attributes (JSON)").fill('{"brand":"Sony","color":"Black","battery_life_hours":30}')
        offering=call(page,"/v1/offerings","POST",lambda:page.get_by_role("button",name="Create offering",exact=True).click(),(201,))
        offering_id=offering.json()["id"]
        shot(page,SHOTS[8])
        page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_role("button",name=OFFERING,exact=True).click()
        page.get_by_text("CURRENT PRICE",exact=True).wait_for()
        assert get(page,f"/v1/offerings/{offering_id}")["attributes"]["battery_life_hours"]==30
        shot(page,SHOTS[9])
        page.keyboard.press("Escape")
        page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_title("Edit",exact=True).click()
        page.get_by_label("Current price").fill("429.99")
        call(page,f"/v1/offerings/{offering_id}","PATCH",lambda:page.get_by_role("button",name="Save changes",exact=True).click())
        assert float(get(page,f"/v1/offerings/{offering_id}")["current_price"])==429.99
        for enabled in (False,True):
            row=page.locator("tbody tr").filter(has_text=OFFERING).first
            call(page,f"/v1/offerings/{offering_id}/toggle-monitoring","POST",lambda row=row:row.get_by_title("Toggle monitoring",exact=True).click())
            assert get(page,f"/v1/offerings/{offering_id}")["is_monitored"] is enabled
        shot(page,SHOTS[10])

        # Dynamic fields and catalog import/export/archive.
        page.get_by_role("button",name="Dynamic fields",exact=True).click()
        page.get_by_text("Dynamic field definitions",exact=True).wait_for()
        page.get_by_role("button",name="Add field",exact=True).click()
        page.get_by_label("Machine name").fill("review_cycle_months")
        page.get_by_label("Display name").fill("Review Cycle")
        page.get_by_label("Data type").fill("NUMBER")
        page.get_by_label("Unit").fill("months")
        page.get_by_label("Category").fill("Commercial")
        field=call(page,"/v1/offerings/fields","POST",lambda:page.get_by_role("button",name="Create field",exact=True).click(),(201,))
        page.get_by_text("Review Cycle",exact=True).wait_for()
        shot(page,SHOTS[11])
        field_id=field.json()["id"]
        row=page.locator("div.list-row").filter(has_text="Review Cycle").last
        call(page,f"/v1/offerings/fields/{field_id}","DELETE",lambda:row.locator("button.danger-icon").click(),(204,))
        page.keyboard.press("Escape")
        payload=[
          {"name":"Sony ULT WEAR Wireless Headphones","offering_type":"PRODUCT","sku":"ULTWEAR-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/headband-headphones/ult-wear","category":"Electronics > Audio","attributes":{"brand":"Sony"}},
          {"name":"Sony LinkBuds S","offering_type":"PRODUCT","sku":"LINKBUDS-S-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/truly-wireless/linkbuds-s","category":"Electronics > Audio","attributes":{"brand":"Sony"}}
        ]
        page.get_by_role("button",name="Bulk import",exact=True).click()
        page.get_by_label("Offering JSON").fill(json.dumps(payload))
        bulk=call(page,"/v1/offerings/bulk","POST",lambda:page.get_by_role("button",name="Import offerings",exact=True).click())
        assert bulk.json()["successful_count"]==2
        for label,filepath in [("CSV","/tmp/nexora.csv"),("JSON","/tmp/nexora.json")]:
            with page.expect_download(timeout=15000) as download:
                page.get_by_role("button",name=label,exact=True).click()
            download.value.save_as(filepath)
            assert Path(filepath).stat().st_size>0
        page.get_by_placeholder("Search name, SKU, category…").fill("Sony ULT WEAR")
        page.get_by_label("Select Sony ULT WEAR Wireless Headphones",exact=True).check()
        archive=call(page,"/v1/offerings/bulk-archive","POST",lambda:page.get_by_role("button",name=re.compile("Archive 1")).click())
        assert archive.json()["archived_count"]==1
        archived=get(page,"/v1/offerings?q=Sony%20ULT%20WEAR&include_archived=true&page=1&page_size=20")
        assert any(x["is_archived"] for x in archived["items"])
        shot(page,SHOTS[12])
        page.get_by_placeholder("Search name, SKU, category…").fill("")

        # Match mapping, HTTP collection, snapshot and price history.
        page.get_by_role("link",name="Matches",exact=True).click()
        page.get_by_role("button",name="Add match",exact=True).click()
        choose(page,"Offering",OFFERING)
        choose(page,"Source","Retail Product Listing (Configured)")
        page.get_by_label("Competitor target URL").fill(HIGH)
        choose(page,"Status","APPROVED")
        page.get_by_label(re.compile("Confidence")).fill("0.98")
        match=call(page,"/v1/offering-matches","POST",lambda:page.get_by_role("button",name="Create match",exact=True).click(),(201,))
        match_id=match.json()["id"]
        shot(page,SHOTS[13])
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        first=call(page,"/v1/collections/run","POST",lambda:row.get_by_title("Run collection",exact=True).click(),(200,201)).json()
        assert first["status"]=="COMPLETED" and first["observation"]["price"]=="399.99",first
        assert first["observation"]["http_status_code"]==200
        assert len(get(page,f"/v1/offerings/{offering_id}/history"))>=1
        shot(page,SHOTS[14])

        # Alert rule, second lower page fetch, persistent log and email dispatch.
        page.get_by_role("link",name="Alerts",exact=True).click()
        page.get_by_role("button",name="New rule",exact=True).click()
        page.get_by_label("Rule name").fill("Sony retail price drop")
        choose(page,"Alert type","PERCENTAGE_DROP")
        choose(page,"Offering scope",OFFERING)
        page.get_by_label("Threshold").fill("10")
        page.get_by_label("Cooldown (minutes)").fill("60")
        rule=call(page,"/v1/alerts/rules","POST",lambda:page.get_by_role("button",name="Create rule",exact=True).click(),(201,))
        shot(page,SHOTS[15])
        page.get_by_role("link",name="Matches",exact=True).click()
        page.locator("tbody tr").filter(has_text=OFFERING).first.get_by_title("Edit",exact=True).click()
        page.get_by_label("Competitor target URL").fill(LOW)
        call(page,f"/v1/offering-matches/{match_id}","PATCH",lambda:page.get_by_role("button",name="Save changes",exact=True).click())
        row=page.locator("tbody tr").filter(has_text=OFFERING).first
        second=call(page,"/v1/collections/run","POST",lambda:row.get_by_title("Run collection",exact=True).click(),(200,201)).json()
        assert second["observation"]["price"]=="349.99" and second["snapshot"]["previous_price"]=="399.99",second
        assert second["snapshot"]["percentage_difference"].startswith("-12.50%"),second
        page.get_by_role("link",name="Alerts",exact=True).click()
        page.get_by_text("Competitor price dropped",exact=True).wait_for(timeout=15000)
        logs=get(page,"/v1/alerts/logs")
        alert=next((x for x in logs if x["title"]=="Competitor price dropped"),None)
        assert alert and not alert["is_read"],logs
        page.get_by_title("Mark as read",exact=True).click()
        page.get_by_title("Read",exact=True).wait_for()
        assert any(x["id"]==alert["id"] and x["is_read"] for x in get(page,"/v1/alerts/logs"))
        shot(page,SHOTS[16])
        start=len(mailbox())
        sent=dispatch_pending_notifications.run()
        assert int(sent.get("sent",0))>=1,sent
        body=wait_mail("Nexora Competitive Alert: Competitor price dropped",EMAIL,start)
        assert "Nexora detected a competitive intelligence event" in body
        async_states=asyncio.run(outbox_states(client_id))
        assert "SENT" in async_states,async_states

        # Real collection jobs remain visible with persisted metadata.
        page.get_by_role("link",name="Jobs",exact=True).click()
        page.get_by_role("heading",name="Jobs",exact=True).wait_for()
        page.get_by_role("button",name=re.compile("Details")).first.wait_for()
        page.get_by_role("button",name=re.compile("Details")).first.click()
        page.get_by_text("Job ID",exact=True).wait_for()
        shot(page,SHOTS[17])
        page.keyboard.press("Escape")

        # Private URL rejection followed by real structured-product discovery and upsert.
        page.get_by_role("link",name="Discovery",exact=True).click()
        page.get_by_label("Website URL").fill("http://127.0.0.1:8000/v1/health")
        page.get_by_label("Max pages").fill("1")
        call(page,"/v1/discovery/run","POST",lambda:page.get_by_role("button",name="Run discovery",exact=True).click(),(422,))
        shot(page,SHOTS[18])
        page.get_by_label("Website URL").fill(DISCOVERY)
        choose(page,"Default type","PRODUCT")
        discovery=call(page,"/v1/discovery/run","POST",lambda:page.get_by_role("button",name="Run discovery",exact=True).click()).json()
        assert discovery["status"]=="COMPLETED" and discovery["created_offerings_count"]==1,discovery
        assert discovery["items"][0]["name"]==DISCOVERED,discovery
        page.get_by_text(DISCOVERED,exact=True).wait_for()
        assert get(page,f"/v1/discovery/jobs/{discovery['job_id']}")["items"][0]["sku"]=="WF1000XM5-BLK"
        shot(page,SHOTS[19])
        again=call(page,"/v1/discovery/run","POST",lambda:page.get_by_role("button",name="Run discovery",exact=True).click()).json()
        assert again["created_offerings_count"]==0 and again["updated_offerings_count"]==1,again
        catalog=get(page,"/v1/offerings?q=Sony%20WF-1000XM5&page=1&page_size=20")
        assert sum(x["sku"]=="WF1000XM5-BLK" for x in catalog["items"])==1
        shot(page,SHOTS[20])

        # Workspace profile, password change, actual reset email and one-time token.
        page.locator("button.profile-trigger").click()
        page.get_by_text("Account settings",exact=True).click()
        page.get_by_role("heading",name="Settings",exact=True).wait_for()
        shot(page,SHOTS[21])
        for label,value in [("Company name","Northstar Analytics"),("Country","US"),("Default currency","USD"),("Market","US"),("Industry","Consumer Electronics"),("Timezone","America/New_York")]:
            page.get_by_label(label).fill(value)
        call(page,"/v1/auth/profile","PATCH",lambda:page.get_by_role("button",name="Save profile",exact=True).click())
        assert get(page,"/v1/auth/profile")["company_name"]=="Northstar Analytics"
        page.get_by_label("Current password").fill(PASSWORD)
        page.get_by_label("New password").fill(CHANGED)
        call(page,"/v1/auth/change-password","POST",lambda:page.get_by_role("button",name="Update password",exact=True).click())
        old=page.request.post(API+"/v1/auth/login",headers={"Content-Type":"application/json"},data=json.dumps({"email":EMAIL,"password":PASSWORD}))
        assert old.status==401,old.text()
        current=page.request.post(API+"/v1/auth/login",headers={"Content-Type":"application/json"},data=json.dumps({"email":EMAIL,"password":CHANGED}))
        assert current.status==200,current.text()
        shot(page,SHOTS[22])

        logout(page)
        page.get_by_role("link",name="Forgot password?",exact=True).click()
        page.get_by_label("Work email").fill(EMAIL)
        start=len(mailbox())
        call(page,"/v1/auth/forgot-password","POST",lambda:page.get_by_role("button",name="Send reset link",exact=True).click())
        page.get_by_role("heading",name="Check your inbox",exact=True).wait_for()
        shot(page,SHOTS[23])
        reset=email_token(wait_mail("Reset your Nexora password",EMAIL,start),"reset-password")
        page.goto(f"{FRONT}/reset-password?token={reset}",wait_until="domcontentloaded")
        page.get_by_label("New password").fill(RESET)
        call(page,"/v1/auth/reset-password","POST",lambda:page.get_by_role("button",name="Update password",exact=True).click())
        page.get_by_role("heading",name="Password updated",exact=True).wait_for()
        replay=page.request.post(API+"/v1/auth/reset-password",headers={"Content-Type":"application/json"},
            data=json.dumps({"token":reset,"new_password":"Nexora-Replayed!2026"}))
        assert replay.status in (400,422),replay.text()
        shot(page,SHOTS[24])
        page.get_by_role("link",name="Continue to sign in",exact=True).click()
        login(page,EMAIL,RESET)
        shot(page,SHOTS[25])

        # Role checks use stored users with real credentials and real API access tokens.
        suffix=uuid.uuid4().hex[:8]
        analyst=asyncio.run(seed_role(client_id,RoleEnum.ANALYST,suffix))
        viewer=asyncio.run(seed_role(client_id,RoleEnum.VIEWER,suffix))
        super_admin=asyncio.run(seed_role(client_id,RoleEnum.SUPER_ADMIN,suffix))
        logout(page)
        login(page,analyst,ROLE_PASSWORD)
        page.get_by_role("link",name="Competitors",exact=True).click()
        assert page.get_by_role("button",name="Add competitor",exact=True).count()==0
        post_as(page,"/v1/competitors",{"name":"Analyst write should fail","domain":f"analyst-{suffix}.example"},403)
        page.get_by_role("link",name="Discovery",exact=True).click()
        assert page.get_by_role("button",name="Run discovery",exact=True).is_visible()
        shot(page,SHOTS[26])
        logout(page)
        login(page,viewer,ROLE_PASSWORD)
        page.get_by_role("link",name="Offerings",exact=True).click()
        assert page.get_by_role("button",name="Add offering",exact=True).count()==0
        assert page.get_by_role("button",name="Bulk import",exact=True).count()==0
        post_as(page,"/v1/competitors",{"name":"Viewer write should fail","domain":f"viewer-{suffix}.example"},403)
        shot(page,SHOTS[27])
        logout(page)
        login(page,super_admin,ROLE_PASSWORD)
        page.get_by_role("link",name="Competitors",exact=True).click()
        assert page.get_by_role("button",name="Add competitor",exact=True).is_visible()
        shot(page,SHOTS[28])

        mobile=context.new_page()
        mobile.set_viewport_size({"width":390,"height":844})
        mobile.goto(FRONT+"/welcome",wait_until="domcontentloaded")
        mobile.get_by_role("heading",level=1).wait_for()
        size=mobile.evaluate("() => ({viewport:document.documentElement.clientWidth,content:document.documentElement.scrollWidth})")
        assert size["content"]<=size["viewport"],size
        shot(mobile,SHOTS[29])
        assert not JS_ERRORS,"Browser JavaScript errors: "+" | ".join(JS_ERRORS)
        missing=[name for name in SHOTS if not (OUT/name).is_file()]
        assert not missing,f"Missing walkthrough screenshots: {missing}"
        print(f"FULLSTACK PASS: UI/API/PostgreSQL and {len(SHOTS)} screenshots.",flush=True)
        browser.close()
        context.close()

if __name__=="__main__":
    main()
