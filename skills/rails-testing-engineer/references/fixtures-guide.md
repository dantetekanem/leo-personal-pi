# Complete Fixtures Guide

Comprehensive guide to using Rails fixtures effectively for fast, maintainable test suites.

## Why Fixtures Over Factories?

### Performance Comparison
```ruby
# Factory approach (slow)
Benchmark.measure do
  1000.times { create(:user_with_posts) }
end
# => ~15 seconds

# Fixture approach (fast)  
Benchmark.measure do
  1000.times { users(:john) }
end
# => ~0.3 seconds (50x faster!)
```

### Key Advantages
- **Speed**: Loaded once at suite start via bulk SQL INSERT
- **Referential Integrity**: Automatic foreign key resolution
- **Real Data**: Forces thinking about valid data structures
- **Memory Efficient**: Shared across all tests
- **Rails Native**: No external dependencies

## Basic Fixture Structure

### Simple Model Fixtures
```yaml
# test/fixtures/users.yml
john:
  name: "John Doe"
  email: "john@example.com"
  password_digest: "<%= BCrypt::Password.create('password') %>"
  role: "user"
  active: true
  created_at: <%= 1.month.ago %>

jane:
  name: "Jane Smith"
  email: "jane@example.com"
  password_digest: "<%= BCrypt::Password.create('password') %>"
  role: "admin"
  active: true
  created_at: <%= 3.weeks.ago %>

inactive_user:
  name: "Inactive User"
  email: "inactive@example.com"
  password_digest: "<%= BCrypt::Password.create('password') %>"
  role: "user"
  active: false
  last_sign_in_at: <%= 3.months.ago %>
```

### Using ERB in Fixtures
```yaml
# test/fixtures/posts.yml
<% 10.times do |i| %>
bulk_post_<%= i %>:
  title: "Bulk Post <%= i + 1 %>"
  body: "This is auto-generated content for post <%= i + 1 %>"
  author: john
  published: <%= [true, false].sample %>
  created_at: <%= i.days.ago %>
<% end %>

featured_post:
  title: "Featured Article"
  body: "This is a featured post that appears on the homepage"
  author: jane
  published: true
  featured: true
  published_at: <%= 1.week.ago %>
  view_count: 1250
```

## Association Handling

### Belongs To Associations
```yaml
# test/fixtures/posts.yml
johns_first_post:
  title: "Getting Started with Rails"
  body: "This is my first post about Rails development"
  author: john  # References users fixture
  category: programming  # References categories fixture
  published: true

# test/fixtures/comments.yml  
helpful_comment:
  body: "This was really helpful, thanks!"
  author: jane
  post: johns_first_post  # References posts fixture
  created_at: <%= 2.days.ago %>
```

### Has Many Associations (Implicit)
```yaml
# test/fixtures/users.yml
prolific_author:
  name: "Prolific Writer"
  email: "prolific@example.com"
  password_digest: "<%= BCrypt::Password.create('password') %>"

# test/fixtures/posts.yml
post_one:
  title: "First Post"
  author: prolific_author
  
post_two:
  title: "Second Post"  
  author: prolific_author

post_three:
  title: "Third Post"
  author: prolific_author

# In tests: users(:prolific_author).posts will include all three posts
```

### Many-to-Many Associations
```yaml
# test/fixtures/posts.yml
tagged_post:
  title: "Post with Multiple Tags"
  body: "This post covers Ruby and Rails"
  author: john

# test/fixtures/tags.yml
ruby:
  name: "ruby"
  description: "Ruby programming language"

rails:
  name: "rails" 
  description: "Ruby on Rails framework"

testing:
  name: "testing"
  description: "Software testing practices"

# test/fixtures/post_tags.yml (join table)
tagged_post_ruby:
  post: tagged_post
  tag: ruby

tagged_post_rails:
  post: tagged_post
  tag: rails
```

### Polymorphic Associations
```yaml
# test/fixtures/comments.yml
post_comment:
  body: "Great post!"
  author: jane
  commentable: johns_first_post (Post)  # Explicit polymorphic reference
  created_at: <%= 1.day.ago %>

user_comment:
  body: "Nice profile!"
  author: john  
  commentable: jane (User)  # References user as commentable
  created_at: <%= 2.hours.ago %>
```

## Advanced Fixture Patterns

### Nested Attributes and Complex Objects
```yaml
# test/fixtures/users.yml
user_with_profile:
  name: "Complete User"
  email: "complete@example.com"
  password_digest: "<%= BCrypt::Password.create('password') %>"

# test/fixtures/profiles.yml  
complete_profile:
  user: user_with_profile
  bio: "I'm a Rails developer who loves testing"
  website: "https://example.com"
  location: "San Francisco, CA"
  github_username: "railsdev"
  twitter_username: "railsdev"
  avatar_url: "https://example.com/avatar.jpg"
  
# test/fixtures/addresses.yml
primary_address:
  user: user_with_profile
  address_type: "primary"
  street: "123 Main St"
  city: "San Francisco"
  state: "CA"
  zip: "94105"
  country: "USA"

billing_address:
  user: user_with_profile  
  address_type: "billing"
  street: "456 Oak Ave"
  city: "Oakland"
  state: "CA"
  zip: "94601"
  country: "USA"
```

### State Machine States
```yaml
# test/fixtures/orders.yml
pending_order:
  user: john
  total: 99.99
  status: "pending"
  created_at: <%= 1.hour.ago %>

confirmed_order:
  user: jane
  total: 149.99
  status: "confirmed"
  confirmed_at: <%= 30.minutes.ago %>
  created_at: <%= 1.hour.ago %>

shipped_order:
  user: john
  total: 75.50
  status: "shipped"
  confirmed_at: <%= 2.days.ago %>
  shipped_at: <%= 1.day.ago %>
  tracking_number: "1Z999AA1234567890"
  created_at: <%= 3.days.ago %>

delivered_order:
  user: jane
  total: 199.99
  status: "delivered"
  confirmed_at: <%= 1.week.ago %>
  shipped_at: <%= 5.days.ago %>
  delivered_at: <%= 2.days.ago %>
  created_at: <%= 1.week.ago %>
```

### Time-Based Data
```yaml
# test/fixtures/subscriptions.yml
active_monthly:
  user: john
  plan: "monthly"
  status: "active"
  started_at: <%= 15.days.ago %>
  current_period_start: <%= 15.days.ago %>
  current_period_end: <%= 15.days.from_now %>
  
active_yearly:
  user: jane
  plan: "yearly"  
  status: "active"
  started_at: <%= 2.months.ago %>
  current_period_start: <%= 2.months.ago %>
  current_period_end: <%= 10.months.from_now %>

expired_subscription:
  user: inactive_user
  plan: "monthly"
  status: "expired"
  started_at: <%= 3.months.ago %>
  current_period_start: <%= 2.months.ago %>
  current_period_end: <%= 1.month.ago %>
  canceled_at: <%= 1.month.ago %>

trial_subscription:
  user: john
  plan: "trial"
  status: "trialing"
  started_at: <%= 1.week.ago %>
  trial_ends_at: <%= 1.week.from_now %>
```

## Fixture Organization Strategies

### Domain-Based Organization
```ruby
# Keep related fixtures together, split large domains

# User-related fixtures
# test/fixtures/users.yml (core user data)
# test/fixtures/profiles.yml (extended user info)  
# test/fixtures/addresses.yml (user addresses)

# Content-related fixtures  
# test/fixtures/posts.yml (blog posts)
# test/fixtures/comments.yml (post comments)
# test/fixtures/tags.yml (content tags)
# test/fixtures/post_tags.yml (many-to-many joins)

# E-commerce fixtures
# test/fixtures/products.yml (product catalog)
# test/fixtures/orders.yml (customer orders)
# test/fixtures/order_items.yml (order line items)
# test/fixtures/payments.yml (payment records)
```

### Realistic Test Scenarios
```yaml
# test/fixtures/scenarios/blog_with_engagement.yml
# Scenario: Popular blog post with active discussion

popular_post:
  title: "The Future of Web Development"
  body: "Long detailed article about web development trends..."
  author: jane
  published: true
  featured: true
  published_at: <%= 1.week.ago %>
  view_count: 5000
  like_count: 250

# Comments showing realistic engagement patterns
first_comment:
  body: "Excellent article! I especially loved the section on performance."
  author: john
  post: popular_post
  created_at: <%= 6.days.ago %>
  like_count: 15

reply_to_first:
  body: "Thanks John! Performance is indeed crucial in modern web apps."
  author: jane  # Author replying
  post: popular_post
  parent: first_comment
  created_at: <%= 6.days.ago %>

critical_comment:
  body: "I disagree with your conclusions about framework choice."
  author: critic_user
  post: popular_post
  created_at: <%= 5.days.ago %>
  like_count: 3

supportive_reply:
  body: "I think the author makes valid points. What specifically do you disagree with?"
  author: supportive_user
  post: popular_post
  parent: critical_comment
  created_at: <%= 5.days.ago %>
  like_count: 8
```

## Testing with Fixtures

### Basic Fixture Usage
```ruby
class PostTest < ActiveSupport::TestCase
  test "should belong to author" do
    post = posts(:johns_first_post)
    author = users(:john)
    
    assert_equal author, post.author
    assert_includes author.posts, post
  end

  test "published scope includes published posts" do
    published = posts(:johns_first_post)
    draft = posts(:draft_post)
    
    assert_includes Post.published, published
    assert_not_includes Post.published, draft
  end

  test "should calculate reading time" do
    long_post = posts(:long_article)
    short_post = posts(:short_note)
    
    assert_operator long_post.reading_time, :>, 5
    assert_operator short_post.reading_time, :<, 2
  end
end
```

### Fixture Modification for Specific Tests
```ruby
class UserTest < ActiveSupport::TestCase
  test "should validate email uniqueness" do
    existing = users(:john)
    
    # Create new user with same email
    duplicate = User.new(
      name: "Different Name",
      email: existing.email,  # Same email as fixture
      password: "password123"
    )
    
    assert_not duplicate.valid?
    assert_includes duplicate.errors[:email], "has already been taken"
  end

  test "should allow email updates for same user" do
    user = users(:john)
    original_email = user.email
    
    # User can update their own email
    user.email = "newemail@example.com"
    assert user.valid?
    
    # But can't use another user's email
    user.email = users(:jane).email
    assert_not user.valid?
  end
end
```

### Combining Fixtures with Dynamic Data
```ruby
class BlogTest < ActiveSupport::TestCase
  test "should display recent posts on homepage" do
    # Use fixture for baseline data
    old_post = posts(:old_archived_post)
    recent_post = posts(:recent_published_post)
    
    # Create dynamic data for this specific test
    newer_post = Post.create!(
      title: "Brand New Post",
      body: "Hot off the press",
      author: users(:john),
      published: true,
      created_at: 1.hour.ago
    )
    
    recent_posts = Post.recent.published
    
    assert_includes recent_posts, recent_post
    assert_includes recent_posts, newer_post
    assert_not_includes recent_posts, old_post
  end
end
```

## Fixture Best Practices

### Keep Fixtures Minimal and Focused
```yaml
# ❌ Bad: Too much unnecessary data
overly_detailed_user:
  name: "John Doe"
  email: "john@example.com"  
  password_digest: "<%= BCrypt::Password.create('password') %>"
  bio: "Long biographical information that's rarely needed in tests..."
  favorite_color: "blue"
  pet_name: "Fluffy"
  shoe_size: 10
  middle_name: "Michael"
  birth_city: "Portland"
  # ... lots of rarely used fields

# ✅ Good: Essential data only
john:
  name: "John Doe"
  email: "john@example.com"
  password_digest: "<%= BCrypt::Password.create('password') %>"
  role: "user"
  active: true
```

### Use Descriptive Names
```yaml
# ❌ Bad: Generic names
user1:
  name: "User One"
  
user2:
  name: "User Two"

# ✅ Good: Descriptive, purpose-driven names  
admin_user:
  name: "Admin User"
  role: "admin"

banned_user:
  name: "Banned User"  
  status: "banned"

trial_user:
  name: "Trial User"
  subscription_status: "trial"
```

### Handle Edge Cases with Fixtures
```yaml
# test/fixtures/edge_cases.yml

# User with no posts
new_user:
  name: "Brand New User"
  email: "new@example.com"
  password_digest: "<%= BCrypt::Password.create('password') %>"
  created_at: <%= 1.day.ago %>

# User with maximum allowed posts
prolific_user:
  name: "Prolific Writer"
  email: "prolific@example.com"
  password_digest: "<%= BCrypt::Password.create('password') %>"
  posts_count: 1000

# User with special characters in name
unicode_user:
  name: "José García-López"
  email: "jose@example.com"
  password_digest: "<%= BCrypt::Password.create('password') %>"

# User with very long valid email
long_email_user:
  name: "Long Email User"
  email: "very.long.email.address.that.tests.email.field.limits@very-long-domain-name-for-testing-purposes.com"
  password_digest: "<%= BCrypt::Password.create('password') %>"
```

## Fixture Loading and Performance

### Efficient Fixture Loading
```ruby
# test/test_helper.rb
class ActiveSupport::TestCase
  # Load all fixtures - happens once at test suite start
  fixtures :all
  
  # For large test suites, be selective
  # fixtures :users, :posts, :comments
  
  # Parallel test execution
  parallelize(workers: :number_of_processors)
  
  # Transactional fixtures for isolation
  self.use_transactional_tests = true
end
```

### Fixture Dependencies and Load Order
```ruby
# Rails automatically handles dependency order, but you can be explicit:

# test/fixtures/users.yml - loaded first
# test/fixtures/posts.yml - depends on users
# test/fixtures/comments.yml - depends on posts and users  
# test/fixtures/post_tags.yml - depends on posts and tags

# Dependencies are resolved automatically through foreign key references
```

### Memory Management for Large Fixtures
```yaml
# For large datasets, use ERB loops efficiently
<% 
  # Generate realistic test data without overwhelming memory
  user_count = ENV['TEST_DATA_SIZE'] == 'large' ? 1000 : 10
  user_count.times do |i| 
%>
user_<%= i %>:
  name: "User <%= i %>"
  email: "user<%= i %>@example.com"
  password_digest: "<%= BCrypt::Password.create('password') %>"
  created_at: <%= rand(1..365).days.ago %>
<% end %>
```

## Debugging Fixtures

### Common Fixture Errors and Solutions

#### 1. Foreign Key Constraint Errors
```yaml
# ❌ Error: references non-existent user
broken_post:
  title: "Broken Post"
  author: nonexistent_user  # This will fail

# ✅ Fix: reference existing fixture
working_post:
  title: "Working Post"
  author: john  # References users(:john)
```

#### 2. Circular Dependencies
```yaml
# ❌ Circular reference problem
user_a:
  name: "User A"
  best_friend: user_b

user_b:
  name: "User B" 
  best_friend: user_a

# ✅ Solution: use after_create callbacks or separate setup
user_a:
  name: "User A"

user_b:
  name: "User B"

# Handle friendship in test setup
```

#### 3. Invalid Data Types
```yaml
# ❌ Wrong data types
bad_user:
  name: "John"
  age: "twenty-five"  # Should be integer
  active: "yes"       # Should be boolean

# ✅ Correct types
good_user:
  name: "John"
  age: 25
  active: true
```

### Fixture Inspection and Testing
```ruby
class FixtureTest < ActiveSupport::TestCase
  test "all fixtures are valid" do
    # Validate all loaded fixtures
    User.all.each do |user|
      assert user.valid?, "User fixture #{user.name} is invalid: #{user.errors.full_messages}"
    end
    
    Post.all.each do |post|
      assert post.valid?, "Post fixture #{post.title} is invalid: #{post.errors.full_messages}"
    end
  end

  test "fixture relationships are properly set up" do
    john = users(:john)
    johns_post = posts(:johns_first_post)
    
    assert_equal john, johns_post.author
    assert_includes john.posts, johns_post
  end

  test "fixture counts match expectations" do
    assert_operator User.count, :>=, 5, "Should have at least 5 test users"
    assert_operator Post.count, :>=, 10, "Should have at least 10 test posts"
  end
end
```

This comprehensive fixtures guide provides everything needed to build fast, maintainable test suites using Rails' built-in fixture system. The key is starting with fixtures for your stable, foundational data and only using factories when you need dynamic test-specific variations.