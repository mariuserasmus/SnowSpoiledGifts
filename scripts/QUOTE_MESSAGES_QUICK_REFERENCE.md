# Quote Messaging System - Quick Reference

## File Locations

- **Database**: `c:\Claude\SSG\database\signups.db`
- **Database Class**: `c:\Claude\SSG\src\database.py` (lines 4043-4213)
- **Migration Script**: `c:\Claude\SSG\scripts\add_quote_messages_system.py`
- **Full Documentation**: `c:\Claude\SSG\scripts\QUOTE_MESSAGES_README.md`

---

## Database Methods

### 1. Add Message (with optional pricing)

```python
from src.database import Database
db = Database('database/signups.db')

success, msg, msg_id = db.add_quote_message(
    quote_type='quote_requests',  # or 'cake_topper_requests', 'print_service_requests'
    quote_id=123,
    message_text='Your message here',
    sender='admin',               # optional, defaults to 'admin'
    quoted_price_per_item=150.00, # optional
    quoted_total=300.00,          # optional
    attached_image='file.png',    # optional
    message_type='quote_sent'     # optional, defaults to 'admin_message'
)
```

### 2. Get All Messages

```python
messages = db.get_quote_messages('quote_requests', 123)
# Returns list of dicts ordered by created_at (oldest first)
```

### 3. Update Pricing Only

```python
success, msg = db.update_quote_pricing(
    quote_type='quote_requests',
    quote_id=123,
    price_per_item=150.00,
    total=300.00,
    quoted_date=None  # optional, defaults to current timestamp
)
```

---

## Schema Summary

### quote_messages Table

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER | Primary key |
| quote_type | TEXT | 'quote_requests', 'cake_topper_requests', or 'print_service_requests' |
| quote_id | INTEGER | Foreign key to respective quote table |
| message_text | TEXT | Message content |
| sender | TEXT | Default: 'admin' |
| quoted_price_per_item | REAL | Optional, for quote messages |
| quoted_total | REAL | Optional, for quote messages |
| attached_image | TEXT | Optional, filename |
| message_type | TEXT | Default: 'admin_message' |
| created_at | TIMESTAMP | Auto-generated |

### Pricing Columns Added to Quote Tables

All three quote tables now have:
- `quoted_price_per_item` (REAL)
- `quoted_total` (REAL)
- `quoted_date` (TIMESTAMP)

---

## Message Types

- `admin_message` - General message from admin
- `quote_sent` - Admin sending a price quote
- `status_update` - Status change notification

---

## Common Patterns

### Send a Quote

```python
# This automatically updates the quote table's pricing fields
db.add_quote_message(
    'quote_requests', quote_id,
    'Based on your requirements, we can complete this for R150.',
    quoted_price_per_item=150.00,
    quoted_total=150.00,
    message_type='quote_sent'
)
```

### Send Follow-up Message

```python
db.add_quote_message(
    'cake_topper_requests', quote_id,
    'We can rush your order for an additional R50.',
    message_type='admin_message'
)
```

### Display Conversation

```python
messages = db.get_quote_messages('print_service_requests', quote_id)

for msg in messages:
    print(f"[{msg['created_at']}] {msg['sender']}: {msg['message_text']}")
    if msg['quoted_total']:
        print(f"  Quote: R{msg['quoted_total']:.2f}")
```

---

## SQL Queries

### Get Quoted Requests

```sql
SELECT * FROM quote_requests
WHERE quoted_total IS NOT NULL
ORDER BY quoted_date DESC;
```

### Get Messages for a Quote

```sql
SELECT * FROM quote_messages
WHERE quote_type = 'quote_requests' AND quote_id = 123
ORDER BY created_at ASC;
```

### Get Recent Activity

```sql
SELECT quote_type, quote_id, message_text, created_at
FROM quote_messages
WHERE created_at >= datetime('now', '-7 days')
ORDER BY created_at DESC
LIMIT 20;
```

---

## Migration

Run once to set up the schema:

```bash
cd c:\Claude\SSG
python scripts/add_quote_messages_system.py
```

Safe to run multiple times (idempotent).

---

## Return Values

### add_quote_message()
Returns: `(success: bool, message: str, message_id: int or None)`

```python
success, msg, msg_id = db.add_quote_message(...)
if success:
    print(f"Message {msg_id} added successfully")
else:
    print(f"Error: {msg}")
```

### get_quote_messages()
Returns: `List[dict]` or `[]` if none found

### update_quote_pricing()
Returns: `(success: bool, message: str)`

```python
success, msg = db.update_quote_pricing(...)
if success:
    print("Pricing updated")
else:
    print(f"Error: {msg}")
```

---

**Created**: 2025-11-14
**Author**: SQLite Database Specialist
