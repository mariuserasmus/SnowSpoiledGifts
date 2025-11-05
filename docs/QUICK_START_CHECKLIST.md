# Unified Cart Migration - Quick Start Checklist

## Pre-Migration

- [ ] Read `UNIFIED_CART_SUMMARY.md` for overview
- [ ] Review current cart implementation in app.py
- [ ] Test current system to establish baseline
- [ ] Schedule migration during low-traffic period
- [ ] Notify team of upcoming changes

## Migration Day

### 1. Backup (5 minutes)
- [ ] Manual backup: `cp database/signups.db database/signups_manual_backup.db`
- [ ] Verify backup file exists and has correct size

### 2. Run Migration Script (5 minutes)
```bash
cd c:\Claude\SSG
python migrate_unified_cart.py
```
- [ ] Script completes without errors
- [ ] Review migration output
- [ ] Note backup file location
- [ ] Verify data counts match

### 3. Update database.py (45 minutes)
- [ ] Open `unified_cart_functions.py`
- [ ] Open `src/database.py`
- [ ] Replace old `add_to_cart()` (line ~1819) with new version
- [ ] Replace old `get_cart_items()` (line ~1864) with new version
- [ ] Replace old `get_cart_count()` (line ~1972) with new version
- [ ] Replace old `update_cart_quantity()` (line ~1931) with new version
- [ ] Replace old `remove_from_cart()` (line ~1957) with new version
- [ ] Replace old `clear_cart()` (line ~1998) with new version
- [ ] Replace old `migrate_guest_cart_to_user()` (line ~2669) with new version
- [ ] Update `get_all_active_carts()` (line ~2017) to use unified schema
- [ ] Add backward compatibility wrappers (lines ~3714-3920)
- [ ] Save file

### 4. Update app.py (1-2 hours)
Follow `APP_PY_UPDATE_INSTRUCTIONS.md` for each change:

#### Add to Cart Routes
- [ ] Update `/add_to_cart/<int:item_id>` - Add `'cutter_item'` parameter
- [ ] Update `/candles-soaps/add_to_cart/<int:product_id>` - Use unified function

#### View Cart
- [ ] Update `/cart` route - Simplify to single `get_cart_items()` call

#### Cart Count
- [ ] Update `inject_cart_count()` context processor

#### Update/Remove Cart
- [ ] Update `/update_cart/<int:cart_id>` route
- [ ] Update `/remove_from_cart/<int:cart_id>` route

#### Clear Cart
- [ ] Update `/clear_cart` route

#### Login/Register
- [ ] Update cart migration in login route
- [ ] Update cart migration in register route (if applicable)

#### Other Routes
- [ ] Search for all `add_to_candles_soaps_cart` calls
- [ ] Search for all `get_candles_soaps_cart_items` calls
- [ ] Search for all `get_candles_soaps_cart_count` calls
- [ ] Search for all `clear_candles_soaps_cart` calls
- [ ] Update any cart-related admin routes

### 5. Testing (2-3 hours)

#### Basic Cart Operations
- [ ] Add cutter item to cart (guest user)
- [ ] Add candles/soap item to cart (guest user)
- [ ] View cart - both items appear
- [ ] Update quantities
- [ ] Remove items
- [ ] Clear cart

#### Guest User Flow
- [ ] Add items to cart as guest
- [ ] Register new account
- [ ] Verify cart persists after registration
- [ ] Logout
- [ ] Add more items as guest
- [ ] Login with existing account
- [ ] Verify carts merge correctly

#### Logged-in User Flow
- [ ] Login
- [ ] Add cutter items
- [ ] Add candles/soap items
- [ ] View cart
- [ ] Update quantities
- [ ] Remove items
- [ ] Logout and login again
- [ ] Verify cart persists

#### Checkout Flow
- [ ] Checkout with only cutter items
- [ ] Checkout with only candles/soaps items
- [ ] Checkout with mixed cart (both types)
- [ ] Verify order created correctly
- [ ] Verify cart cleared after checkout
- [ ] Verify stock updated correctly

#### Edge Cases
- [ ] Empty cart displays correctly
- [ ] Cart count badge updates correctly
- [ ] Inactive products don't show in cart
- [ ] Out-of-stock handling works
- [ ] Cart persists across sessions

#### Database Verification
```sql
-- Check cart data
SELECT * FROM cart_items LIMIT 10;

-- Check product type distribution
SELECT product_type, COUNT(*) as count, SUM(quantity) as total_qty
FROM cart_items
GROUP BY product_type;

-- Verify no orphaned data
SELECT c.*
FROM cart_items c
LEFT JOIN cutter_items ci ON c.product_id = ci.id AND c.product_type = 'cutter_item'
LEFT JOIN candles_soaps_products csp ON c.product_id = csp.id AND c.product_type = 'candles_soap'
WHERE ci.id IS NULL AND csp.id IS NULL;
```

### 6. Performance Check
- [ ] Cart loads quickly
- [ ] Cart count updates quickly
- [ ] Checkout is responsive
- [ ] No slow queries in logs

## Post-Deployment

### Day 1
- [ ] Monitor application logs
- [ ] Check error rates
- [ ] Verify cart operations working
- [ ] Monitor user feedback
- [ ] Check cart abandonment rates

### Week 1
- [ ] Review cart analytics
- [ ] Check for any reported issues
- [ ] Verify data integrity
- [ ] Monitor performance metrics

### Month 1
- [ ] Consider removing backward compatibility wrappers
- [ ] Consider dropping old cart tables
- [ ] Update documentation if needed
- [ ] Review benefits realized

## Rollback (If Needed)

### Quick Rollback
```bash
# Stop application
# Restore database
cp database/signups_backup_YYYYMMDD_HHMMSS.db database/signups.db

# Revert code
git checkout src/database.py app.py

# Restart application
```

### Verify Rollback
- [ ] Application starts successfully
- [ ] Cart functionality restored
- [ ] User data intact
- [ ] No errors in logs

## Files Reference

All files in `c:\Claude\SSG\`:

- `migrate_unified_cart.py` - Migration script
- `unified_cart_functions.py` - New database functions
- `UNIFIED_CART_MIGRATION_GUIDE.md` - Complete guide
- `APP_PY_UPDATE_INSTRUCTIONS.md` - app.py changes
- `UNIFIED_CART_SUMMARY.md` - Executive summary
- `QUICK_START_CHECKLIST.md` - This checklist

## Success Criteria

All checked means migration is complete:

- [ ] Migration script ran successfully
- [ ] Database schema updated
- [ ] All cart data migrated
- [ ] database.py updated
- [ ] app.py updated
- [ ] All tests pass
- [ ] No errors in logs
- [ ] Cart works for guest users
- [ ] Cart works for logged-in users
- [ ] Mixed cart checkout works
- [ ] Performance is acceptable
- [ ] Backup retained for rollback

## Common Issues & Solutions

### Issue: Migration script fails
**Solution**: Check database file path, verify Python has write permissions

### Issue: Cart items don't appear after migration
**Solution**: Verify JOINs in `get_cart_items()` are correct for both product types

### Issue: Cart count is wrong
**Solution**: Check `get_cart_count()` is summing all product types

### Issue: Can't add items to cart
**Solution**: Verify `product_type` parameter is being passed correctly

### Issue: Checkout fails with mixed cart
**Solution**: Ensure order items table can handle `product_type` field

### Issue: Old cart functions still being called
**Solution**: Search app.py for old function names, ensure all are updated

## Notes

- Keep this checklist handy during migration
- Check off items as you complete them
- Don't skip testing steps
- Document any issues encountered
- Keep backup for at least 30 days

## Sign-off

- [ ] All steps completed
- [ ] All tests passed
- [ ] Team notified of completion
- [ ] Documentation updated
- [ ] Migration considered successful

---

**Date Started**: _______________
**Date Completed**: _______________
**Migrated By**: _______________
**Verified By**: _______________
