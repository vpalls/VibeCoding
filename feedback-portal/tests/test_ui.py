"""
Customer Feedback Portal – Selenium UI Test Suite
==================================================

26 test cases across two suites:
  Suite 1 (TC_F01–TC_F11)  – Customer Feedback Submission Page  (port 5000 /)
  Suite 2 (TC_A01–TC_A15)  – Admin Response Dashboard           (port 5000 /admin)

Prerequisites
─────────────
  pip install selenium webdriver-manager

Both servers must be running BEFORE executing:
  Terminal 1 (feedback-portal/backend/):
      uvicorn main:app --reload --port 8000

  Terminal 2 (feedback-portal/frontend/):
      python app.py

Run
───
  cd feedback-portal
  python tests/test_ui.py

Results are written to:
  tests/TestResults_YYYYMMDD_HHMMSS.txt
"""

import re
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

try:
    from webdriver_manager.chrome import ChromeDriverManager
    _USE_WDM = True
except ImportError:
    _USE_WDM = False

# ── Configuration ──────────────────────────────────────────────────────────
BASE_URL     = "http://localhost:5000"
WAIT_TIMEOUT = 12   # seconds per explicit wait


# ── Helpers ────────────────────────────────────────────────────────────────

def _make_driver() -> webdriver.Chrome:
    """Return a visible Chrome WebDriver instance."""
    opts = Options()
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--log-level=3")           # suppress console noise
    if _USE_WDM:
        svc = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=svc, options=opts)
    return webdriver.Chrome(options=opts)


class _Tee:
    """Write simultaneously to multiple streams (console + file)."""

    def __init__(self, *streams):
        self._streams = streams

    def write(self, data: str):
        for s in self._streams:
            s.write(data)

    def flush(self):
        for s in self._streams:
            s.flush()


# ══════════════════════════════════════════════════════════════════════════
# Suite 1 – Customer Feedback Submission Page
# ══════════════════════════════════════════════════════════════════════════

class TestFeedbackPage(unittest.TestCase):
    """
    Validates the customer-facing feedback form at GET/POST /.

    TC_F01  Page loads without errors
    TC_F02  <title> contains 'Feedback'
    TC_F03  H2 heading reads 'Share Your Feedback'
    TC_F04  Name / Email / Message fields all visible
    TC_F05  Star-rating widget has exactly 5 star labels
    TC_F06  Submit button visible and enabled
    TC_F07  Admin nav-link navigates to /admin
    TC_F08  Clicking star-3 radio selects it
    TC_F09  Valid submission shows green success alert
    TC_F10  Form fields are empty after POST-redirect-GET
    TC_F11  Second submission succeeds (seeds data for Admin tests)
    """

    @classmethod
    def setUpClass(cls):
        cls.driver = _make_driver()
        cls.wait   = WebDriverWait(cls.driver, WAIT_TIMEOUT)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    # ── internal helpers ──────────────────────────────────────────────────

    def _goto_form(self):
        """Navigate to the feedback form and wait until it is ready."""
        self.driver.get(BASE_URL + "/")
        self.wait.until(EC.presence_of_element_located((By.ID, "name")))

    def _fill_and_submit(self, name: str, email: str, message: str, star_id: str = "star4"):
        """Fill the feedback form and click Submit. Returns the flash-alert element."""
        self._goto_form()
        self.driver.find_element(By.ID, "name").send_keys(name)
        self.driver.find_element(By.ID, "email").send_keys(email)
        # Star ratings are hidden radio inputs – click via JS
        self.driver.execute_script(
            "arguments[0].click();",
            self.driver.find_element(By.ID, star_id),
        )
        self.driver.find_element(By.ID, "message").send_keys(message)
        # Wait for submit button to be clickable and scroll into view
        btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        self.driver.execute_script("arguments[0].click();", btn)
        return self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert"))
        )

    # ── test cases ────────────────────────────────────────────────────────

    def test_TC_F01_page_loads(self):
        """Feedback page should load without a 4xx/5xx error."""
        self._goto_form()
        self.assertNotIn("500", self.driver.title)
        self.assertNotIn("Not Found", self.driver.title)

    def test_TC_F02_page_title_contains_feedback(self):
        """Page <title> must contain the word 'Feedback'."""
        self._goto_form()
        self.assertIn("Feedback", self.driver.title)

    def test_TC_F03_heading_text(self):
        """H2 must read 'Share Your Feedback'."""
        self._goto_form()
        heading = self.driver.find_element(By.TAG_NAME, "h2")
        self.assertIn("Share Your Feedback", heading.text)

    def test_TC_F04_all_form_fields_visible(self):
        """Name, email, and message fields must all be displayed."""
        self._goto_form()
        for fid in ("name", "email", "message"):
            with self.subTest(field=fid):
                el = self.driver.find_element(By.ID, fid)
                self.assertTrue(el.is_displayed(), f"#{fid} is not visible")

    def test_TC_F05_star_rating_has_five_labels(self):
        """Star-rating widget must render exactly 5 clickable labels."""
        self._goto_form()
        stars = self.driver.find_elements(By.CSS_SELECTOR, ".star-rating label")
        self.assertEqual(5, len(stars), f"Expected 5 stars, found {len(stars)}")

    def test_TC_F06_submit_button_enabled(self):
        """Submit button must be visible and enabled."""
        self._goto_form()
        btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.assertTrue(btn.is_displayed(), "Submit button is hidden")
        self.assertTrue(btn.is_enabled(),   "Submit button is disabled")

    def test_TC_F07_admin_nav_link_navigates(self):
        """Clicking the Admin nav-link must navigate the browser to /admin."""
        self._goto_form()
        admin_link = self.driver.find_element(By.CSS_SELECTOR, "a.nav-link[href='/admin']")
        admin_link.click()
        self.wait.until(EC.url_contains("/admin"))
        self.assertIn("/admin", self.driver.current_url)

    def test_TC_F08_star_rating_click_selects_radio(self):
        """Clicking the star-3 label should select the star3 radio input."""
        self._goto_form()
        star3 = self.driver.find_element(By.ID, "star3")
        self.driver.execute_script("arguments[0].click();", star3)
        self.assertTrue(star3.is_selected(), "star3 radio was not selected after click")

    def test_TC_F09_valid_submission_shows_success_alert(self):
        """A fully-filled form submission must show a green 'Thank you' alert."""
        alert = self._fill_and_submit(
            name    = "Alice Tester",
            email   = "alice@example.com",
            message = "Great service, highly recommend!",
            star_id = "star5",
        )
        self.assertIn("alert-success", alert.get_attribute("class"))
        self.assertIn("Thank you",     alert.text)

    def test_TC_F10_form_is_empty_after_redirect(self):
        """After POST-redirect-GET the name field must be empty (PRG pattern)."""
        self._fill_and_submit(
            name    = "Bob Reset",
            email   = "bob@example.com",
            message = "Testing form reset after redirect.",
            star_id = "star3",
        )
        # Wait for redirect back to form
        self.wait.until(EC.presence_of_element_located((By.ID, "name")))
        name_val = self.driver.find_element(By.ID, "name").get_attribute("value")
        self.assertEqual("", name_val, "Name field should be empty after redirect")

    def test_TC_F11_second_submission_seeds_admin_data(self):
        """Submit a third entry so the Admin test suite has enough data."""
        alert = self._fill_and_submit(
            name    = "Charlie Admin",
            email   = "charlie@example.com",
            message = "Excellent product. Very satisfied overall.",
            star_id = "star4",
        )
        self.assertIn("alert-success", alert.get_attribute("class"),
                      "Second submission did not show success alert")


# ══════════════════════════════════════════════════════════════════════════
# Suite 2 – Admin Response Dashboard
# ══════════════════════════════════════════════════════════════════════════

class TestAdminPage(unittest.TestCase):
    """
    Validates the admin dashboard at GET /admin.

    TC_A01  Admin page loads without errors
    TC_A02  <title> contains 'Admin'
    TC_A03  H2 reads 'Admin Dashboard'
    TC_A04  Three summary stat cards are rendered
    TC_A05  At least one feedback card is present
    TC_A06  Each card displays the customer name in an H5
    TC_A07  Star symbols (★) appear in page source
    TC_A08  At least one 'Pending' status badge is visible
    TC_A09  Every feedback card has a response textarea
    TC_A10  Every feedback card has a delete (trash) button
    TC_A11  Admin can type and submit a response; success alert shown
    TC_A12  'Responded' badge appears after TC_A11 response
    TC_A13  Clicking trash button opens Bootstrap confirm modal
    TC_A14  Clicking Cancel in modal closes it without deleting
    TC_A15  Clicking Delete in modal removes the entry
    """

    @classmethod
    def setUpClass(cls):
        cls.driver = _make_driver()
        cls.wait   = WebDriverWait(cls.driver, WAIT_TIMEOUT)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    # ── internal helpers ──────────────────────────────────────────────────

    def _goto_admin(self):
        """Navigate to the admin dashboard and wait until the H2 is ready."""
        self.driver.get(BASE_URL + "/admin")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))

    def _feedback_cards(self):
        return self.driver.find_elements(By.CSS_SELECTOR, ".card.mb-3")

    def _open_delete_modal(self, index: int = 0):
        """Click the trash button at position *index* and wait for modal."""
        btns = self.driver.find_elements(By.CSS_SELECTOR, ".btn-outline-danger")
        self.driver.execute_script("arguments[0].click();", btns[index])
        return self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal.show"))
        )

    # ── test cases ────────────────────────────────────────────────────────

    def test_TC_A01_page_loads(self):
        """Admin page must load without a 4xx/5xx error."""
        self._goto_admin()
        self.assertNotIn("500",       self.driver.title)
        self.assertNotIn("Not Found", self.driver.title)

    def test_TC_A02_page_title_contains_admin(self):
        """Page <title> must contain 'Admin'."""
        self._goto_admin()
        self.assertIn("Admin", self.driver.title)

    def test_TC_A03_heading_text(self):
        """H2 must read 'Admin Dashboard'."""
        self._goto_admin()
        h2 = self.driver.find_element(By.TAG_NAME, "h2")
        self.assertIn("Admin Dashboard", h2.text)

    def test_TC_A04_three_stat_cards_rendered(self):
        """Three summary cards (Total / Pending / Avg Rating) must be visible."""
        self._goto_admin()
        stat_cards = self.driver.find_elements(By.CSS_SELECTOR, ".row.g-3 .card")
        self.assertGreaterEqual(len(stat_cards), 3,
            f"Expected ≥ 3 stat cards, found {len(stat_cards)}")

    def test_TC_A05_feedback_entries_present(self):
        """At least one feedback card must be rendered."""
        self._goto_admin()
        cards = self._feedback_cards()
        self.assertGreater(len(cards), 0,
            "No feedback cards found – did TC_F09–F11 submissions succeed?")

    def test_TC_A06_card_shows_customer_name(self):
        """Every feedback card must display a non-empty customer name in H5."""
        self._goto_admin()
        names = self.driver.find_elements(By.CSS_SELECTOR, ".card.mb-3 h5")
        self.assertGreater(len(names), 0, "No H5 name elements found")
        for el in names:
            self.assertTrue(el.text.strip(), "Found an H5 with empty customer name")

    def test_TC_A07_star_symbols_in_page(self):
        """Star symbols (★) must appear in the rendered page source."""
        self._goto_admin()
        self.assertIn("★", self.driver.page_source,
                      "No ★ characters found in admin page source")

    def test_TC_A08_pending_badge_visible(self):
        """At least one 'Pending' badge must be visible for unresponded entries."""
        self._goto_admin()
        badges = self.driver.find_elements(By.CSS_SELECTOR, ".badge-pending")
        self.assertGreater(len(badges), 0,
            "No pending badges found – all entries may have been responded to already")

    def test_TC_A09_response_textarea_per_card(self):
        """Every feedback card must include a response textarea."""
        self._goto_admin()
        areas = self.driver.find_elements(
            By.CSS_SELECTOR, ".card.mb-3 textarea[name='response']"
        )
        cards = self._feedback_cards()
        self.assertEqual(len(cards), len(areas),
            f"Mismatch: {len(cards)} cards but {len(areas)} response textareas")

    def test_TC_A10_delete_button_per_card(self):
        """Every feedback card must include a delete (trash) button."""
        self._goto_admin()
        btns  = self.driver.find_elements(By.CSS_SELECTOR, ".btn-outline-danger")
        cards = self._feedback_cards()
        self.assertEqual(len(cards), len(btns),
            f"Mismatch: {len(cards)} cards but {len(btns)} delete buttons")

    def test_TC_A11_admin_can_submit_response(self):
        """Admin typing a response and clicking Send must show a success alert."""
        self._goto_admin()
        # Target the first feedback card's textarea
        textarea = self.driver.find_elements(
            By.CSS_SELECTOR, ".card.mb-3 textarea[name='response']"
        )[0]
        textarea.clear()
        textarea.send_keys("Thank you for your kind words! We truly appreciate it.")

        # Find the submit button inside the same form
        form = textarea.find_element(By.XPATH, "ancestor::form[1]")
        form.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        alert = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success"))
        )
        self.assertIn("Response sent", alert.text)

    def test_TC_A12_responded_badge_after_response(self):
        """After TC_A11, the entry must display a 'Responded' badge."""
        self._goto_admin()
        badges = self.driver.find_elements(By.CSS_SELECTOR, ".badge-responded")
        self.assertGreater(len(badges), 0,
            "No 'Responded' badge found after submitting a response")

    def test_TC_A13_delete_button_opens_modal(self):
        """Clicking the trash icon must open the Bootstrap confirmation modal."""
        self._goto_admin()
        modal = self._open_delete_modal(index=0)
        self.assertTrue(modal.is_displayed(), "Delete modal did not become visible")
        # Modal body should warn about permanent deletion
        body_text = modal.find_element(By.CSS_SELECTOR, ".modal-body").text
        self.assertIn("cannot be undone", body_text.lower(),
                      "Modal body does not warn about permanence")

    def test_TC_A14_cancel_delete_closes_modal(self):
        """Clicking Cancel must close the modal and leave entry count unchanged."""
        self._goto_admin()
        before = len(self._feedback_cards())

        self._open_delete_modal(index=0)
        cancel_btn = self.driver.find_element(
            By.CSS_SELECTOR, ".modal.show .btn-secondary"
        )
        cancel_btn.click()

        # Wait for modal to disappear
        self.wait.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal.show"))
        )
        after = len(self._feedback_cards())
        self.assertEqual(before, after,
            f"Card count changed after Cancel: was {before}, now {after}")

    def test_TC_A15_confirm_delete_removes_entry(self):
        """Confirming deletion must decrease the feedback card count by one."""
        self._goto_admin()
        before = len(self._feedback_cards())

        if before == 0:
            self.skipTest("No feedback entries available to delete.")

        # Delete the last (bottom) entry to avoid affecting earlier tests
        self._open_delete_modal(index=before - 1)
        confirm_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal.show .btn-danger"))
        )
        confirm_btn.click()

        # Wait for admin page to reload after redirect
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "h2")))
        after = len(self._feedback_cards())
        self.assertEqual(before - 1, after,
            f"Expected {before - 1} cards after delete, found {after}")


# ══════════════════════════════════════════════════════════════════════════
# Pretty Test Runner – dual output (console + timestamped file)
# ══════════════════════════════════════════════════════════════════════════

W = 74   # total line width for borders and alignment

_SUITE_META = {
    "TestFeedbackPage": ("Customer Feedback Submission Page", "GET / POST /"),
    "TestAdminPage":    ("Admin Response Dashboard",          "GET /admin"),
}
_TOTAL_SUITES = 2


def _build_suite() -> unittest.TestSuite:
    """Return the full ordered test suite."""
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestFeedbackPage))
    suite.addTests(loader.loadTestsFromTestCase(TestAdminPage))
    return suite


class _PrettyResult(unittest.TestResult):
    """
    Custom TestResult that writes richly-formatted, readable output
    to a _Tee stream (console + file simultaneously).

    Output structure
    ────────────────
      ═══ Report Header ═══
      ┌─── Suite Header ───┐
      │  SUITE N of M  ·  ClassName
      │  Description
      └────────────────────┘
        [ PASS ]  TC_F01   Short docstring description       (1.2s)
        [ FAIL ]  TC_F02   Short docstring description       (0.4s)
                       ↳  AssertionError: …detail…
      ── Suite Footer ──
      ═══ Final Summary ═══
    """

    def __init__(self, stream: _Tee):
        super().__init__()
        self._stream      = stream
        self._current_cls = None
        self._suite_idx   = 0
        self._suite_stats: list = []   # one dict per suite
        self._t_run       = 0.0        # per-test start time
        self._t_total     = 0.0        # overall start time

    # ── stream helper ─────────────────────────────────────────────────────

    def _w(self, text: str):
        self._stream.write(text)
        self._stream.flush()

    # ── formatting helpers ─────────────────────────────────────────────────

    @staticmethod
    def _tc_id(test) -> str:
        """Extract 'TC_F01' or 'TC_A15' from the method name."""
        m = re.search(r"TC_[A-Z]\d+", test._testMethodName)
        return m.group(0) if m else test._testMethodName[:10]

    @staticmethod
    def _short_err(test, err) -> str:
        """Return the last meaningful line of a traceback string."""
        lines = unittest.TestResult()._exc_info_to_string(err, test).strip().splitlines()
        return next((ln.strip() for ln in reversed(lines) if ln.strip()), "")

    def _print_suite_header(self, test):
        cls = type(test)
        if cls is self._current_cls:
            return
        if self._current_cls is not None:
            self._print_suite_footer()

        self._current_cls = cls
        self._suite_idx  += 1
        self._suite_stats.append({"passed": 0, "failed": 0, "errors": 0, "skipped": 0})

        title, sub = _SUITE_META.get(cls.__name__, (cls.__name__, ""))
        tag  = f"SUITE {self._suite_idx} of {_TOTAL_SUITES}  ·  {cls.__name__}"

        self._w("\n")
        self._w("┌" + "─" * (W - 2) + "┐\n")
        self._w(f"│  {tag:<{W - 4}}│\n")
        self._w(f"│  {title:<{W - 4}}│\n")
        self._w(f"│  Route: {sub:<{W - 11}}│\n")
        self._w("└" + "─" * (W - 2) + "┘\n\n")

    def _print_suite_footer(self):
        s = self._suite_stats[-1]
        total = s["passed"] + s["failed"] + s["errors"] + s["skipped"]
        bar   = "─" * (W - 2)
        self._w(f"\n  {bar}\n")
        self._w(
            f"  Suite {self._suite_idx} Result  ──  "
            f"Total: {total}   "
            f"Passed: {s['passed']}   "
            f"Failed: {s['failed']}   "
            f"Errors: {s['errors']}   "
            f"Skipped: {s['skipped']}\n"
        )
        self._w(f"  {bar}\n")

    def _record(self, badge: str, test, detail: str = ""):
        elapsed = time.time() - self._t_run
        tc_id   = self._tc_id(test)
        desc    = (test.shortDescription() or test._testMethodName)[:48]
        timing  = f"({elapsed:.1f}s)"
        left    = f"  {badge}  {tc_id:<8}  {desc}"
        pad     = max(1, W - len(left) - len(timing))
        self._w(f"{left}{' ' * pad}{timing}\n")
        if detail:
            wrap = W - 15
            self._w(f"{'':14}↳  {detail[:wrap]}\n")
            if len(detail) > wrap:
                self._w(f"{'':17}{detail[wrap:wrap * 2]}\n")

    # ── TestResult interface ───────────────────────────────────────────────

    def startTestRun(self):
        self._t_total = time.time()

    def startTest(self, test):
        super().startTest(test)
        self._print_suite_header(test)
        self._t_run = time.time()

    def addSuccess(self, test):
        super().addSuccess(test)
        self._suite_stats[-1]["passed"] += 1
        self._record("[ PASS ]", test)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._suite_stats[-1]["failed"] += 1
        self._record("[ FAIL ]", test, self._short_err(test, err))

    def addError(self, test, err):
        super().addError(test, err)
        self._suite_stats[-1]["errors"] += 1
        self._record("[ERROR ]", test, self._short_err(test, err))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._suite_stats[-1]["skipped"] += 1
        self._record("[ SKIP ]", test, reason)

    def stopTestRun(self):
        if self._current_cls is not None:
            self._print_suite_footer()


# ── Report sections ────────────────────────────────────────────────────────

def _report_header(results_path: Path) -> str:
    now = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
    return "\n".join([
        "",
        "═" * W,
        "  Customer Feedback Portal  –  Selenium UI Test Results",
        "═" * W,
        f"  Date / Time  :  {now}",
        f"  Base URL     :  {BASE_URL}",
        f"  Test Suites  :  {_TOTAL_SUITES}  (TestFeedbackPage, TestAdminPage)",
        f"  Output file  :  {results_path.name}",
        "═" * W,
        "",
    ]) + "\n"


def _report_summary(result: _PrettyResult, duration: float, results_path: Path) -> str:
    passed  = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
    verdict = "ALL TESTS PASSED  ✓" if result.wasSuccessful() else "SOME TESTS FAILED  ✗"

    lines = [
        "",
        "═" * W,
        "  FINAL SUMMARY",
        "═" * W,
        f"  Total Tests  :  {result.testsRun}",
        f"  Passed       :  {passed}",
        f"  Failed       :  {len(result.failures)}",
        f"  Errors       :  {len(result.errors)}",
        f"  Skipped      :  {len(result.skipped)}",
        f"  Duration     :  {duration:.1f}s",
        f"  Result       :  {verdict}",
        "═" * W,
    ]

    issues = (
        [("FAIL", t, e) for t, e in result.failures] +
        [("ERR",  t, e) for t, e in result.errors]
    )
    if issues:
        lines += [
            "",
            f"  ── Failed / Errored Tests {'─' * (W - 27)}",
            "",
        ]
        for i, (kind, test, tb) in enumerate(issues, 1):
            lines.append(f"  {i}. [{kind}]  {test.id()}")
            tb_lines = [ln for ln in tb.strip().splitlines() if ln.strip()]
            for tl in tb_lines[-3:]:
                lines.append(f"         {tl.strip()}")
            lines.append("")

    lines += [
        "═" * W,
        f"  Results saved to: {results_path}",
        "═" * W,
        "",
    ]
    return "\n".join(lines)


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = Path(__file__).parent / f"TestResults_{timestamp}.txt"

    with open(results_path, "w", encoding="utf-8") as f:
        tee = _Tee(sys.stdout, f)
        tee.write(_report_header(results_path))

        result = _PrettyResult(tee)
        t0     = time.time()
        _build_suite().run(result)
        duration = time.time() - t0

        tee.write(_report_summary(result, duration, results_path))

    sys.exit(0 if result.wasSuccessful() else 1)
