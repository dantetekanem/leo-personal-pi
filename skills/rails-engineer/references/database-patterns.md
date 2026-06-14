# Database Performance Patterns for Rails

Comprehensive guide to database optimization patterns that expert Rails developers must understand.

## Index Usage Patterns

### Function Calls on Indexed Columns

**Problem**: Function calls in WHERE clauses prevent index usage, even when indexes exist.

```ruby
# ❌ BREAKS index on 'email' column
User.where("LOWER(email) = ?", "john@example.com")

# ❌ BREAKS index on 'created_at' column  
Post.where("DATE(created_at) = ?", Date.current)

# ❌ BREAKS index on 'title' column
Post.where("LENGTH(title) > ?", 50)
```

**Solution**: Create functional indexes for computed values:

```ruby
# Migration
add_index :users, "LOWER(email)", name: 'index_users_on_lower_email'
add_index :posts, "DATE(created_at)", name: 'index_posts_on_date_created_at' 
add_index :posts, "LENGTH(title)", name: 'index_posts_on_title_length'

# Query (now uses index)
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

**Problem**: OR conditions prevent composite index usage.

```ruby
# ❌ Won't use composite index on (user_id, status)
Order.where(user_id: user.id)
     .where("status = 'pending' OR status = 'processing'")

# ❌ Same problem with Rails syntax
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

**Problem**: NOT conditions require scanning most of the table.

```ruby
# ❌ Scans ~95% of table even with status index
Order.where.not(status: 'canceled')
User.where.not(email: nil)
Post.where("status != 'draft'")
```

**Solutions**:

1. **Use positive conditions**:
```ruby
# ✅ Uses index efficiently
Order.where(status: ['pending', 'processing', 'shipped', 'delivered'])
User.where.not(email: nil)  # Use presence validation instead
Post.where(status: ['published', 'featured'])
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
  has_many :posts, counter_cache: true
end

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
# ❌ Loads all records then counts
User.where(active: true).count  # Can be slow with large datasets

# ✅ Database-level count
User.where(active: true).count  # Uses SQL COUNT()

# ✅ Counter caches for associations
class User < ApplicationRecord
  has_many :posts, counter_cache: true
end

user.posts_count  # No query needed

# ✅ Estimated counts for large tables (PostgreSQL)
ActiveRecord::Base.connection.execute(
  "SELECT reltuples::bigint FROM pg_class WHERE relname = 'users'"
).first['reltuples']
```

### Batching Large Operations

```ruby
# ❌ Memory explosion with large datasets
User.where(created_at: 1.year.ago..1.day.ago).update_all(status: 'inactive')

# ✅ Process in batches
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

-- Index only recent orders  
CREATE INDEX idx_recent_orders_status ON orders (status) 
WHERE created_at > NOW() - INTERVAL '30 days';

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

This database optimization guide provides the foundation for writing Rails applications that perform well at scale. Always measure before optimizing, and use EXPLAIN ANALYZE to verify that your indexes are being used effectively.