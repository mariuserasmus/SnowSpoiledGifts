# Quote Messaging System Documentation

## Overview

The Quote Messaging System enables bidirectional communication between administrators and customers regarding quotes. It stores all messages, pricing information, and attachments in a centralized `quote_messages` table.

**Created**: 2025-11-14
**Author**: SQLite Database Specialist
**Database**: `database/signups.db`

---

## Database Schema

### New Table: `quote_messages`

Stores all messages exchanged between admin and customers for quotes.

```sql
CREATE TABLE quote_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_type TEXT NOT NULL,                -- 'quote_requests', 'cake_topper_requests', 'print_service_requests'
    quote_id INTEGER NOT NULL,               -- ID of the quote in its respective table
    message_text TEXT NOT NULL,              -- The message content
    sender TEXT NOT NULL DEFAULT 'admin',    -- Who sent the message
    quoted_price_per_item REAL,              -- Price per item (NULL for non-quote messages)
    quoted_total REAL,                       -- Total price (NULL for non-quote messages)
    attached_image TEXT,                     -- Filename of attached image (optional)
    message_type TEXT DEFAULT 'admin_message', -- Message type (see below)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_quote_messages_quote ON quote_messages(quote_type, quote_id);
CREATE INDEX idx_quote_messages_created ON quote_messages(created_at);
CREATE INDEX idx_quote_messages_type ON quote_messages(message_type);
```

**Message Types:**
- `admin_message` - General message from admin to customer
- `quote_sent` - Admin sending a price quote
- `status_update` - Status change notification
- Custom types as needed

### Modified Tables

Added pricing columns to all three quote tables:

**quote_requests:**
```sql
ALTER TABLE quote_requests ADD COLUMN quoted_price_per_item REAL;
ALTER TABLE quote_requests ADD COLUMN quoted_total REAL;
ALTER TABLE quote_requests ADD COLUMN quoted_date TIMESTAMP;
```

**cake_topper_requests:**
```sql
ALTER TABLE cake_topper_requests ADD COLUMN quoted_price_per_item REAL;
ALTER TABLE cake_topper_requests ADD COLUMN quoted_total REAL;
ALTER TABLE cake_topper_requests ADD COLUMN quoted_date TIMESTAMP;
```

**print_service_requests:**
```sql
ALTER TABLE print_service_requests ADD COLUMN quoted_price_per_item REAL;
ALTER TABLE print_service_requests ADD COLUMN quoted_total REAL;
ALTER TABLE print_service_requests ADD COLUMN quoted_date TIMESTAMP;
```

---

## Database Methods

### 1. `add_quote_message()`

Add a message to a quote conversation.

**Signature:**
```python
def add_quote_message(
    self,
    quote_type,               # Required: 'quote_requests', 'cake_topper_requests', or 'print_service_requests'
    quote_id,                 # Required: ID of the quote
    message_text,             # Required: Message content
    sender='admin',           # Optional: Who sent it (default: 'admin')
    quoted_price_per_item=None,  # Optional: Price per item
    quoted_total=None,        # Optional: Total price
    attached_image=None,      # Optional: Filename of attached image
    message_type='admin_message'  # Optional: Type of message
)
```

**Returns:** `(success: bool, message: str, message_id: int or None)`

**Behavior:**
- Validates that the quote exists
- Inserts the message into `quote_messages`
- If `message_type='quote_sent'` and pricing provided, automatically updates the quote table's pricing fields
- Returns the new message ID on success

**Example Usage:**
```python
from src.database import Database

db = Database('database/signups.db')

# Simple admin message
success, msg, msg_id = db.add_quote_message(
    quote_type='quote_requests',
    quote_id=123,
    message_text='Hello! We received your quote request.',
    sender='admin',
    message_type='admin_message'
)

# Quote message with pricing
success, msg, msg_id = db.add_quote_message(
    quote_type='cake_topper_requests',
    quote_id=456,
    message_text='Here is your quote. The cake topper will be R85.',
    sender='admin',
    quoted_price_per_item=85.00,
    quoted_total=85.00,
    message_type='quote_sent'
)

# Message with attachment
success, msg, msg_id = db.add_quote_message(
    quote_type='print_service_requests',
    quote_id=789,
    message_text='Please see the attached mockup of your design.',
    sender='admin',
    attached_image='mockup_789.png',
    message_type='admin_message'
)
```

---

### 2. `get_quote_messages()`

Retrieve all messages for a specific quote, ordered by timestamp (oldest first).

**Signature:**
```python
def get_quote_messages(
    self,
    quote_type,    # Required: 'quote_requests', 'cake_topper_requests', or 'print_service_requests'
    quote_id       # Required: ID of the quote
)
```

**Returns:** `List[dict]` - List of message dictionaries, or empty list if none found

**Message Dictionary Structure:**
```python
{
    'id': 1,
    'quote_type': 'quote_requests',
    'quote_id': 123,
    'message_text': 'Hello! We received your quote request.',
    'sender': 'admin',
    'quoted_price_per_item': None,
    'quoted_total': None,
    'attached_image': None,
    'message_type': 'admin_message',
    'created_at': '2025-11-14 12:30:45'
}
```

**Example Usage:**
```python
messages = db.get_quote_messages('quote_requests', 123)

for msg in messages:
    print(f"[{msg['created_at']}] {msg['sender']}: {msg['message_text']}")
    if msg['quoted_total']:
        print(f"  Quote: R{msg['quoted_total']:.2f}")
    if msg['attached_image']:
        print(f"  Attachment: {msg['attached_image']}")
```

---

### 3. `update_quote_pricing()`

Update the pricing information directly in the quote table (without adding a message).

**Signature:**
```python
def update_quote_pricing(
    self,
    quote_type,        # Required: 'quote_requests', 'cake_topper_requests', or 'print_service_requests'
    quote_id,          # Required: ID of the quote
    price_per_item,    # Required: Price per item
    total,             # Required: Total price
    quoted_date=None   # Optional: Custom quote date (defaults to current timestamp)
)
```

**Returns:** `(success: bool, message: str)`

**Example Usage:**
```python
# Update pricing with current timestamp
success, msg = db.update_quote_pricing(
    quote_type='quote_requests',
    quote_id=123,
    price_per_item=150.00,
    total=300.00
)

# Update pricing with custom date
success, msg = db.update_quote_pricing(
    quote_type='cake_topper_requests',
    quote_id=456,
    price_per_item=85.00,
    total=85.00,
    quoted_date='2025-11-14 10:00:00'
)
```

---

## Migration Script

**Location:** `scripts/add_quote_messages_system.py`

**Purpose:** Creates the quote_messages table and adds pricing columns to quote tables.

**Safety Features:**
- Checks if tables/columns already exist before creating
- Can be run multiple times safely (idempotent)
- Uses transactions with rollback on error
- Validates all changes after migration

**Running the Migration:**
```bash
cd c:\Claude\SSG
python scripts/add_quote_messages_system.py
```

**Expected Output:**
```
Running migration on: C:\Claude\SSG\database\signups.db
Migration started at: 2025-11-14 20:39:42
------------------------------------------------------------

[1/4] Creating quote_messages table...
  [OK] Created quote_messages table with indexes

[2/4] Adding pricing columns to quote_requests...
  [OK] Added columns to quote_requests: quoted_price_per_item, quoted_total, quoted_date

[3/4] Adding pricing columns to cake_topper_requests...
  [OK] Added columns to cake_topper_requests: quoted_price_per_item, quoted_total, quoted_date

[4/4] Adding pricing columns to print_service_requests...
  [OK] Added columns to print_service_requests: quoted_price_per_item, quoted_total, quoted_date

============================================================
MIGRATION COMPLETED SUCCESSFULLY
============================================================

[VERIFICATION]
  quote_messages table: 0 messages
  quote_requests: OK
  cake_topper_requests: OK
  print_service_requests: OK

Migration ended at: 2025-11-14 20:39:42
```

---

## Usage Patterns

### Pattern 1: Admin sends a quote

```python
# Send quote message with pricing
success, msg, msg_id = db.add_quote_message(
    quote_type='quote_requests',
    quote_id=request_id,
    message_text=f'Based on your requirements, we can complete this for R{total:.2f}. This includes {details}.',
    sender='admin',
    quoted_price_per_item=price_per_item,
    quoted_total=total,
    message_type='quote_sent'
)

# The quote table is automatically updated with pricing
# No need to call update_quote_pricing() separately
```

### Pattern 2: Admin sends follow-up message

```python
success, msg, msg_id = db.add_quote_message(
    quote_type='cake_topper_requests',
    quote_id=request_id,
    message_text='We can rush your order for an additional R50 if needed.',
    sender='admin',
    message_type='admin_message'
)
```

### Pattern 3: Display quote conversation in UI

```python
# Get quote details
quote = db.get_quote_request_by_id(quote_id)

# Get all messages
messages = db.get_quote_messages('quote_requests', quote_id)

# Display in template
for msg in messages:
    if msg['message_type'] == 'quote_sent':
        # Show as highlighted quote message with pricing
        print(f"QUOTE: {msg['message_text']}")
        print(f"Total: R{msg['quoted_total']:.2f}")
    else:
        # Show as regular message
        print(f"Message: {msg['message_text']}")
```

### Pattern 4: Update pricing after negotiation

```python
# If admin manually updates pricing without sending a message
success, msg = db.update_quote_pricing(
    quote_type='print_service_requests',
    quote_id=request_id,
    price_per_item=40.00,
    total=120.00
)

# Optionally add a message about the price change
db.add_quote_message(
    quote_type='print_service_requests',
    quote_id=request_id,
    message_text='Updated pricing based on our discussion.',
    sender='admin',
    message_type='status_update'
)
```

---

## Query Examples

### Get quotes with pricing information

```python
import sqlite3

conn = sqlite3.connect('database/signups.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all quotes that have been priced
cursor.execute('''
    SELECT
        id, name, email, description, quantity,
        quoted_price_per_item, quoted_total, quoted_date,
        status, request_date
    FROM quote_requests
    WHERE quoted_total IS NOT NULL
    ORDER BY quoted_date DESC
''')

for quote in cursor.fetchall():
    print(f"Quote #{quote['id']}: {quote['name']} - R{quote['quoted_total']:.2f}")
```

### Get quotes with message counts

```python
cursor.execute('''
    SELECT
        q.id, q.name, q.email, q.status,
        COUNT(m.id) as message_count,
        MAX(m.created_at) as last_message_date
    FROM quote_requests q
    LEFT JOIN quote_messages m ON m.quote_type = 'quote_requests' AND m.quote_id = q.id
    GROUP BY q.id
    ORDER BY last_message_date DESC
''')
```

### Get recent quote activity

```python
cursor.execute('''
    SELECT
        quote_type, quote_id, message_text, sender,
        message_type, created_at
    FROM quote_messages
    WHERE created_at >= datetime('now', '-7 days')
    ORDER BY created_at DESC
    LIMIT 20
''')
```

---

## Security Considerations

1. **Parameterized Queries**: All database methods use parameterized queries to prevent SQL injection
2. **Input Validation**: Quote types are validated against a whitelist
3. **Quote Existence Check**: Methods verify quotes exist before adding messages
4. **Transaction Safety**: All write operations use transactions with rollback on error

---

## Performance

**Indexes Created:**
- `idx_quote_messages_quote` - Fast lookup by quote_type and quote_id (most common query)
- `idx_quote_messages_created` - Fast ordering by timestamp
- `idx_quote_messages_type` - Fast filtering by message type

**Expected Performance:**
- Message retrieval: O(log n) with index on (quote_type, quote_id)
- Message insertion: O(log n) for index maintenance
- Quote pricing update: O(1) with primary key lookup

---

## Future Enhancements

Potential features to add:

1. **Customer Replies**: Add customer_id field and allow customers to reply to quotes
2. **Read Receipts**: Track when messages are viewed
3. **Email Integration**: Automatically email customers when new messages arrive
4. **Attachments Table**: Separate table for multiple attachments per message
5. **Message Threading**: Group related messages into threads
6. **Admin User Tracking**: Store which admin user sent each message

---

## Troubleshooting

### Issue: "Table already exists" error
**Solution**: The migration script is idempotent. If tables exist, it will skip creation.

### Issue: "Column already exists" error
**Solution**: The migration checks for existing columns. This shouldn't happen unless running incompatible migrations.

### Issue: Messages not appearing
**Solution**:
1. Verify quote exists: `SELECT * FROM quote_requests WHERE id = ?`
2. Check quote_type spelling: Must match exactly ('quote_requests', not 'quotes')
3. Verify messages were inserted: `SELECT * FROM quote_messages WHERE quote_id = ?`

### Issue: Pricing not updating in quote table
**Solution**: Ensure `message_type='quote_sent'` when adding messages with pricing. Or use `update_quote_pricing()` directly.

---

## Contact

For issues or questions about the quote messaging system, refer to:
- SQLite Database Specialist agent
- `src/database.py` - lines 4043-4213
- This documentation file

---

**Last Updated**: 2025-11-14
**Schema Version**: 1.0
