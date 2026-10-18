# 📸 Nexora Live Production: Aligned Before & After Visual Progression

**Live Frontend Target:** [https://nexora-frontend-hazel.vercel.app](https://nexora-frontend-hazel.vercel.app)  
**Live Backend Target:** [https://nexora-backend-5ie2.onrender.com](https://nexora-backend-5ie2.onrender.com)  
**Execution Environment:** Chromium (1440 × 900 Desktop High-DPI Viewport)  
**Data Domain:** Real Enterprise Multi-Cloud, Observability, and Retail Tech (AWS, Datadog, Snowflake, Nexora Sentinel AI)

---

## 📌 Production Notes

1. **Backend on Render Free Tier:**  
   The backend API is deployed on Render's free tier. Inactivity causes the service to sleep/spin down. The very first request can take 30–50 seconds to wake up the server. Once awake, all requests respond normally.

2. **User Registration & Email Verification:**  
   In local development, registering sends an email verification link. Because Render's free tier does not provide SMTP email delivery, registration on this live deployment is configured to activate the account directly so users can register and test immediately.

---

## Executive Summary & Alignment Schema

Every functional flow below is structured into an aligned chronological transition demonstrating:
1. **Initial Blank / Default State:** What a user sees before entering data.
2. **Real Enterprise Data Entry:** Real names, real domains, authentic pricing, valid SKUs, and configuration parameters.
3. **Populated Live State / Success:** Data committed to PostgreSQL via Render backend, active table pills, toasts, and real-time metrics.

---

## 1. Flow 1: Enterprise Workspace Registration

| State | Image Filename | Description | Live Entity Data |
| :--- | :--- | :--- | :--- |
| **Before (Blank)** | `01_register_blank.png` | Clean registration view with secure workspace boundaries | Empty Form Fields |
| **During (Filled)** | `02_register_filled.png` | Form populated with enterprise tenant credentials | `Vanguard Global Intelligence`, `Elena Vance`, `elena.vance@vanguard-intel.io` |
| **After (Success)** | `03_register_success.png` | Confirmation toast with transition prompt to secure sign-in | Tenant boundary established in PostgreSQL |

![Initial Blank Registration Form](tests/screenshots_aligned/01_register_blank.png)
*Initial Blank Registration Form*

![Registration Form Populated with Real Enterprise Identity](tests/screenshots_aligned/02_register_filled.png)
*Registration Form Populated with Real Enterprise Identity*

![Workspace Created Confirmation](tests/screenshots_aligned/03_register_success.png)
*Workspace Created Confirmation*

---

## 2. Flow 2: Authentication & Operational Dashboard

| State | Image Filename | Description | Live Entity Data |
| :--- | :--- | :--- | :--- |
| **Before (Blank)** | `04_login_blank.png` | Login screen with empty email and password inputs | Empty Form Fields |
| **During (Filled)** | `05_login_filled.png` | Login screen populated with real registered admin credentials | `elena.vance@vanguard-intel.io` |
| **After (Dashboard)**| `06_dashboard_authenticated.png` | Full authenticated Command Center with status indicators | Session token active, ORG_ADMIN badge, system metrics |

![Blank Login Interface](tests/screenshots_aligned/04_login_blank.png)
*Blank Login Interface*

![Login with Authenticated Tenant Credentials](tests/screenshots_aligned/05_login_filled.png)
*Login with Authenticated Tenant Credentials*

![Authenticated Operating Picture Dashboard](tests/screenshots_aligned/06_dashboard_authenticated.png)
*Authenticated Operating Picture Dashboard*

---

## 3. Flow 3: Competitor Network Configuration

| State | Image Filename | Description | Live Entity Data |
| :--- | :--- | :--- | :--- |
| **Before (Blank Modal)** | `07_competitor_modal_blank.png` | Add Competitor modal in default blank state | Empty Name & Domain fields |
| **During (Filled Modal)** | `08_competitor_modal_filled.png` | Modal populated with authentic enterprise competitor | `Amazon Web Services Inc` (`aws.amazon.com`) |
| **After (Populated Table)**| `09_competitors_table_populated.png` | Table displaying multi-niche enterprise competitors | `AWS`, `Datadog`, `Snowflake` with `ACTIVE` badges |
| **Action (Inline Edit)** | `10_competitor_edited.png` | Inline edit state updating entity classification | Renamed entity to `Snowflake Enterprise Cloud Corp` |

![Add Competitor Modal (Initial Blank State)](tests/screenshots_aligned/07_competitor_modal_blank.png)
*Add Competitor Modal (Initial Blank State)*

![Add Competitor Modal (Populated with AWS)](tests/screenshots_aligned/08_competitor_modal_filled.png)
*Add Competitor Modal (Populated with AWS)*

![Competitors Table (Populated Multi-Niche Real Enterprises)](tests/screenshots_aligned/09_competitors_table_populated.png)
*Competitors Table (Populated Multi-Niche Real Enterprises)*

![Competitor Table After Inline Edit](tests/screenshots_aligned/10_competitor_edited.png)
*Competitor Table After Inline Edit*

---

## 4. Flow 4: Collection Sources & Ingestion Configuration

| State | Image Filename | Description | Live Entity Data |
| :--- | :--- | :--- | :--- |
| **Before (Blank Modal)** | `11_source_modal_blank.png` | Add Source modal with unselected competitor and blank URLs | Default empty dropdown and text inputs |
| **During (Filled Modal)** | `12_source_modal_filled.png` | Source populated with real enterprise pricing endpoint | `AWS EC2 Infrastructure Pricing Feed` (`https://aws.amazon.com/ec2/pricing`) |
| **After (Populated Table)**| `13_sources_table_populated.png` | Sources table showing multiple live collection endpoints | `AWS EC2`, `Datadog Pro Feed`, `Snowflake Catalog` (`HEALTHY`, `CLOSED`) |
| **Action (Config Modal)** | `14_source_config_modal.png` | Technical configuration for rate limits, headers, and DOM selectors | `45 RPM`, `1.5s delay`, custom headers, custom extraction JSON |

![Add Collection Source Modal (Blank State)](tests/screenshots_aligned/11_source_modal_blank.png)
*Add Collection Source Modal (Blank State)*

![Add Collection Source Modal (Populated with AWS Feed)](tests/screenshots_aligned/12_source_modal_filled.png)
*Add Collection Source Modal (Populated with AWS Feed)*

![Collection Sources Table (Populated Multi-Source Endpoints)](tests/screenshots_aligned/13_sources_table_populated.png)
*Collection Sources Table (Populated Multi-Source Endpoints)*

![Source Ingestion Parameters Modal (Rate Limit & Selectors)](tests/screenshots_aligned/14_source_config_modal.png)
*Source Ingestion Parameters Modal (Rate Limit & Selectors)*

---

## 5. Flow 5: Offerings Catalog, Dynamic Schema & Telemetry

| State | Image Filename | Description | Live Entity Data |
| :--- | :--- | :--- | :--- |
| **Before (Blank Modal)** | `15_offering_modal_blank.png` | Add Catalog Offering modal in blank state | Empty name, SKU, price, and category |
| **During (Filled Modal)** | `16_offering_modal_filled.png` | Populated offering modal with real enterprise product | `Nexora Sentinel AI Monitor`, SKU: `NXR-SNT-8800-PRO`, `$2,499.00` |
| **After (Populated Table)**| `17_offerings_catalog_populated.png` | Populated catalog table showing enterprise cloud products | `Nexora Global Merchant ($1,299)`, `Multi-Cloud Fabric ($4,850)`, `Sentinel AI ($2,499)` |
| **Action (Dynamic Schema)**| `18_dynamic_field_modal.png` | Dynamic custom schema field definition modal | Custom field: `compliance_tier_rating` |
| **Action (Telemetry Modal)**| `19_offering_telemetry_modal.png` | Detail modal showing live pricing telemetry and metrics | Historical benchmark comparisons and price history |
| **Action (Monitor Toggle)** | `20_monitoring_toggled.png` | Active monitoring status toggle interaction | State transitioned from PAUSED to MONITORED |
| **Action (Filter Search)** | `21_catalog_filtered.png` | Dynamic client-side search filtering catalog table | Real-time search query for "Sentinel" |

![Add Catalog Offering Modal (Blank State)](tests/screenshots_aligned/15_offering_modal_blank.png)
*Add Catalog Offering Modal (Blank State)*

![Add Catalog Offering Modal (Populated Real Product Data)](tests/screenshots_aligned/16_offering_modal_filled.png)
*Add Catalog Offering Modal (Populated Real Product Data)*

![Offerings Catalog Table (Populated Real Enterprise Products)](tests/screenshots_aligned/17_offerings_catalog_populated.png)
*Offerings Catalog Table (Populated Real Enterprise Products)*

![Dynamic Field Definition Modal (Custom Schema Attribute)](tests/screenshots_aligned/18_dynamic_field_modal.png)
*Dynamic Field Definition Modal (Custom Schema Attribute)*

![Offering Detail Modal (Live Telemetry & Price Comparison)](tests/screenshots_aligned/19_offering_telemetry_modal.png)
*Offering Detail Modal (Live Telemetry & Price Comparison)*

![Offering Monitoring Toggled (Active Collection Monitoring Pill)](tests/screenshots_aligned/20_monitoring_toggled.png)
*Offering Monitoring Toggled (Active Collection Monitoring Pill)*

![Offerings Catalog Filtered (Real-Time Search for 'Sentinel')](tests/screenshots_aligned/21_catalog_filtered.png)
*Offerings Catalog Filtered (Real-Time Search for 'Sentinel')*

---

## 6. Flow 6: Benchmark Matches & Real-Time Collection Run

| State | Image Filename | Description | Live Entity Data |
| :--- | :--- | :--- | :--- |
| **Before (Blank Modal)** | `22_match_modal_blank.png` | Map Offering Match modal in unconfigured blank state | Default unselected dropdowns and empty URL |
| **During (Filled Modal)** | `23_match_modal_filled.png` | Pairing internal offering to competitor product target | `Datadog Infrastructure Pricing`, `0.95` confidence |
| **After (Populated Table)**| `24_matches_table_populated.png` | Offering Matches table displaying live pairings | `Nexora Merchant Engine` $\leftrightarrow$ `Datadog` (`100%`, `APPROVED`) |
| **Action (Trigger Run)** | `25_collection_run_active.png` | Live collection run triggered directly from row action | Execution spinner active, dispatching scraper job |

![Map Offering Match Modal (Blank State)](tests/screenshots_aligned/22_match_modal_blank.png)
*Map Offering Match Modal (Blank State)*

![Map Offering Match Modal (Populated Real Competitor Pairing)](tests/screenshots_aligned/23_match_modal_filled.png)
*Map Offering Match Modal (Populated Real Competitor Pairing)*

![Offering Matches Table (Populated Live Benchmark Pairing)](tests/screenshots_aligned/24_matches_table_populated.png)
*Offering Matches Table (Populated Live Benchmark Pairing)*

![Collection Run Triggered (Live Benchmark Execution Active)](tests/screenshots_aligned/25_collection_run_active.png)
*Collection Run Triggered (Live Benchmark Execution Active)*

---

## 7. Flow 7: Website Discovery Scan Engine

| State | Image Filename | Description | Live Entity Data |
| :--- | :--- | :--- | :--- |
| **Before (Blank Form)** | `26_discovery_form_blank.png` | Website Discovery Engine with blank target URL input | Default crawler configuration |
| **During (Filled Form)** | `27_discovery_form_filled.png` | Form populated with live public storefront target | `https://www.datadoghq.com/pricing`, `5 pages`, `PRODUCT` type |
| **After (Scan Active)** | `28_discovery_results_live.png` | Real-time crawl telemetry and candidate discovery | Discovery scanner active, evaluating DOM structure |

![Website Discovery Engine (Initial Blank State)](tests/screenshots_aligned/26_discovery_form_blank.png)
*Website Discovery Engine (Initial Blank State)*

![Website Discovery Engine (Populated Real Target Storefront)](tests/screenshots_aligned/27_discovery_form_filled.png)
*Website Discovery Engine (Populated Real Target Storefront)*

![Website Discovery Scan Active (Scanning Storefront)](tests/screenshots_aligned/28_discovery_results_live.png)
*Website Discovery Scan Active (Scanning Storefront)*

---

## 8. Flow 8: Background Jobs Queue Telemetry

| State | Image Filename | Description | Live Entity Data |
| :--- | :--- | :--- | :--- |
| **Telemetry State** | `29_jobs_telemetry_queue.png` | Real-time job execution queue showing task states | Ingestion jobs, execution durations, and processed item counters |

![Background Jobs Queue (Real-Time Telemetry & Metrics)](tests/screenshots_aligned/29_jobs_telemetry_queue.png)
*Background Jobs Queue (Real-Time Telemetry & Metrics)*

---

## 9. Flow 9: Market Intelligence Alerts & Rules

| State | Image Filename | Description | Live Entity Data |
| :--- | :--- | :--- | :--- |
| **Before (Blank Modal)** | `30_alert_modal_blank.png` | Add Alert Rule modal in initial unconfigured state | Default rule template |
| **During (Filled Modal)** | `31_alert_modal_filled.png` | Populated rule with real percentage price drop threshold | `Datadog Pro Realtime Price Drop 10%`, threshold: `10%` |
| **After (Populated Table)**| `32_alerts_table_populated.png` | Alerts dashboard showing active monitoring rule | `ACTIVE` rule, `PERCENTAGE DROP · 10%`, 0 unread alerts |

![Add Alert Rule Modal (Blank State)](tests/screenshots_aligned/30_alert_modal_blank.png)
*Add Alert Rule Modal (Blank State)*

![Add Alert Rule Modal (Populated Real Drop Threshold 10%)](tests/screenshots_aligned/31_alert_modal_filled.png)
*Add Alert Rule Modal (Populated Real Drop Threshold 10%)*

![Alerts & Event Log View (Active Alert Rules Configured)](tests/screenshots_aligned/32_alerts_table_populated.png)
*Alerts & Event Log View (Active Alert Rules Configured)*

---

## 10. Flow 10: Workspace Identity & Tenant Settings

| State | Image Filename | Description | Live Entity Data |
| :--- | :--- | :--- | :--- |
| **Populated Settings** | `33_settings_profile_populated.png` | Tenant workspace settings updated with corporate entity | `Vanguard Global Intelligence Systems Inc`, `Cloud Intelligence & Observability` |

![Workspace Settings (Populated Enterprise Tenant Profile)](tests/screenshots_aligned/33_settings_profile_populated.png)
*Workspace Settings (Populated Enterprise Tenant Profile)*

---

## Summary of Test Results

- **Total Synchronized Flows Executed:** 10
- **Total Aligned High-Resolution Screenshots Captured:** 33
- **Live Production URL:** [https://nexora-frontend-hazel.vercel.app](https://nexora-frontend-hazel.vercel.app)  
- **All Screenshots Stored at:** `tests/screenshots_aligned/`
