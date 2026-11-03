"""Read-only checks for the final report; no database records are changed."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pages.login_page import LoginPage
from pages.payments_page import PaymentsPage


def run_checks():
    results = []

    def check(test_id, feature, condition, expected, function):
        try:
            actual = function()
            results.append(dict(id=test_id, feature=feature, condition=condition,
                                expected=expected, actual=actual, status="Pass"))
        except Exception as exc:
            results.append(dict(id=test_id, feature=feature, condition=condition,
                                expected=expected, actual=str(exc), status="Fail"))

    def syntax():
        files = [Path("main.py")]
        for folder in ("pages", "components", "config", "data"):
            files.extend(Path(folder).glob("*.py"))
        for path in files:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        return f"All {len(files)} application Python files parsed successfully."

    check("T01", "Source syntax", "Parse all application Python files", "No syntax errors", syntax)

    def money():
        value = PaymentsPage._parse_money(None, "UGX 1,200,000")
        assert value == 1200000.0
        return "Returned 1200000.0."
    check("T02", "Money conversion", "UGX 1,200,000", "1200000.0", money)

    def invalid_money():
        try:
            PaymentsPage._parse_money(None, "abc")
        except ValueError:
            return "Raised ValueError as expected."
        raise AssertionError("Invalid value accepted")
    check("T03", "Money conversion", "abc", "ValueError", invalid_money)

    def safe_name():
        value = PaymentsPage._safe_filename(None, "Sarah / Namuli")
        assert value == "Sarah___Namuli"
        return f"Returned {value}."
    check("T04", "Receipt filename", "Sarah / Namuli", "Replace spaces and slash with underscores", safe_name)

    class Field:
        def __init__(self, value): self.value = value
        def get(self): return self.value
        def set(self, value): self.value = value
        def focus_set(self): pass

    def login(valid):
        called = []
        obj = SimpleNamespace(username_var=Field("eric"), password_var=Field("12345" if valid else "wrong"),
                              password_entry=Field(""), unbind_all=lambda event: None,
                              login_success_function=lambda: called.append(True), winfo_toplevel=lambda: None)
        with patch("pages.login_page.messagebox.showerror") as error:
            LoginPage.check_login(obj)
            if valid:
                assert called and not error.called
                return "Success callback called; no error message."
            assert not called and error.called and obj.password_var.get() == ""
            return "Error requested, password cleared, success callback not called."
    check("T05", "Login logic", "Correct default credentials; mocked controls", "Allow login", lambda: login(True))
    check("T06", "Login logic", "Wrong password; mocked controls", "Reject login and clear password", lambda: login(False))

    def payment(balance, date, expected_warning=None):
        entries = {key: Field(value) for key, value in dict(tenant="Sample Tenant", property_unit="Sample / A1",
                   amount="500000", balance=balance, payment_date=date, reference="DEMO", notes="Sample",
                   method="Cash", status="Paid").items()}
        obj = SimpleNamespace(tenant_lookup={"Sample Tenant": {"tenant_id": 1}},
                              _parse_money=lambda value: PaymentsPage._parse_money(None, value),
                              load_payment_data=lambda: None)
        modal = SimpleNamespace(destroy=lambda: None)
        with patch("pages.payments_page.save_payment_to_database") as save, patch("pages.payments_page.messagebox.showwarning") as warning:
            PaymentsPage.save_payment(obj, entries, modal)
            if expected_warning:
                assert not save.called and warning.call_args.args[0] == expected_warning
                return f"{expected_warning} warning requested; database save not called."
            data = save.call_args.args[0]
            assert data["amount"] == 350000 and data["balance"] == 150000
            return "Save received amount 350000 and balance 150000; no real database write."
    check("T07", "Partial payment", "Main amount 500000, balance 150000, date 2026-11-02", "Save amount paid 350000", lambda: payment("150000", "2026-11-02"))
    check("T08", "Balance validation", "Balance -1", "Invalid Balance; block save", lambda: payment("-1", "2026-11-02", "Invalid Balance"))
    check("T09", "Balance validation", "Balance 600000, main amount 500000", "Invalid Balance; block save", lambda: payment("600000", "2026-11-02", "Invalid Balance"))
    check("T10", "Date validation", "2026-02-30", "Invalid Date; block save", lambda: payment("0", "2026-02-30", "Invalid Date"))
    return results


if __name__ == "__main__":
    output = Path("reports")
    output.mkdir(exist_ok=True)
    results = run_checks()
    (output / "test_evidence.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    for result in results:
        print(result["id"], result["status"], result["actual"])
    raise SystemExit(any(result["status"] == "Fail" for result in results))
