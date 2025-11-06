# Email Case Sensitivity - Quick Reference Guide

## TL;DR

A bug allowed duplicate users with different email casing. **FIXED** in `src/database.py` lines 3311 & 3322.

---

## What Was The Bug?

The `convert_quote_to_sale()` method wasn't lowercasing emails, allowing:
- User created via quote: `Smithshaun71@gmail.com`
- User registered manually: `smithshaun71@gmail.com`
- Result: 2 separate accounts for same person

---

## What Was Fixed?

**File**: `c:\Claude\SSG\src\database.py`

**Line 3311**: Added `.lower()` to email lookup
```python
cursor.execute('SELECT id FROM users WHERE email = ?', (customer_email.lower(),))
```

**Line 3322**: Added `.lower()` to email insertion
```python
''', (customer_email.lower(), password_hash, customer_name, customer_phone))
```

---

## How To Use The New Scripts

### Check For Duplicates
```bash
python scripts/manage_duplicate_users.py --list
```

### Check Specific Email
```bash
python scripts/manage_duplicate_users.py --email "user@example.com"
```

### Fix Duplicate Users (Dry Run First!)
```bash
# Dry run to see what would happen
python scripts/manage_duplicate_users.py --merge 123 456 --dry-run

# Actually merge (merges 456 into 123, then deletes 456)
python scripts/manage_duplicate_users.py --merge 123 456
```

### Normalize Existing Emails
```bash
# Check what needs fixing
python scripts/fix_email_case_sensitivity.py --dry-run

# Fix with backup
python scripts/fix_email_case_sensitivity.py --backup
```

### Run Tests
```bash
python scripts/test_email_case_insensitivity.py
```

---

## Verification

All tests pass:
```
[PASS] User Creation: PASS
[PASS] Login: PASS
[PASS] Email Lookup: PASS
[PASS] Set Admin: PASS
[PASS] Update User Email: PASS
Results: 5/5 tests passed
```

Current database status:
- All emails already lowercase
- No duplicates found

---

## Code Review Checklist

When adding user-related code, always check:

- [ ] Emails converted to lowercase before INSERT
- [ ] Emails converted to lowercase before SELECT
- [ ] Emails converted to lowercase before UPDATE
- [ ] Email comparisons are case-insensitive

---

## Where Email Lowercasing Happens

All these locations already correctly lowercase emails:

| Method | File | Line | Status |
|--------|------|------|--------|
| `create_user()` | database.py | 2355 | OK |
| `get_user_by_email()` | database.py | 2379 | OK |
| `set_user_admin()` | database.py | 2413 | OK |
| `update_user()` | database.py | 2606 | OK |
| `verify_password()` | database.py | 2571 | OK |
| `convert_quote_to_sale()` | database.py | 3311, 3322 | FIXED |
| `reset_password()` | reset_password.py | 25 | OK |

---

## Full Documentation

For complete details, see:
`c:\Claude\SSG\docs\EMAIL_CASE_SENSITIVITY_BUG_REPORT.md`
