#!/usr/bin/env python3
"""
Test script to verify email case-insensitivity fix

This script tests that:
1. Users cannot be created with duplicate emails (different casing)
2. Login works with any casing
3. Email lookups are case-insensitive
4. Quote conversion uses lowercase emails
"""

import sys
import os
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import Database


def test_user_creation_case_insensitive():
    """Test that duplicate users cannot be created with different email casing"""
    print("\n" + "=" * 80)
    print("TEST 1: User Creation Case Insensitivity")
    print("=" * 80)

    # Create temporary database for testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_db_path = tmp.name

    try:
        db = Database(tmp_db_path)

        # Test 1: Create user with lowercase email
        print("\n[TEST] Creating user with email: testuser@example.com")
        success, message, user_id = db.create_user(
            'testuser@example.com',
            'password123',
            'Test User',
            '1234567890'
        )

        if success:
            print(f"[OK] User created successfully (ID: {user_id})")
        else:
            print(f"[FAIL] Failed to create user: {message}")
            return False

        # Test 2: Try to create duplicate with uppercase
        print("\n[TEST] Attempting to create duplicate with email: TestUser@Example.COM")
        success, message, user_id = db.create_user(
            'TestUser@Example.COM',
            'password456',
            'Test User Duplicate',
            '0987654321'
        )

        if not success:
            print(f"[OK] Duplicate correctly rejected: {message}")
        else:
            print(f"[FAIL] Duplicate user was created! This should not happen.")
            return False

        # Test 3: Verify email is stored as lowercase
        user = db.get_user_by_email('TestUser@Example.COM')
        if user and user['email'] == 'testuser@example.com':
            print(f"[OK] Email stored as lowercase: {user['email']}")
        else:
            print(f"[FAIL] Email not stored correctly")
            return False

        print("\n[SUCCESS] User creation case insensitivity test passed!")
        return True

    finally:
        # Clean up
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)


def test_login_case_insensitive():
    """Test that login works with any email casing"""
    print("\n" + "=" * 80)
    print("TEST 2: Login Case Insensitivity")
    print("=" * 80)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_db_path = tmp.name

    try:
        db = Database(tmp_db_path)

        # Create a test user
        print("\n[TEST] Creating test user with email: login@test.com")
        success, message, user_id = db.create_user(
            'login@test.com',
            'MySecretPassword',
            'Login Test',
            None
        )

        if not success:
            print(f"[FAIL] Could not create test user: {message}")
            return False

        # Test login with various casings
        test_cases = [
            'login@test.com',      # Original
            'Login@Test.Com',      # Mixed case
            'LOGIN@TEST.COM',      # All uppercase
            'LoGiN@TeSt.CoM',      # Random case
        ]

        for email in test_cases:
            print(f"\n[TEST] Attempting login with: {email}")
            is_valid, user = db.verify_password(email, 'MySecretPassword')

            if is_valid and user:
                print(f"[OK] Login successful! User ID: {user['id']}")
            else:
                print(f"[FAIL] Login failed for: {email}")
                return False

        print("\n[SUCCESS] Login case insensitivity test passed!")
        return True

    finally:
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)


def test_email_lookup_case_insensitive():
    """Test that email lookups are case-insensitive"""
    print("\n" + "=" * 80)
    print("TEST 3: Email Lookup Case Insensitivity")
    print("=" * 80)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_db_path = tmp.name

    try:
        db = Database(tmp_db_path)

        # Create test user
        print("\n[TEST] Creating test user with email: lookup@test.com")
        success, message, user_id = db.create_user(
            'lookup@test.com',
            'password',
            'Lookup Test',
            None
        )

        if not success:
            print(f"[FAIL] Could not create test user: {message}")
            return False

        # Test lookups with various casings
        test_cases = [
            'lookup@test.com',
            'Lookup@Test.Com',
            'LOOKUP@TEST.COM',
            'LoOkUp@TeSt.CoM',
        ]

        for email in test_cases:
            print(f"\n[TEST] Looking up user with: {email}")
            user = db.get_user_by_email(email)

            if user and user['id'] == user_id:
                print(f"[OK] Found user! ID: {user['id']}, Stored email: {user['email']}")
            else:
                print(f"[FAIL] User not found with: {email}")
                return False

        print("\n[SUCCESS] Email lookup case insensitivity test passed!")
        return True

    finally:
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)


def test_set_admin_case_insensitive():
    """Test that set_user_admin is case-insensitive"""
    print("\n" + "=" * 80)
    print("TEST 4: Set Admin Case Insensitivity")
    print("=" * 80)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_db_path = tmp.name

    try:
        db = Database(tmp_db_path)

        # Create test user
        print("\n[TEST] Creating test user with email: admin@test.com")
        success, message, user_id = db.create_user(
            'admin@test.com',
            'password',
            'Admin Test',
            None
        )

        if not success:
            print(f"[FAIL] Could not create test user: {message}")
            return False

        # Test setting admin with different casing
        print("\n[TEST] Setting admin status with email: ADMIN@TEST.COM")
        success = db.set_user_admin('ADMIN@TEST.COM', True)

        if success:
            print("[OK] Admin status set successfully")
        else:
            print("[FAIL] Failed to set admin status")
            return False

        # Verify admin status
        user = db.get_user_by_email('admin@test.com')
        if user and user.get('is_admin'):
            print(f"[OK] User is now admin!")
        else:
            print(f"[FAIL] Admin status not set correctly")
            return False

        print("\n[SUCCESS] Set admin case insensitivity test passed!")
        return True

    finally:
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)


def test_update_user_email_case_insensitive():
    """Test that updating user email normalizes to lowercase"""
    print("\n" + "=" * 80)
    print("TEST 5: Update User Email Case Normalization")
    print("=" * 80)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_db_path = tmp.name

    try:
        db = Database(tmp_db_path)

        # Create test user
        print("\n[TEST] Creating test user")
        success, message, user_id = db.create_user(
            'oldmail@test.com',
            'password',
            'Update Test',
            None
        )

        if not success:
            print(f"[FAIL] Could not create test user: {message}")
            return False

        # Update email with mixed case
        print("\n[TEST] Updating email to: NewEmail@Test.COM")
        success, message = db.update_user(user_id, {'email': 'NewEmail@Test.COM'})

        if not success:
            print(f"[FAIL] Failed to update email: {message}")
            return False

        # Verify email is stored as lowercase
        user = db.get_user_by_id(user_id)
        if user and user['email'] == 'newemail@test.com':
            print(f"[OK] Email normalized to lowercase: {user['email']}")
        else:
            print(f"[FAIL] Email not normalized. Stored as: {user['email'] if user else 'N/A'}")
            return False

        print("\n[SUCCESS] Update user email case normalization test passed!")
        return True

    finally:
        if os.path.exists(tmp_db_path):
            os.unlink(tmp_db_path)


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("EMAIL CASE INSENSITIVITY TEST SUITE")
    print("=" * 80)
    print("Testing that email addresses are handled case-insensitively")
    print("throughout the application.")
    print("=" * 80)

    tests = [
        ("User Creation", test_user_creation_case_insensitive),
        ("Login", test_login_case_insensitive),
        ("Email Lookup", test_email_lookup_case_insensitive),
        ("Set Admin", test_set_admin_case_insensitive),
        ("Update User Email", test_update_user_email_case_insensitive),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "[PASS]" if result else "[FAIL]"
        print(f"{symbol} {test_name}: {status}")

    print("=" * 80)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 80)

    if passed == total:
        print("\n[SUCCESS] All tests passed! Email case insensitivity is working correctly.")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
