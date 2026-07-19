# Database Performance Patterns for Rails

> Return to [SKILL.md](../SKILL.md) for core principles, boundaries, and reference-selection rules.

Load this reference for Active Record data modeling, query shape, indexes, N+1s, counting, batching, replicas, migration safety, query plans, or database monitoring.

## Contents

- [Index Usage Patterns](#index-usage-patterns)
- [Composite Index Column Order](#composite-index-column-order)
- [N+1 Query Patterns](#n1-query-patterns)
- [Query Optimization Patterns](#query-optimization-patterns)
- [Advanced Performance Techniques](#advanced-performance-techniques)
- [PostgreSQL Specific Optimizations](#postgresql-specific-optimizations)
- [Migration Best Practices](#migration-best-practices)
- [Performance Monitoring](#performance-monitoring)
- [Active Record Modeling and Query Semantics](#active-record-modeling-and-query-semantics)

## Index Usage Patterns

### Function Calls on Indexed Columns

**Guidance**: Applying a function to an indexed column can prevent a plain index from being used for that expression. The result depends on the database, operator class, and selectivity, so verify with `EXPLAIN`.

```ruby
# ⚠️ May not use a plain index on 'email'
User.where("LOWER(email) = ?", "john@example.com")

# ⚠️ May not use a plain index on 'created_at'
Post.where("DATE(created_at) = ?", Date.current)

# ⚠️ May not use a plain index on 'title'
Post.where("LENGTH(title) > ?", 50)
```

**Solution**: Create functional indexes for computed values, or rewrite the predicate to filter the raw column. Verify the plan; a matching expression index can be used:

```ruby
# Migration
add_index :users, "LOWER(email)", name: 'index_users_on_lower_email'
add_index :posts, "DATE(created_at)", name: 'index_posts_on_date_created_at'
add_index :posts, "LENGTH(title)", name: 'index_posts_on_title_length'

# Query (can use a matching expression index)
User.where("LOWER(email) = ?", email.downcase)
Post.where("DATE(created_at) = ?", Date.current)
Post.where("LENGTH(title) > ?", 50)
```

**PostgreSQL Expression Indexes**:
```sql
-- Create expression index
CREATE INDEX idx_users_email_lower ON users (LOWER(email));

-- Create partial expression index
CREATE INDEX idx_active_users_email ON users (LOWER(email)) 
WHERE status = 'active';
```

### OR Conditions and Composite Indexes

**Guidance**: OR conditions can make a composite index less effective. A planner may use separate index scans (such as a BitmapOr) or choose a sequential scan, so verify the plan with `EXPLAIN`.

```ruby
# ⚠️ May be less efficient with a composite index on (user_id, status)
Order.where(user_id: user.id)
     .where("status = 'pending' OR status = 'processing'")

# ⚠️ Equivalent Rails syntax; verify the generated plan
Order.where(user_id: user.id)
     .where(status: 'pending')
     .or(Order.where(user_id: user.id, status: 'processing'))
```

**Solution**: Use IN conditions which are index-friendly:

```ruby
# ✅ USES composite index on (user_id, status)
Order.where(user_id: user.id, status: ['pending', 'processing'])

# ✅ Alternative with scope
class Order
  scope :pending_or_processing, -> { where(status: ['pending', 'processing']) }
end

Order.where(user_id: user.id).pending_or_processing
```

### NOT Conditions Break Index Usage

**Guidance**: NOT and inequality predicates can be less selective and may lead the planner to scan much of the table. Index use depends on selectivity, null semantics, and the database, so verify with `EXPLAIN`.

```ruby
# ⚠️ May scan much of the table when most rows are not canceled
Order.where.not(status: 'canceled')
User.where.not(email: nil)
Post.where("status != 'draft'")
```

**Solutions**:

1. **Use selective positive conditions when the domain allows**:
```ruby
# ✅ Can use an index when the values are selective
Order.where(status: ['pending', 'processing', 'shipped', 'delivered'])
Post.where(status: ['published', 'featured'])

# For frequent non-NULL queries, consider a matching partial index
User.where.not(email: nil)
```

2. **Partial indexes (PostgreSQL)**:
```sql
-- Index only non-canceled orders
CREATE INDEX idx_orders_active_status ON orders (status) 
WHERE status != 'canceled';

-- Index only users with emails
CREATE INDEX idx_users_with_email ON users (email) 
WHERE email IS NOT NULL;
```

### LIKE Pattern Performance

**LIKE patterns behave differently for indexing**:

```ruby
# ✅ Can use index (prefix match)
Post.where("title LIKE ?", "Rails%")      
User.where("name LIKE ?", "John%")

# ❌ Cannot use standard index (suffix match)
Post.where("title LIKE ?", "%Tutorial")   
User.where("email LIKE ?", "%@gmail.com")

# ❌ Cannot use standard index (contains)
Post.where("title LIKE ?", "%Rails%")     
```

**Solutions for contains/suffix matching**:

1. **pg_trgm extension (PostgreSQL)**:
```ruby
# Migration
enable_extension :pg_trgm

# GIN index for trigram matching
add_index :posts, :title, using: :gin, opclass: :gin_trgm_ops
add_index :users, :email, using: :gin, opclass: :gin_trgm_ops

# Queries now use index
Post.where("title ILIKE ?", "%rails%")
User.where("email ILIKE ?", "%gmail%")
```

2. **Full-text search**:
```ruby
# PostgreSQL built-in full-text search
add_index :posts, "to_tsvector('english', title)", using: :gin

Post.where("to_tsvector('english', title) @@ plainto_tsquery('english', ?)", query)
```

## Composite Index Column Order

**Critical Rule**: Index column order matters significantly for query performance.

```ruby
# Given composite index: (user_id, created_at, status)
add_index :orders, [:user_id, :created_at, :status]

# ✅ USES index efficiently (left-to-right prefix)
Order.where(user_id: 1)
Order.where(user_id: 1, created_at: Date.current)  
Order.where(user_id: 1, created_at: Date.current, status: 'pending')

# ❌ CANNOT use index (doesn't start with leftmost column)
Order.where(created_at: Date.current)
Order.where(status: 'pending')
Order.where(created_at: Date.current, status: 'pending')

# ⚠️ PARTIAL index usage (user_id only)
Order.where(user_id: 1, status: 'pending')  # skips created_at
```

**Designing Index Order**:
1. **Equality conditions first** (WHERE user_id = ?)
2. **Range conditions last** (WHERE created_at > ?)  
3. **Most selective columns first** (columns with highest cardinality)

```ruby
# Good index design for common query patterns
add_index :orders, [:user_id, :status, :created_at]  # user filter + status filter + date sort
add_index :posts, [:published, :category_id, :created_at]  # published filter + category + date sort
```

## N+1 Query Patterns

### Basic N+1 Prevention

```ruby
# ❌ N+1: loads posts separately for each user
users = User.limit(10)
users.each { |user| puts user.posts.count }

# ✅ Single query with includes
users = User.includes(:posts).limit(10)  
users.each { |user| puts user.posts.size }  # uses loaded association

# ✅ Even better: counter cache
class User < ApplicationRecord
  has_many :posts
end

class Post < ApplicationRecord
  belongs_to :user, counter_cache: true
end

# The users table has a posts_count column.
users.each { |user| puts user.posts_count }  # no query needed
```

### Complex Association N+1

```ruby
# ❌ Multiple N+1 queries
@posts = Post.published.limit(10)
# In view: post.author.name (N queries)
# In view: post.comments.approved.count (N queries)  
# In view: post.tags.pluck(:name) (N queries)

# ✅ Preload everything needed
@posts = Post.published
             .includes(:author, :tags)
             .includes(comments: :author)
             .limit(10)
```

### Deep Association N+1

```ruby
# ❌ Deep N+1
users.each do |user|
  user.orders.each do |order|
    order.order_items.each do |item|
      puts item.product.name  # N*M*P queries
    end
  end
end

# ✅ Nested includes
users = User.includes(orders: { order_items: :product })
```

## Query Optimization Patterns

### Select Only Needed Columns

```ruby
# ❌ Loads all columns (including large text fields)
posts = Post.where(published: true)

# ✅ Select only needed columns
posts = Post.where(published: true).select(:id, :title, :created_at)

# ✅ Useful for large text/json columns
users = User.select(:id, :name, :email)  # excludes bio, preferences JSON
```

### Efficient Counting

```ruby
# ❌ Loads all records then counts in Ruby
User.where(active: true).to_a.count

# ✅ Database-level count
User.where(active: true).count  # Uses SQL COUNT()

# ✅ Counter caches for associations
class User < ApplicationRecord
  has_many :posts
end

class Post < ApplicationRecord
  belongs_to :user, counter_cache: true
end

# The users table has a posts_count column.
user.posts_count  # No query needed

# ✅ Estimated counts for large tables (PostgreSQL)
ActiveRecord::Base.connection.execute(
  "SELECT reltuples::bigint FROM pg_class WHERE relname = 'users'"
).first['reltuples']
```

### Batching Large Operations

```ruby
# ❌ Instantiates and updates every record one by one
User.where(created_at: 1.year.ago..1.day.ago).each do |user|
  user.update!(status: 'inactive')
end

# ✅ One SQL UPDATE, with no record instantiation
User.where(created_at: 1.year.ago..1.day.ago).update_all(status: 'inactive')

# ✅ Batch SQL updates when the set is very large
User.where(created_at: 1.year.ago..1.day.ago).in_batches(of: 1000) do |batch|
  batch.update_all(status: 'inactive')
end

# ✅ find_each for iteration
User.where(active: true).find_each(batch_size: 1000) do |user|
  user.calculate_metrics
end
```

## Advanced Performance Techniques

### Connection Pool Optimization

```yaml
# config/database.yml
production:
  adapter: postgresql
  pool: <%= ENV['RAILS_MAX_THREADS'] || 25 %>
  checkout_timeout: 5
  reaping_frequency: 10
  dead_connection_timeout: 5
```

### Read Replicas

```ruby
# config/database.yml  
production:
  primary:
    adapter: postgresql
    database: myapp_production
    # primary connection config
  
  primary_replica:
    adapter: postgresql  
    database: myapp_production
    replica: true
    # read replica connection config

# Use read replica for heavy queries
User.connected_to(role: :reading) do
  @users = User.includes(:posts).page(params[:page])
end
```

### Database Connection Management

```ruby
# Long-running background jobs
class HeavyReportJob < ApplicationJob
  def perform
    # Clear connections to prevent timeouts
    ActiveRecord::Base.clear_active_connections!
    
    # Heavy work here
    generate_report
    
  ensure
    ActiveRecord::Base.clear_active_connections!
  end
end
```

## PostgreSQL Specific Optimizations

### EXPLAIN ANALYZE Usage

```ruby
# Check query execution plan
result = ActiveRecord::Base.connection.execute(
  "EXPLAIN ANALYZE #{User.where(active: true).to_sql}"
)
puts result.to_a
```

### Partial Indexes

```sql
-- Index only active users
CREATE INDEX idx_active_users_email ON users (email) WHERE active = true;

-- Partial-index predicates must be immutable; rolling time windows cannot be used here.
-- Index orders with a stable status predicate instead.
CREATE INDEX idx_pending_orders_status ON orders (status)
WHERE status = 'pending';

-- Index only published posts
CREATE INDEX idx_published_posts_category ON posts (category_id) 
WHERE status = 'published';
```

### JSON Column Optimization

```ruby
# Migration
add_column :users, :preferences, :jsonb
add_index :users, :preferences, using: :gin

# Efficient JSON queries
User.where("preferences @> ?", { theme: 'dark' }.to_json)
User.where("preferences -> 'notifications' ->> 'email' = ?", 'true')
```

### Array Column Performance

```ruby
# Migration  
add_column :posts, :tag_names, :text, array: true
add_index :posts, :tag_names, using: :gin

# Array queries
Post.where("tag_names && ARRAY[?]", ['rails', 'performance'])  # overlap
Post.where("tag_names @> ARRAY[?]", ['tutorial'])  # contains
```

## Migration Best Practices

### Large Table Migrations

```ruby
# ❌ Dangerous on large tables (locks table)
add_column :users, :new_field, :string
add_index :users, :email  

# ✅ Safe patterns
add_column :users, :new_field, :string
add_index :users, :email, algorithm: :concurrently

# Or use strong_migrations gem for safety
```

### Index Creation Strategy

```ruby
# Create indexes concurrently in production
class AddIndexToUsers < ActiveRecord::Migration[7.0]
  disable_ddl_transaction!  # Required for concurrent indexes
  
  def change
    add_index :users, :email, algorithm: :concurrently
  end
end
```

## Performance Monitoring

### Query Analysis

```ruby
# Log slow queries
# config/environments/production.rb
config.active_record.logger = ActiveSupport::Logger.new(STDOUT)
config.log_level = :info

# Or use query analysis gems
gem 'bullet'  # N+1 detection
gem 'prosopite'  # N+1 detection  
gem 'query_diet'  # Query analysis
```

### Database Statistics

```sql
-- PostgreSQL: Find slow queries
SELECT query, mean_time, calls, total_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

-- PostgreSQL: Find unused indexes
SELECT schemaname, tablename, indexname, idx_scan 
FROM pg_stat_user_indexes 
WHERE idx_scan = 0;
```

## Active Record Modeling and Query Semantics

### Associations and Domain Shape

- Model ownership and cardinality honestly. Do not use `belongs_to :user` as a lazy substitute for account/tenant ownership.
- Association names should express the domain, not table plumbing.
- Prefer association traversal, scoped associations, and `merge` over manual foreign-key juggling.
- Join models are required when the relationship has attributes, lifecycle, permissions, ordering, auditability, or behavior.
- `dependent:` is product/data-retention policy, not housekeeping. Understand deletion, nullification, archival, audit, and legal implications.
- JSON/serialized columns fit opaque metadata/config blobs. They are a smell for queryable, relational, constrained, permissioned, audited, or lifecycle-bearing data.
- Polymorphism, STI, and delegated types are sharp knives. Choose by query shape, shared behavior, lifecycle, authorization, and migration path.
- If enum state accumulates timestamps, actors, retry counts, error messages, audit trails, or history, consider a first-class event/process table.

### Validations, Constraints, and Invariants

- Model validations improve UX. Database constraints preserve truth.
- Use unique indexes for uniqueness; scoped uniqueness needs matching composite indexes.
- Use foreign keys and check constraints unless the app has a documented reason not to.
- Avoid validations that load large associations or perform expensive queries on hot paths.
- Race-sensitive invariants require database enforcement, transactions, locks, upserts, or atomic writes, not just validation.

### Relations and Querying

- Ask constantly: is this still an `ActiveRecord::Relation`, or did Ruby materialize it into an array/scalar?
- Return relations from scopes and chainable query methods unless intentionally returning a scalar, array, or performing work.
- Keep database work in SQL until loading is deliberate. Avoid `to_a`, `map`, `select`, `group_by`, `sort_by`, `uniq`, and Ruby filtering over unbounded relations when SQL can do it.
- `find_by`, `take`, and first-row behavior are unordered unless explicit order exists. Add deterministic order when it matters.
- `where.not(column: value)` does not include NULL rows unless handled explicitly.
- `joins` against `has_many` can duplicate parent rows. Use `distinct`, grouping, or subqueries only when the SQL semantics are intended.
- Choose `preload`, `includes`, `eager_load`, `references`, and `strict_loading` based on desired SQL shape and N+1 risk, not folklore.
- `select` can instantiate partial models and cause missing attributes. `pluck`, `pick`, `ids`, calculations, `exists?`, `in_batches`, and `find_each` execute/load differently; use them intentionally.
- `find_each`/batching imposes batching order and is not a drop-in replacement for arbitrary ordered iteration.
- Avoid `default_scope` unless the app already depends on it and hidden behavior is understood.
- Never interpolate SQL. Use bound parameters, hash conditions, Arel where appropriate, and `sanitize_sql_like` for LIKE patterns.
- Bulk APIs (`insert_all`, `upsert_all`, `update_all`, `delete_all`, `touch_all`) bypass validations/callbacks; state that explicitly when using them.

### Indexes, Plans, Transactions, and Locks

- Composite index design starts from real `WHERE`, `JOIN`, and `ORDER BY` shape. Adapter rules differ; verify with EXPLAIN when the claim matters.
- Avoid speculative or duplicate indexes. Account for write cost, storage, lock risk, and planner selectivity.
- Plan-reading basics: estimated vs actual rows, loops, sort/hash/seq-scan nodes, index condition vs filter, join strategy, and eager-loading side effects.
- Transactions are per database connection, not per model and not distributed across databases.
- Do not rescue `ActiveRecord::StatementInvalid` inside a PostgreSQL transaction and continue; restart the transaction.
- Nested transactions are not independent unless `requires_new: true`; adapters usually emulate with savepoints.
- Use `after_commit` for external side effects, cache invalidation, broadcasts, and jobs that need committed data.
- Prefer unique indexes, upserts, atomic updates, and constraints over check-then-act code.
- Use optimistic locking (`lock_version`) for human edit conflicts and surface/reload on `StaleObjectError`. Use pessimistic locks/`with_lock` for short critical sections. Acquire multiple locks in one globally deterministic order to avoid deadlocks, retry `ActiveRecord::Deadlocked` only at an idempotent boundary with a strict limit, and never perform network I/O while holding locks.
- A transaction is not serial execution. Two `READ COMMITTED` transactions can both pass a check and both commit (write skew/phantom). Enforce the invariant with a constraint, an atomic conditional write, or a supported `SERIALIZABLE` level with bounded retries.
- `find_or_create_by` is not atomic; back the key with a unique constraint and use `create_or_find_by` or `upsert_all(unique_by:)` deliberately.
- Treat `:reading`/replica connections as stale by design. Keep correctness-dependent post-write reads on the writer (`connected_to(role: :writing)` or verified stickiness) until the replication window is safe.
- Represent money as integer minor units or `BigDecimal`/decimal, never `Float`; define one rounding mode and stage. Treat counter caches as denormalized data maintained by every create/delete path.
- For deep failure modes (isolation, deadlocks, money, counter caches, deletion semantics, time zones, batching, counts, N+1 in serializers/jobs, update-API bypass), read `rails-concurrency-and-safety.md`.

### Migrations and Data Changes

- The schema dump is the practical source of rebuild truth; migrations describe evolution.
- Do not edit committed/applied migrations. Add a new migration.
- Prefer reversible migrations. Use `up`/`down` or `reversible` for irreversible operations.
- Adding `NOT NULL`, uniqueness, FKs, checks, or indexes requires existing-data proof plus lock/backfill/deploy-order thinking.
- Large tables need choreography: backward-compatible nullable schema, deploy code, batch backfill, validate constraints/indexes, then tighten invariants.
- PostgreSQL concurrent indexes require disabling DDL transactions and a rollback/drop plan.
- Treat every large-table DDL as adapter/version-specific rollout choreography: prove lock/rewrite behavior, use concurrent or not-valid-then-validate where supported, backfill idempotently, tighten later, ship rollback/monitoring first. Do not assume blanket rules (e.g. "adding a column with a default always rewrites" is false on modern PostgreSQL); verify against the installed adapter/version.
- Data migrations are operational risk. Prefer separate, idempotent, batched, observable work using stable SQL or anonymous model classes. Avoid current app models/callbacks in migrations that may run months later.
- Stop if table size, lock behavior, timeout policy, deploy order, rollback path, or monitoring is unknown.

This database optimization guide provides the foundation for writing Rails applications that perform well at scale. Always measure before optimizing, and use EXPLAIN ANALYZE to verify that your indexes are being used effectively.
