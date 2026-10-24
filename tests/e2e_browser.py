"""Real-browser Nexora workflow: React UI -> FastAPI -> PostgreSQL/Redis -> SMTP."""
from __future__ import annotations
import asyncio, json, os, re, threading, time, uuid
from email import message_from_string
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import Browser, Page, sync_playwright
from sqlalchemy import select
from backend.core.security import get_password_hash
from backend.db.session import AsyncSessionLocal
from backend.models.alert import AlertLogModel
from backend.models.client import UserModel
from backend.models.competitor import CompetitorModel, OfferingMatchModel, SourceModel
from backend.models.enums import RoleEnum
from backend.models.notification import NotificationOutboxModel
from backend.models.observation import JobModel, ObservationModel, SnapshotModel
from backend.models.offering import OfferingModel

FRONTEND = os.getenv("NEXORA_FRONTEND_URL", "http://127.0.0.1:4173").rstrip("/")
API = os.getenv("NEXORA_API_URL", "http://127.0.0.1:8000").rstrip("/")
MAILBOX = Path(os.getenv("NEXORA_MAILBOX", "/tmp/nexora-mailbox.jsonl"))
SCREENSHOTS = Path(os.getenv("NEXORA_SCREENSHOTS", "docs/testing/screenshots"))
EMAIL = "market-analyst@northstar.example.com"
PASSWORD = "Nexora-Strong!2026"
CHANGED_PASSWORD = "Nexora-Changed!2026"
RESET_PASSWORD = "Nexora-Reset!2026"
ROLE_PASSWORD = "Nexora-Role!2026"
ORGANIZATION = "Northstar Market Intelligence"
FULL_NAME = "Alex Morgan"
COMPETITOR = "Retail Product Reference"
SOURCE = "Retail Product Listing"
OFFERING = "Sony WH-1000XM5 Wireless Headphones"
DISCOVERED = "Sony WF-1000XM5 Truly Wireless Noise Canceling Earbuds"
FIXTURES = "https://cdn.jsdelivr.net/gh/faizansaiyed123/Nexora-backend@main/tests/fixtures"
HIGH_URL = f"{FIXTURES}/retail-price-high.html"
LOW_URL = f"{FIXTURES}/retail-price-low.html"
DISCOVERY_URL = f"{FIXTURES}/retail-discovery-product.html"
js_errors: list[str] = []

def shot(page: Page, filename: str) -> None:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SCREENSHOTS / filename), full_page=True, animations="disabled", caret="hide")
    print(f"SCREENSHOT {filename}", flush=True)

def choose(page: Page, label: str, option: str) -> None:
    field = page.locator("label.field").filter(has_text=label).last
    field.locator("button.select-trigger").click()
    page.get_by_role("option", name=re.compile("^" + re.escape(option))).last.click()

def input_field(page: Page, label: str):
    pattern = re.compile("^" + re.escape(label), re.IGNORECASE)
    return page.locator("label.field").filter(has_text=pattern).last.locator("input").first

def token(page: Page) -> str:
    value = page.evaluate("() => localStorage.getItem('nexora.access')")
    assert value, "No browser access token was saved after authentication."
    return str(value)

def api_get(page: Page, path: str, expected: int = 200):
    r = page.request.get(API + path, headers={"Authorization": f"Bearer {token(page)}"})
    assert r.status == expected, f"GET {path}: HTTP {r.status}: {r.text()}"
    return r.json()

def api_post(page: Page, path: str, payload: dict, extra_headers: dict[str, str] | None = None):
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    return page.request.post(API + path, data=json.dumps(payload), headers=headers)

def mailbox() -> list[dict]:
    if not MAILBOX.exists(): return []
    rows = []
    for line in MAILBOX.read_text(encoding="utf-8").splitlines():
        try: value = json.loads(line)
        except json.JSONDecodeError: continue
        if isinstance(value, dict) and value.get("data"): rows.append(value)
    return rows

def mail_fields(item: dict) -> tuple[str, str, list[str]]:
    msg = message_from_string(str(item["data"]))
    subject = str(msg.get("Subject", ""))
    if msg.is_multipart():
        bodies = []
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                data = part.get_payload(decode=True)
                if data: bodies.append(data.decode(part.get_content_charset() or "utf-8", "replace"))
        body = "\n".join(bodies)
    else:
        data = msg.get_payload(decode=True)
        body = data.decode(msg.get_content_charset() or "utf-8", "replace") if data else str(msg.get_payload())
    return subject, body, [str(x).lower() for x in item.get("rcpt_tos", [])]

def wait_email(subject_piece: str, recipient: str, start: int, timeout: float = 35) -> tuple[dict, str]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for item in mailbox()[start:]:
            subject, body, rcpts = mail_fields(item)
            if subject_piece.lower() in subject.lower() and recipient.lower() in rcpts: return item, body
        time.sleep(0.25)
    raise AssertionError(f"Email {subject_piece!r} not delivered to {recipient!r}; new inbox messages: {[mail_fields(x)[0] for x in mailbox()[start:]]}")

def email_link(body: str, route: str) -> str:
    m = re.search(rf"https?://[^\s<>]+/{re.escape(route)}\?token=[^\s<>]+", body)
    assert m, f"Actual email did not contain the one-time {route} link."
    return m.group(0).rstrip(".,);")

def login_ui(page: Page, email: str, password: str) -> None:
    input_field(page, "Work email").fill(email)
    input_field(page, "Password").fill(password)
    with page.expect_response(lambda r: r.url.endswith("/v1/auth/login") and r.request.method == "POST") as event:
        page.get_by_role("button", name=re.compile("Sign in")).click()
    assert event.value.status == 200, event.value.text()
    page.get_by_role("heading", name="Dashboard", exact=True).last.wait_for(timeout=15000)

def logout_ui(page: Page) -> None:
    page.locator("button.profile-trigger").click()
    page.get_by_text("Sign out", exact=True).click()
    page.get_by_label("Work email").wait_for(timeout=15000)

async def add_role_user(client_id: uuid.UUID, role: RoleEnum) -> str:
    email = f"{role.value.lower()}-workspace@northstar.example.com"
    async with AsyncSessionLocal() as session:
        found = await session.scalar(select(UserModel).where(UserModel.email == email))
        if not found:
            session.add(UserModel(client_id=client_id, email=email, full_name=f"Northstar {role.value.title()}",
                hashed_password=get_password_hash(ROLE_PASSWORD), role=role, is_active=True, email_verified=True))
            await session.commit()
    return email

async def sent_statuses(client_id: uuid.UUID) -> list[str]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(NotificationOutboxModel.status).where(
            NotificationOutboxModel.client_id == client_id, NotificationOutboxModel.channel == "email"))
        return list(result.scalars().all())

async def assert_persisted_market_state(
    client_id: uuid.UUID,
    offering_id: uuid.UUID,
    match_id: uuid.UUID,
    rule_id: uuid.UUID,
) -> dict:
    """Verify core intelligence outputs through direct PostgreSQL reads."""
    async with AsyncSessionLocal() as session:
        observations = list((await session.scalars(
            select(ObservationModel)
            .where(ObservationModel.offering_match_id == match_id)
            .order_by(ObservationModel.observed_at.asc())
        )).all())
        snapshot = await session.scalar(
            select(SnapshotModel).where(SnapshotModel.offering_match_id == match_id)
        )
        alert_rows = list((await session.scalars(
            select(AlertLogModel).where(AlertLogModel.alert_rule_id == rule_id)
        )).all())
        offering = await session.get(OfferingModel, offering_id)
        match = await session.get(OfferingMatchModel, match_id)
        discovered = await session.scalar(select(OfferingModel).where(
            OfferingModel.client_id == client_id,
            OfferingModel.sku == "WF1000XM5-BLK",
        ))
        jobs = list((await session.scalars(
            select(JobModel)
            .join(SourceModel, SourceModel.id == JobModel.source_id)
            .join(CompetitorModel, CompetitorModel.id == SourceModel.competitor_id)
            .where(CompetitorModel.client_id == client_id)
        )).all())
        notification_statuses = list((await session.scalars(
            select(NotificationOutboxModel.status).where(
                NotificationOutboxModel.client_id == client_id,
                NotificationOutboxModel.channel == "email",
            )
        )).all())

        prices = [round(float(row.observed_price), 2) for row in observations if row.observed_price is not None]
        assert prices[:2] == [399.99, 349.99], prices
        assert [row.http_status_code for row in observations[:2]] == [200, 200]
        assert snapshot is not None
        assert round(float(snapshot.current_price), 2) == 349.99
        assert round(float(snapshot.previous_price), 2) == 399.99
        assert round(float(snapshot.percentage_difference), 2) == -12.5
        assert match is not None and match.offering_id == offering_id
        assert offering is not None and offering.client_id == client_id
        assert any(row.title == "Competitor price dropped" and row.is_read for row in alert_rows)
        assert discovered is not None and discovered.name == DISCOVERED
        assert any(row.status.value == "COMPLETED" and row.job_type.value == "ON_DEMAND_REFRESH" for row in jobs)
        assert any(status == "SENT" for status in notification_statuses)
        evidence = {
            "database": "PostgreSQL",
            "observations": len(observations),
            "first_two_observed_prices": prices[:2],
            "http_status_codes": [row.http_status_code for row in observations[:2]],
            "snapshot_current_price": str(snapshot.current_price),
            "snapshot_previous_price": str(snapshot.previous_price),
            "snapshot_change_percent": round(float(snapshot.percentage_difference), 2),
            "persisted_read_alerts": len(alert_rows),
            "completed_collection_jobs": sum(
                row.status.value == "COMPLETED" and row.job_type.value == "ON_DEMAND_REFRESH"
                for row in jobs
            ),
            "email_outbox_sent": sum(status == "SENT" for status in notification_statuses),
            "discovered_offering": discovered.name,
            "tenant_id": str(client_id),
        }
    Path("/tmp/nexora-db-evidence.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )
    print("DIRECT POSTGRESQL READ-BACK: " + json.dumps(evidence, sort_keys=True), flush=True)
    return evidence

_async_loop: asyncio.AbstractEventLoop | None = None
_async_thread: threading.Thread | None = None

def _start_async_loop() -> tuple[asyncio.AbstractEventLoop, threading.Thread]:
    loop = asyncio.new_event_loop()
    def run_loop() -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()
    thread = threading.Thread(target=run_loop, name="nexora-e2e-async-loop", daemon=True)
    thread.start()
    return loop, thread

def run_async(coro, timeout: float = 90):
    """Run async DB/worker work on one stable loop, isolated from Playwright's sync runtime."""
    global _async_loop, _async_thread
    if _async_loop is None:
        _async_loop, _async_thread = _start_async_loop()
    future = asyncio.run_coroutine_threadsafe(coro, _async_loop)
    return future.result(timeout=timeout)

def main() -> None:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    MAILBOX.unlink(missing_ok=True)
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, accept_downloads=True, device_scale_factor=1)
        page = context.new_page()
        page.set_default_timeout(12000)
        page.on("pageerror", lambda error: js_errors.append(str(error)))
        page.on("dialog", lambda dialog: dialog.accept())

        # Public entry, registration, email verification and authentication.
        page.goto(FRONTEND + "/welcome", wait_until="networkidle")
        assert page.get_by_role("heading", name=re.compile("Understand the market")).is_visible()
        shot(page, "00-public-homepage.png")
        page.get_by_role("link", name="Create workspace", exact=True).click()
        page.get_by_label("Organization name").wait_for()
        shot(page, "01-registration-form.png")
        input_field(page, "Organization name").fill(ORGANIZATION)
        input_field(page, "Your full name").fill(FULL_NAME)
        input_field(page, "Work email").fill(EMAIL)
        input_field(page, "Password").fill(PASSWORD)
        mail_start = len(mailbox())
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/register") and r.request.method == "POST") as reg:
            page.get_by_role("button", name=re.compile("Create workspace")).click()
        assert reg.value.status == 201, reg.value.text()
        assert reg.value.json()["email_verification_required"] is True
        page.get_by_role("heading", name="Verification required").wait_for()
        shot(page, "02-verification-email-sent.png")
        _, verify_body = wait_email("Verify your Nexora account", EMAIL, mail_start)
        verify_url = email_link(verify_body, "verify-email")
        assert urlparse(verify_url).path.endswith("/verify-email")
        page.goto(verify_url, wait_until="networkidle")
        shot(page, "03-email-verification-page.png")
        with page.expect_response(lambda r: "/v1/auth/verify-email?" in r.url and r.request.method == "GET") as verify:
            page.get_by_role("button", name=re.compile("Verify email")).click()
        assert verify.value.status == 200, verify.value.text()
        page.get_by_role("link", name="Continue to sign in", exact=True).wait_for()
        shot(page, "04-email-verified.png")
        page.get_by_role("link", name="Continue to sign in", exact=True).click()
        page.get_by_label("Work email").wait_for()
        shot(page, "05-login.png")
        login_ui(page, EMAIL, PASSWORD)
        shot(page, "06-dashboard-empty-workspace.png")
        me = api_get(page, "/v1/auth/me")
        client_id = uuid.UUID(me["client_id"])
        assert me["role"] == "ORG_ADMIN"

        # Competitor creation/edit and server-side duplicate guard.
        page.get_by_role("link", name="Competitors", exact=True).click()
        page.get_by_role("heading", name="Competitors", exact=True).last.wait_for()
        shot(page, "07-competitors-empty.png")
        page.get_by_role("button", name="Add competitor", exact=True).click()
        input_field(page, "Name").fill(COMPETITOR)
        input_field(page, "Domain").fill("cdn.jsdelivr.net")
        with page.expect_response(lambda r: r.url.endswith("/v1/competitors") and r.request.method == "POST") as create_comp:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert create_comp.value.status == 201, create_comp.value.text()
        competitor_id = create_comp.value.json()["id"]
        page.get_by_text(COMPETITOR, exact=True).wait_for()
        shot(page, "08-competitor-created.png")
        page.get_by_role("button", name="Add competitor", exact=True).click()
        input_field(page, "Name").fill("Duplicate Retail Reference")
        input_field(page, "Domain").fill("cdn.jsdelivr.net")
        with page.expect_response(lambda r: r.url.endswith("/v1/competitors") and r.request.method == "POST") as duplicate:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert duplicate.value.status == 403, duplicate.value.text()
        page.get_by_text("A competitor with this domain already exists.").wait_for()
        shot(page, "09-duplicate-domain-rejected.png")
        page.get_by_role("button", name="Cancel", exact=True).click()
        row = page.locator("tbody tr").filter(has_text=COMPETITOR).first
        row.locator("button").first.click()
        input_field(page, "Name").fill("Retail Product Reference")
        with page.expect_response(lambda r: r.url.endswith(f"/v1/competitors/{competitor_id}") and r.request.method == "PATCH") as edit_comp:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert edit_comp.value.status == 200, edit_comp.value.text()
        competitor_name = "Retail Product Reference"
        assert any(x["id"] == competitor_id and x["name"] == competitor_name for x in api_get(page, "/v1/competitors"))

        # Source create, advanced configuration and edit read-back.
        page.get_by_role("link", name="Sources", exact=True).click()
        page.get_by_role("heading", name="Sources", exact=True).last.wait_for()
        page.get_by_role("button", name="Add source", exact=True).click()
        choose(page, "Competitor", competitor_name)
        input_field(page, "Source name").fill(SOURCE)
        input_field(page, "Base URL").fill(HIGH_URL)
        choose(page, "Source type", "OFFICIAL_STORE")
        choose(page, "Collection method", "HTTP_FAST")
        shot(page, "10-source-creation-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/sources") and r.request.method == "POST") as create_source:
            page.get_by_role("button", name="Create source", exact=True).click()
        assert create_source.value.status == 201, create_source.value.text()
        source_id = create_source.value.json()["id"]
        page.get_by_text(SOURCE, exact=True).wait_for()
        shot(page, "11-sources-created.png")
        page.get_by_title("Configuration", exact=True).click()
        input_field(page, "Rate / minute").fill("60")
        input_field(page, "Delay seconds").fill("0.1")
        input_field(page, "Timeout seconds").fill("25")
        input_field(page, "Max retries").fill("1")
        page.get_by_label("Custom headers (JSON)").fill('{"Accept-Language":"en-US,en;q=0.9"}')
        page.get_by_label("Extraction selectors (JSON)").fill("{}")
        shot(page, "12-source-configuration.png")
        with page.expect_response(lambda r: r.url.endswith(f"/v1/sources/{source_id}/configuration") and r.request.method == "PATCH") as config:
            page.get_by_role("button", name="Save configuration", exact=True).click()
        assert config.value.status == 200, config.value.text()
        config_saved = api_get(page, f"/v1/sources/{source_id}")
        assert config_saved["configuration"]["rate_limit_rpm"] == 60
        assert config_saved["configuration"]["max_retries"] == 1
        page.get_by_title("Edit source", exact=True).click()
        source_name = SOURCE + " (Structured)"
        input_field(page, "Source name").fill(source_name)
        with page.expect_response(lambda r: r.url.endswith(f"/v1/sources/{source_id}") and r.request.method == "PATCH") as edit_source:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert edit_source.value.status == 200, edit_source.value.text()
        page.get_by_text(source_name, exact=True).wait_for()
        shot(page, "13-source-configuration-saved.png")

        # Catalog create/detail/edit/monitoring, attributes, schema and bulk operations.
        page.get_by_role("link", name="Offerings", exact=True).click()
        page.get_by_role("heading", name="Offerings", exact=True).last.wait_for()
        page.get_by_role("button", name="Add offering", exact=True).click()
        input_field(page, "Name").fill(OFFERING)
        choose(page, "Offering type", "PRODUCT")
        input_field(page, "SKU").fill("WH1000XM5-BLK")
        input_field(page, "Current price").fill("449.99")
        input_field(page, "Currency").fill("USD")
        input_field(page, "Market").fill("US")
        input_field(page, "Category").fill("Electronics > Audio")
        input_field(page, "Product URL").fill("https://www.sony.com/electronics/headband-headphones/wh-1000xm5")
        page.get_by_label("Description").fill("Wireless over-ear headphones with active noise cancellation and multipoint Bluetooth.")
        page.get_by_label("Dynamic attributes (JSON)").fill('{"brand":"Sony","color":"Black","battery_life_hours":30,"noise_cancellation":true}')
        shot(page, "14-offering-creation-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/offerings") and r.request.method == "POST") as create_offering:
            page.get_by_role("button", name="Create offering", exact=True).click()
        assert create_offering.value.status == 201, create_offering.value.text()
        offering_id = create_offering.value.json()["id"]
        page.get_by_text(OFFERING, exact=True).wait_for()
        shot(page, "15-catalog-offering-created.png")
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        row.get_by_role("button", name=OFFERING, exact=True).click()
        page.get_by_text("CURRENT PRICE", exact=True).wait_for()
        shot(page, "16-offering-detail-and-history.png")
        page.keyboard.press("Escape")
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        row.get_by_title("Edit", exact=True).click()
        input_field(page, "Current price").fill("429.99")
        with page.expect_response(lambda r: r.url.endswith(f"/v1/offerings/{offering_id}") and r.request.method == "PATCH") as edit_offering:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert edit_offering.value.status == 200, edit_offering.value.text()
        assert float(api_get(page, f"/v1/offerings/{offering_id}")["current_price"]) == 429.99
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r: r.url.endswith(f"/v1/offerings/{offering_id}/toggle-monitoring") and r.request.method == "POST") as pause:
            row.get_by_title("Toggle monitoring", exact=True).click()
        assert pause.value.status == 200
        assert api_get(page, f"/v1/offerings/{offering_id}")["is_monitored"] is False
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r: r.url.endswith(f"/v1/offerings/{offering_id}/toggle-monitoring") and r.request.method == "POST") as resume:
            row.get_by_title("Toggle monitoring", exact=True).click()
        assert resume.value.status == 200
        assert api_get(page, f"/v1/offerings/{offering_id}")["is_monitored"] is True
        shot(page, "17-catalog-monitoring-active.png")

        page.get_by_role("button", name="Dynamic fields", exact=True).click()
        page.get_by_text("Dynamic field definitions", exact=True).wait_for()
        shot(page, "18-dynamic-fields.png")
        page.get_by_role("button", name="Add field", exact=True).click()
        input_field(page, "Machine name").fill("review_cycle_months")
        input_field(page, "Display name").fill("Review Cycle")
        input_field(page, "Data type").fill("NUMBER")
        input_field(page, "Unit").fill("months")
        input_field(page, "Category").fill("Commercial")
        shot(page, "19-dynamic-field-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/offerings/fields") and r.request.method == "POST") as create_field:
            page.get_by_role("button", name="Create field", exact=True).click()
        assert create_field.value.status == 201, create_field.value.text()
        page.get_by_text("Review Cycle", exact=True).wait_for()
        shot(page, "20-dynamic-field-created.png")
        fieldrow = page.locator("div.list-row").filter(has_text="Review Cycle").last
        with page.expect_response(lambda r: "/v1/offerings/fields/" in r.url and r.request.method == "DELETE") as delete_field:
            fieldrow.locator("button.danger-icon").click()
        assert delete_field.value.status == 204, delete_field.value.text()
        page.keyboard.press("Escape")

        page.get_by_role("button", name="Bulk import", exact=True).click()
        payload = [
            {"name":"Sony ULT WEAR Wireless Headphones","offering_type":"PRODUCT","sku":"ULTWEAR-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/headband-headphones/ult-wear","category":"Electronics > Audio","attributes":{"brand":"Sony","color":"Black"}},
            {"name":"Sony LinkBuds S","offering_type":"PRODUCT","sku":"LINKBUDS-S-BLK","current_price":"199.99","currency":"USD","market":"US","url":"https://www.sony.com/electronics/truly-wireless/linkbuds-s","category":"Electronics > Audio","attributes":{"brand":"Sony","fit":"In-ear"}}
        ]
        page.get_by_label("Offering JSON").fill(json.dumps(payload))
        shot(page, "21-bulk-import-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/offerings/bulk") and r.request.method == "POST") as bulk:
            page.get_by_role("button", name="Import offerings", exact=True).click()
        assert bulk.value.status == 200, bulk.value.text()
        assert bulk.value.json()["successful_count"] == 2, bulk.value.text()
        page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).wait_for()
        shot(page, "22-bulk-imported-catalog.png")
        csv_path, json_path = Path("/tmp/nexora-catalog.csv"), Path("/tmp/nexora-catalog.json")
        with page.expect_download(timeout=15000) as csvdl:
            page.get_by_role("button", name="CSV", exact=True).click()
        csvdl.value.save_as(str(csv_path))
        assert csv_path.is_file() and csv_path.stat().st_size > 0
        with page.expect_download(timeout=15000) as jsondl:
            page.get_by_role("button", name="JSON", exact=True).click()
        jsondl.value.save_as(str(json_path))
        assert json_path.is_file() and json_path.stat().st_size > 0
        page.get_by_placeholder("Search name, SKU, category…").fill("Sony ULT WEAR")
        page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).wait_for()
        page.get_by_label("Select Sony ULT WEAR Wireless Headphones", exact=True).check()
        with page.expect_response(lambda r: r.url.endswith("/v1/offerings/bulk-archive") and r.request.method == "POST") as archive:
            page.get_by_role("button", name="Archive 1", exact=True).click()
        assert archive.value.status == 200, archive.value.text()
        assert archive.value.json()["archived_count"] == 1
        assert page.get_by_text("Sony ULT WEAR Wireless Headphones", exact=True).count() == 0
        archived = api_get(page, "/v1/offerings?q=Sony%20ULT%20WEAR&include_archived=true&page=1&page_size=20")
        assert any(x["is_archived"] for x in archived["items"])
        page.get_by_placeholder("Search name, SKU, category…").fill("")
        page.get_by_text(OFFERING, exact=True).wait_for()
        shot(page, "23-catalog-import-export-and-archive.png")

        # Create match and collect the first real price observation.
        page.get_by_role("link", name="Matches", exact=True).click()
        page.get_by_role("heading", name="Offering matches", exact=True).last.wait_for()
        page.get_by_role("button", name="Add match", exact=True).click()
        choose(page, "Offering", OFFERING)
        choose(page, "Source", source_name)
        input_field(page, "Competitor target URL").fill(HIGH_URL)
        choose(page, "Status", "APPROVED")
        input_field(page, "Confidence (0–1)").fill("0.98")
        shot(page, "24-offering-match-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/offering-matches") and r.request.method == "POST") as create_match:
            page.get_by_role("button", name="Create match", exact=True).click()
        assert create_match.value.status == 201, create_match.value.text()
        match_id = create_match.value.json()["id"]
        page.locator("tbody tr").filter(has_text=OFFERING).first.locator("a").wait_for()
        shot(page, "25-offering-match-created.png")
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r: "/v1/collections/run" in r.url and r.request.method == "POST") as first_collection:
            row.get_by_title("Run collection", exact=True).click()
        assert first_collection.value.status in (200, 201), first_collection.value.text()
        first = first_collection.value.json()
        assert first["status"] == "COMPLETED", first
        assert first["observation"]["price"] == "399.99", first
        assert first["observation"]["http_status_code"] == 200, first
        assert len(api_get(page, f"/v1/offerings/{offering_id}/history")) >= 1
        shot(page, "26-first-price-observation.png")

        # Alert rule + lower second observation => alert log + email outbox delivery.
        page.get_by_role("link", name="Alerts", exact=True).click()
        page.get_by_role("heading", name="Alerts", exact=True).last.wait_for()
        page.get_by_role("button", name="New rule", exact=True).click()
        input_field(page, "Rule name").fill("Sony retail price drop")
        choose(page, "Alert type", "PERCENTAGE_DROP")
        choose(page, "Offering scope", OFFERING)
        input_field(page, "Threshold").fill("10")
        input_field(page, "Cooldown (minutes)").fill("60")
        shot(page, "27-alert-rule-form.png")
        with page.expect_response(lambda r: r.url.endswith("/v1/alerts/rules") and r.request.method == "POST") as rule:
            page.get_by_role("button", name="Create rule", exact=True).click()
        assert rule.value.status == 201, rule.value.text()
        rule_id = rule.value.json()["id"]
        page.get_by_text("Sony retail price drop", exact=True).wait_for()
        shot(page, "28-alert-rule-created.png")

        page.get_by_role("link", name="Matches", exact=True).click()
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        row.get_by_title("Edit", exact=True).click()
        input_field(page, "Competitor target URL").fill(LOW_URL)
        with page.expect_response(lambda r: r.url.endswith(f"/v1/offering-matches/{match_id}") and r.request.method == "PATCH") as edit_match:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert edit_match.value.status == 200, edit_match.value.text()
        row = page.locator("tbody tr").filter(has_text=OFFERING).first
        with page.expect_response(lambda r: "/v1/collections/run" in r.url and r.request.method == "POST") as second_collection:
            row.get_by_title("Run collection", exact=True).click()
        assert second_collection.value.status in (200, 201), second_collection.value.text()
        second = second_collection.value.json()
        assert second["observation"]["price"] == "349.99", second
        assert second["snapshot"]["previous_price"] == "399.99", second
        assert second["snapshot"]["percentage_difference"].startswith("-12.50%"), second

        page.get_by_role("link", name="Alerts", exact=True).click()
        page.get_by_text("Competitor price dropped", exact=True).wait_for(timeout=15000)
        logs = api_get(page, "/v1/alerts/logs")
        alert = next((x for x in logs if x["title"] == "Competitor price dropped"), None)
        assert alert and not alert["is_read"], logs
        page.get_by_title("Mark as read", exact=True).click()
        page.get_by_title("Read", exact=True).wait_for()
        assert any(x["id"] == alert["id"] and x["is_read"] for x in api_get(page, "/v1/alerts/logs"))
        shot(page, "29-alert-generated-and-read.png")

        alert_mail_start = len(mailbox())
        from backend.workers.tasks import _dispatch_pending_notifications
        sent_count = run_async(_dispatch_pending_notifications())
        assert int(sent_count) >= 1, {"sent": sent_count}
        _, alert_body = wait_email("Nexora Competitive Alert: Competitor price dropped", EMAIL, alert_mail_start)
        assert "Nexora detected a competitive intelligence event" in alert_body
        assert "SENT" in run_async(sent_statuses(client_id))

        page.get_by_role("link", name="Jobs", exact=True).click()
        page.get_by_role("heading", name="Jobs", exact=True).last.wait_for()
        page.locator("tbody tr").filter(has_text="ON DEMAND REFRESH").first.wait_for()
        shot(page, "30-collection-job-history.png")
        page.get_by_role("button", name="Details", exact=True).first.click()
        page.get_by_text("Job ID", exact=True).wait_for()
        shot(page, "31-collection-job-detail.png")
        page.keyboard.press("Escape")

        # SSRF rejection then real HTTPS schema extraction and catalog upsert.
        page.get_by_role("link", name="Discovery", exact=True).click()
        page.get_by_role("heading", name="Website discovery", exact=True).last.wait_for()
        input_field(page, "Website URL").fill("http://127.0.0.1:8000/v1/health")
        input_field(page, "Max pages").fill("1")
        with page.expect_response(lambda r: r.url.endswith("/v1/discovery/run") and r.request.method == "POST") as blocked:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        assert blocked.value.status == 422, blocked.value.text()
        shot(page, "32-private-target-blocked.png")
        input_field(page, "Website URL").fill(DISCOVERY_URL)
        choose(page, "Default type", "PRODUCT")
        with page.expect_response(lambda r: r.url.endswith("/v1/discovery/run") and r.request.method == "POST") as discovery:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        assert discovery.value.status == 200, discovery.value.text()
        discovered = discovery.value.json()
        assert discovered["status"] == "COMPLETED", discovered
        assert discovered["created_offerings_count"] == 1, discovered
        assert discovered["items"][0]["name"] == DISCOVERED, discovered
        page.get_by_text(DISCOVERED, exact=True).wait_for(timeout=15000)
        shot(page, "33-discovery-product-created.png")
        discovery_readback = api_get(page, f"/v1/discovery/jobs/{discovered['job_id']}")
        assert discovery_readback["items"][0]["sku"] == "WF1000XM5-BLK"
        with page.expect_response(lambda r: r.url.endswith("/v1/discovery/run") and r.request.method == "POST") as discovery_again:
            page.get_by_role("button", name="Run discovery", exact=True).click()
        assert discovery_again.value.status == 200, discovery_again.value.text()
        repeat = discovery_again.value.json()
        assert repeat["created_offerings_count"] == 0 and repeat["updated_offerings_count"] == 1, repeat
        query_result = api_get(page, "/v1/offerings?q=Sony%20WF-1000XM5&page=1&page_size=20")
        assert sum(x["sku"] == "WF1000XM5-BLK" for x in query_result["items"]) == 1
        shot(page, "34-discovery-upsert-history.png")

        # Profile changes, password change, reset-token email and re-login.
        page.locator("button.profile-trigger").click()
        page.get_by_text("Account settings", exact=True).click()
        page.get_by_role("heading", name="Settings", exact=True).last.wait_for()
        page.get_by_label("Organization name").wait_for()
        shot(page, "35-workspace-settings.png")
        input_field(page, "Company name").fill("Northstar Analytics")
        input_field(page, "Country").fill("US")
        input_field(page, "Default currency").fill("USD")
        input_field(page, "Market").fill("US")
        input_field(page, "Industry").fill("Consumer Electronics")
        input_field(page, "Timezone").fill("America/New_York")
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/profile") and r.request.method == "PATCH") as profile:
            page.get_by_role("button", name="Save profile", exact=True).click()
        assert profile.value.status == 200, profile.value.text()
        assert api_get(page, "/v1/auth/profile")["company_name"] == "Northstar Analytics"
        shot(page, "36-workspace-profile-updated.png")
        input_field(page, "Current password").fill(PASSWORD)
        input_field(page, "New password").fill(CHANGED_PASSWORD)
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/change-password") and r.request.method == "POST") as pw_change:
            page.get_by_role("button", name="Update password", exact=True).click()
        assert pw_change.value.status == 200, pw_change.value.text()
        assert api_post(page, "/v1/auth/login", {"email": EMAIL, "password": PASSWORD}).status == 401
        assert api_post(page, "/v1/auth/login", {"email": EMAIL, "password": CHANGED_PASSWORD}).status == 200
        shot(page, "37-password-changed.png")

        logout_ui(page)
        page.get_by_role("link", name="Forgot password?", exact=True).click()
        page.get_by_role("heading", name="Reset access without losing your workspace.", exact=True).wait_for()
        reset_email_input = input_field(page, "Work email")
        reset_email_input.fill(EMAIL)
        assert reset_email_input.input_value() == EMAIL, "Password-reset email was not populated in the form."
        reset_mail_start = len(mailbox())
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/forgot-password") and r.request.method == "POST") as forgot:
            page.get_by_role("button", name="Send reset link", exact=True).click()
        assert forgot.value.status == 200, forgot.value.text()
        page.get_by_role("heading", name="Check your inbox", exact=True).last.wait_for()
        shot(page, "38-password-reset-requested.png")
        _, reset_body = wait_email("Reset your Nexora password", EMAIL, reset_mail_start)
        reset_url = email_link(reset_body, "reset-password")
        page.goto(reset_url, wait_until="networkidle")
        input_field(page, "New password").wait_for()
        shot(page, "39-password-reset-form.png")
        input_field(page, "New password").fill(RESET_PASSWORD)
        with page.expect_response(lambda r: r.url.endswith("/v1/auth/reset-password") and r.request.method == "POST") as reset:
            page.get_by_role("button", name="Update password", exact=True).click()
        assert reset.value.status == 200, reset.value.text()
        page.get_by_role("heading", name="Password updated", exact=True).last.wait_for()
        shot(page, "40-password-reset-complete.png")
        page.get_by_role("link", name="Continue to sign in", exact=True).click()
        login_ui(page, EMAIL, RESET_PASSWORD)
        shot(page, "41-dashboard-after-password-reset.png")

        # Verify observations, snapshot, alert, discovered item, jobs and outbox directly in PostgreSQL.
        run_async(assert_persisted_market_state(
            client_id, uuid.UUID(offering_id), uuid.UUID(match_id), uuid.UUID(rule_id)
        ))

        # Exercise the rest of alert-rule management through the real UI.
        page.get_by_role("link", name="Alerts", exact=True).click()
        rule_row = page.locator("div.list-row").filter(has_text="Sony retail price drop").first
        rule_row.get_by_title("Edit rule", exact=True).click()
        edit_rule_dialog = page.get_by_role("dialog", name="Edit alert rule", exact=True)
        edit_rule_dialog.get_by_role("spinbutton", name="Threshold", exact=True).fill("15")
        with page.expect_response(lambda r: r.url.endswith(f"/v1/alerts/rules/{rule_id}") and r.request.method == "PATCH") as rule_edit:
            page.get_by_role("button", name="Save changes", exact=True).click()
        assert rule_edit.value.status == 200, rule_edit.value.text()
        rules = api_get(page, "/v1/alerts/rules")
        assert next(row for row in rules if row["id"] == rule_id)["threshold_value"] == 15

        rule_row = page.locator("div.list-row").filter(has_text="Sony retail price drop").first
        with page.expect_response(lambda r: r.url.endswith(f"/v1/alerts/rules/{rule_id}") and r.request.method == "PATCH") as rule_pause:
            rule_row.get_by_title("Pause rule", exact=True).click()
        assert rule_pause.value.status == 200 and rule_pause.value.json()["is_active"] is False
        rule_row = page.locator("div.list-row").filter(has_text="Sony retail price drop").first
        with page.expect_response(lambda r: r.url.endswith(f"/v1/alerts/rules/{rule_id}") and r.request.method == "PATCH") as rule_activate:
            rule_row.get_by_title("Activate rule", exact=True).click()
        assert rule_activate.value.status == 200 and rule_activate.value.json()["is_active"] is True
        rule_row = page.locator("div.list-row").filter(has_text="Sony retail price drop").first
        with page.expect_response(lambda r: r.url.endswith(f"/v1/alerts/rules/{rule_id}") and r.request.method == "DELETE") as rule_delete:
            rule_row.get_by_title("Delete rule", exact=True).click()
        assert rule_delete.value.status == 204, rule_delete.value.text()
        assert all(row["id"] != rule_id for row in api_get(page, "/v1/alerts/rules"))

        # Persistent users, actual issued JWTs, UI restrictions and server permission checks.
        viewer_email = run_async(add_role_user(client_id, RoleEnum.VIEWER))
        analyst_email = run_async(add_role_user(client_id, RoleEnum.ANALYST))
        super_admin_email = run_async(add_role_user(client_id, RoleEnum.SUPER_ADMIN))
        logout_ui(page)
        login_ui(page, analyst_email, ROLE_PASSWORD)
        page.get_by_role("link", name="Competitors", exact=True).click()
        page.get_by_role("heading", name="Competitors", exact=True).last.wait_for()
        assert page.get_by_role("button", name="Add competitor", exact=True).count() == 0
        denied = api_post(page, "/v1/competitors",
            {"name": "Not Allowed", "domain": "forbidden.example"},
            {"Authorization": f"Bearer {token(page)}"})
        assert denied.status == 403, denied.text()
        page.get_by_role("link", name="Discovery", exact=True).click()
        assert page.get_by_role("button", name="Run discovery", exact=True).is_visible()
        shot(page, "42-analyst-workspace.png")

        logout_ui(page)
        login_ui(page, viewer_email, ROLE_PASSWORD)
        page.get_by_role("link", name="Offerings", exact=True).click()
        page.get_by_role("heading", name="Offerings", exact=True).last.wait_for()
        assert page.get_by_role("button", name="Add offering", exact=True).count() == 0
        assert page.get_by_role("button", name="Bulk import", exact=True).count() == 0
        assert page.get_by_role("button", name="Dynamic fields", exact=True).count() == 0
        viewer_read = page.request.get(API + "/v1/offerings", headers={"Authorization": f"Bearer {token(page)}"})
        assert viewer_read.status == 200, viewer_read.text()
        viewer_write = api_post(page, "/v1/competitors",
            {"name": "Viewer Write Attempt", "domain": "viewer-write.example"},
            {"Authorization": f"Bearer {token(page)}"})
        assert viewer_write.status == 403, viewer_write.text()
        shot(page, "43-viewer-read-only-workspace.png")

        # Platform-super-admin role remains available and is authorized by the server.
        logout_ui(page)
        login_ui(page, super_admin_email, ROLE_PASSWORD)
        page.get_by_role("link", name="Competitors", exact=True).click()
        page.get_by_role("heading", name="Competitors", exact=True).last.wait_for()
        assert page.get_by_role("button", name="Add competitor", exact=True).is_visible()
        super_domain = "superadmin-" + client_id.hex[:10] + ".example.com"
        page.get_by_role("button", name="Add competitor", exact=True).click()
        page.get_by_label("Name").fill("Super Admin Verification")
        page.get_by_label("Domain").fill(super_domain)
        with page.expect_response(lambda r: r.url.endswith("/v1/competitors") and r.request.method == "POST") as super_create:
            page.get_by_role("button", name="Save competitor", exact=True).click()
        assert super_create.value.status == 201, super_create.value.text()
        super_competitor_id = super_create.value.json()["id"]
        page.get_by_text("Super Admin Verification", exact=True).wait_for()
        shot(page, "44-super-admin-workspace.png")
        super_row = page.locator("tbody tr").filter(has_text="Super Admin Verification").first
        with page.expect_response(lambda r: r.url.endswith(f"/v1/competitors/{super_competitor_id}") and r.request.method == "DELETE") as super_delete:
            super_row.locator("button.danger-icon").click()
        assert super_delete.value.status == 204, super_delete.value.text()
        assert all(row["id"] != super_competitor_id for row in api_get(page, "/v1/competitors"))

        mobile_context = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=1)
        mobile = mobile_context.new_page()
        mobile.goto(FRONTEND + "/welcome", wait_until="networkidle")
        dimensions = mobile.evaluate("() => ({viewport:document.documentElement.clientWidth,content:document.documentElement.scrollWidth})")
        assert dimensions["content"] <= dimensions["viewport"], dimensions
        shot(mobile, "45-mobile-homepage.png")
        mobile_context.close()

        if js_errors: raise AssertionError("JavaScript errors: " + " | ".join(js_errors))
        expected = [
            "00-public-homepage.png","01-registration-form.png","02-verification-email-sent.png",
            "03-email-verification-page.png","04-email-verified.png","05-login.png","06-dashboard-empty-workspace.png",
            "07-competitors-empty.png","08-competitor-created.png","09-duplicate-domain-rejected.png",
            "10-source-creation-form.png","11-sources-created.png","12-source-configuration.png","13-source-configuration-saved.png",
            "14-offering-creation-form.png","15-catalog-offering-created.png","16-offering-detail-and-history.png",
            "17-catalog-monitoring-active.png","18-dynamic-fields.png","19-dynamic-field-form.png","20-dynamic-field-created.png",
            "21-bulk-import-form.png","22-bulk-imported-catalog.png","23-catalog-import-export-and-archive.png",
            "24-offering-match-form.png","25-offering-match-created.png","26-first-price-observation.png",
            "27-alert-rule-form.png","28-alert-rule-created.png","29-alert-generated-and-read.png",
            "30-collection-job-history.png","31-collection-job-detail.png","32-private-target-blocked.png",
            "33-discovery-product-created.png","34-discovery-upsert-history.png","35-workspace-settings.png",
            "36-workspace-profile-updated.png","37-password-changed.png","38-password-reset-requested.png",
            "39-password-reset-form.png","40-password-reset-complete.png","41-dashboard-after-password-reset.png",
            "42-analyst-workspace.png","43-viewer-read-only-workspace.png","44-super-admin-workspace.png","45-mobile-homepage.png"
        ]
        missing = [name for name in expected if not (SCREENSHOTS / name).is_file()]
        assert not missing, f"Missing screenshots: {missing}"
        print(f"PASSED: real UI/API/PostgreSQL browser workflow; {len(expected)} screenshots.", flush=True)
        browser.close()
        context.close()

if __name__ == "__main__":
    main()
