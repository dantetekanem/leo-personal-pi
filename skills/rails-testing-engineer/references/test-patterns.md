# Comprehensive Test Patterns

Detailed code examples for every type of Rails test using Minitest.

## Model Testing Patterns

### Basic Model Test Structure
```ruby
class UserTest < ActiveSupport::TestCase
  def setup
    @user = User.new(
      name: "John Doe",
      email: "john@example.com", 
      password: "password123"
    )
  end

  # Validation Testing
  test "should be valid with valid attributes" do
    assert @user.valid?
  end

  test "should require email presence" do
    @user.email = nil
    assert_not @user.valid?
    assert_includes @user.errors[:email], "can't be blank"
  end

  test "should validate email format" do
    invalid_emails = ["invalid", "@example.com", "test@", "test..test@example.com"]
    
    invalid_emails.each do |email|
      @user.email = email
      assert_not @user.valid?, "#{email} should be invalid"
      assert_includes @user.errors[:email], "is invalid"
    end
  end

  test "should validate email uniqueness" do
    @user.save!
    duplicate = User.new(name: "Jane", email: @user.email, password: "pass")
    
    assert_not duplicate.valid?
    assert_includes duplicate.errors[:email], "has already been taken"
  end

  test "should validate password length" do
    @user.password = "short"
    assert_not @user.valid?
    assert_includes @user.errors[:password], "is too short (minimum is 8 characters)"
  end

  # Association Testing
  test "should have many posts" do
    assert_respond_to @user, :posts
    assert_instance_of ActiveRecord::Associations::CollectionProxy, @user.posts
  end

  test "should destroy dependent posts" do
    @user.save!
    post1 = @user.posts.create!(title: "Test 1", body: "Content")
    post2 = @user.posts.create!(title: "Test 2", body: "Content")
    
    assert_difference 'Post.count', -2 do
      @user.destroy
    end
  end

  test "should belong to account" do
    account = Account.create!(name: "Test Account")
    @user.account = account
    @user.save!
    
    assert_equal account, @user.account
    assert_includes account.users, @user
  end

  # Custom Method Testing
  test "display_name returns name when present" do
    @user.name = "John Doe"
    assert_equal "John Doe", @user.display_name
  end

  test "display_name returns email when name blank" do
    @user.name = ""
    assert_equal "john@example.com", @user.display_name
    
    @user.name = nil
    assert_equal "john@example.com", @user.display_name
  end

  test "full_name combines first and last name" do
    @user.first_name = "John"
    @user.last_name = "Doe"
    assert_equal "John Doe", @user.full_name
  end

  test "initials returns first letter of each name part" do
    @user.name = "John Michael Doe"
    assert_equal "JMD", @user.initials
    
    @user.name = "Single"
    assert_equal "S", @user.initials
  end

  # Scope Testing
  test "active scope returns recently active users" do
    active_user = User.create!(
      name: "Active", 
      email: "active@test.com", 
      password: "password",
      last_sign_in_at: 1.day.ago
    )
    
    inactive_user = User.create!(
      name: "Inactive",
      email: "inactive@test.com", 
      password: "password",
      last_sign_in_at: 2.months.ago
    )
    
    assert_includes User.active, active_user
    assert_not_includes User.active, inactive_user
  end

  test "by_role scope filters by role" do
    admin = User.create!(name: "Admin", email: "admin@test.com", password: "pass", role: "admin")
    user = User.create!(name: "User", email: "user@test.com", password: "pass", role: "user")
    
    assert_includes User.by_role("admin"), admin
    assert_not_includes User.by_role("admin"), user
  end

  # Callback Testing
  test "should generate slug after create" do
    @user.name = "John Michael Doe"
    assert_nil @user.slug
    
    @user.save!
    assert_equal "john-michael-doe", @user.slug
  end

  test "should update slug when name changes" do
    @user.save!
    original_slug = @user.slug
    
    @user.update!(name: "Jane Smith")
    assert_not_equal original_slug, @user.slug
    assert_equal "jane-smith", @user.slug
  end

  test "should send welcome email after create" do
    assert_emails 1 do
      @user.save!
    end
    
    email = ActionMailer::Base.deliveries.last
    assert_equal [@user.email], email.to
    assert_equal "Welcome to our platform!", email.subject
  end

  # State Machine Testing (if using AASM or similar)
  test "should start in pending state" do
    assert_equal "pending", @user.status
    assert @user.pending?
  end

  test "should transition from pending to active" do
    @user.save!
    assert @user.may_activate?
    
    @user.activate!
    assert @user.active?
    assert_not @user.pending?
  end

  test "should not transition from active to pending" do
    @user.save!
    @user.activate!
    
    assert_not @user.may_pend?
  end

  # Complex Business Logic Testing
  test "should calculate subscription end date" do
    @user.subscription_type = "monthly"
    @user.subscription_started_at = Date.parse("2024-01-15")
    
    assert_equal Date.parse("2024-02-15"), @user.subscription_end_date
    
    @user.subscription_type = "yearly"
    assert_equal Date.parse("2025-01-15"), @user.subscription_end_date
  end

  test "should determine if subscription is active" do
    travel_to Date.parse("2024-01-20") do
      @user.subscription_started_at = Date.parse("2024-01-01")
      @user.subscription_type = "monthly"
      
      assert @user.subscription_active?
      
      travel 2.months do
        assert_not @user.subscription_active?
      end
    end
  end
end
```

## Controller Testing Patterns

### Basic Controller Structure
```ruby
class PostsControllerTest < ActionDispatch::IntegrationTest
  def setup
    @user = users(:john)
    @admin = users(:admin)
    @post = posts(:published)
    @draft = posts(:draft)
  end

  # Index Action Testing
  test "should get index" do
    get posts_path
    assert_response :success
    assert_select 'h1', 'All Posts'
    assert_select '.post-card', Post.published.count
  end

  test "should show only published posts to visitors" do
    get posts_path
    assert_response :success
    
    assert_select '.post-card', text: @post.title
    assert_select '.post-card', { text: @draft.title, count: 0 }
  end

  test "should show draft posts to authors" do
    sign_in @draft.author
    get posts_path
    
    assert_select '.post-card', text: @draft.title
  end

  # Show Action Testing
  test "should show published post" do
    get post_path(@post)
    assert_response :success
    assert_select 'h1', @post.title
    assert_select '.post-body', text: @post.body
  end

  test "should not show draft post to visitors" do
    get post_path(@draft)
    assert_response :not_found
  end

  test "should show draft post to author" do
    sign_in @draft.author
    get post_path(@draft)
    assert_response :success
  end

  # Create Action Testing
  test "should create post when authenticated" do
    sign_in @user
    
    assert_difference 'Post.count' do
      post posts_path, params: {
        post: { title: "New Post", body: "Great content", published: true }
      }
    end
    
    assert_redirected_to post_path(Post.last)
    assert_equal "Post was successfully created.", flash[:notice]
    assert_equal @user, Post.last.author
  end

  test "should redirect to login when not authenticated" do
    post posts_path, params: {
      post: { title: "New Post", body: "Content" }
    }
    
    assert_redirected_to login_path
    assert_equal "Please sign in to continue.", flash[:alert]
  end

  test "should show validation errors for invalid post" do
    sign_in @user
    
    assert_no_difference 'Post.count' do
      post posts_path, params: {
        post: { title: "", body: "No title" }
      }
    end
    
    assert_response :unprocessable_entity
    assert_select '.field_with_errors', text: /Title/
    assert_select '.error-message', text: /Title can't be blank/
  end

  # Update Action Testing
  test "should update own post" do
    sign_in @post.author
    
    patch post_path(@post), params: {
      post: { title: "Updated Title" }
    }
    
    assert_redirected_to post_path(@post)
    assert_equal "Post was successfully updated.", flash[:notice]
    assert_equal "Updated Title", @post.reload.title
  end

  test "should not update other user's post" do
    sign_in @user # Different from @post.author
    
    patch post_path(@post), params: {
      post: { title: "Hacked Title" }
    }
    
    assert_response :forbidden
    assert_not_equal "Hacked Title", @post.reload.title
  end

  test "should allow admin to update any post" do
    sign_in @admin
    
    patch post_path(@post), params: {
      post: { title: "Admin Updated" }
    }
    
    assert_redirected_to post_path(@post)
    assert_equal "Admin Updated", @post.reload.title
  end

  # Destroy Action Testing
  test "should destroy own post" do
    sign_in @post.author
    
    assert_difference 'Post.count', -1 do
      delete post_path(@post)
    end
    
    assert_redirected_to posts_path
    assert_equal "Post was successfully deleted.", flash[:notice]
  end

  test "should not destroy other user's post" do
    sign_in @user
    
    assert_no_difference 'Post.count' do
      delete post_path(@post)
    end
    
    assert_response :forbidden
  end

  # Search and Filtering
  test "should filter posts by tag" do
    rails_tag = tags(:rails)
    ruby_tag = tags(:ruby)
    
    rails_post = Post.create!(title: "Rails Post", body: "Content", tags: [rails_tag], published: true)
    ruby_post = Post.create!(title: "Ruby Post", body: "Content", tags: [ruby_tag], published: true)
    
    get posts_path, params: { tag: rails_tag.name }
    
    assert_response :success
    assert_select '.post-card', text: rails_post.title
    assert_select '.post-card', { text: ruby_post.title, count: 0 }
  end

  test "should search posts by title and body" do
    searchable_post = Post.create!(
      title: "Rails Testing Guide", 
      body: "Comprehensive Minitest examples",
      published: true
    )
    
    get posts_path, params: { search: "testing" }
    
    assert_response :success
    assert_select '.post-card', text: searchable_post.title
  end

  # Format-Specific Testing
  test "should return JSON format" do
    get posts_path, headers: { 'Accept' => 'application/json' }
    
    assert_response :success
    assert_equal 'application/json', response.media_type
    
    json = JSON.parse(response.body)
    assert_instance_of Array, json['posts']
    assert_equal Post.published.count, json['posts'].length
  end

  test "should return XML format" do
    get posts_path(format: :xml)
    
    assert_response :success
    assert_equal 'application/xml', response.media_type
    assert_match /<posts>/, response.body
  end

  # Error Handling
  test "should handle non-existent post gracefully" do
    get post_path(id: 999999)
    assert_response :not_found
  end

  test "should handle invalid post ID" do
    get post_path(id: "invalid")
    assert_response :not_found
  end

  private

  def sign_in(user)
    post login_path, params: { 
      session: { email: user.email, password: 'password' } 
    }
  end
end
```

## Integration Testing Patterns

### User Journey Testing
```ruby
class UserJourneyTest < ActionDispatch::IntegrationTest
  test "complete signup to first post workflow" do
    # Step 1: Visit signup page
    get signup_path
    assert_response :success
    assert_select 'h1', 'Sign Up'

    # Step 2: Submit valid signup
    assert_difference 'User.count' do
      post users_path, params: {
        user: {
          name: "New User",
          email: "newuser@example.com",
          password: "password123",
          password_confirmation: "password123"
        }
      }
    end

    assert_redirected_to dashboard_path
    user = User.find_by(email: "newuser@example.com")
    assert user.persisted?

    # Step 3: Verify welcome email sent
    email = ActionMailer::Base.deliveries.last
    assert_equal [user.email], email.to
    assert_equal "Welcome to our platform!", email.subject

    # Step 4: Follow redirect to dashboard
    follow_redirect!
    assert_response :success
    assert_select '.welcome-message', text: /Welcome, New User/

    # Step 5: Create first post
    click_link "Write Your First Post"
    assert_current_path new_post_path

    post posts_path, params: {
      post: {
        title: "My First Post",
        body: "This is my introduction to the platform!",
        published: true
      }
    }

    # Step 6: Verify post creation and redirect
    assert_redirected_to post_path(Post.last)
    created_post = Post.last
    assert_equal user, created_post.author
    assert_equal "My First Post", created_post.title

    # Step 7: Verify post appears in user's profile
    get user_path(user)
    assert_response :success
    assert_select '.user-posts .post-title', text: "My First Post"

    # Step 8: Verify post appears in public feed
    get posts_path
    assert_select '.post-card .title', text: "My First Post"
  end

  test "shopping cart to checkout workflow" do
    product1 = products(:book)
    product2 = products(:course)
    
    # Add items to cart
    post cart_items_path, params: { product_id: product1.id, quantity: 2 }
    assert_response :created
    
    post cart_items_path, params: { product_id: product2.id, quantity: 1 }
    assert_response :created
    
    # View cart
    get cart_path
    assert_response :success
    assert_select '.cart-item', count: 2
    assert_select '.cart-total', text: /\$#{product1.price * 2 + product2.price}/
    
    # Proceed to checkout
    post checkout_path
    assert_redirected_to new_user_session_path # Requires authentication
    
    # Sign up/in and retry checkout
    sign_up_user("customer@example.com", "password123")
    post checkout_path
    assert_redirected_to checkout_payment_path
    
    # Complete payment
    follow_redirect!
    post checkout_payment_path, params: {
      payment: {
        card_number: "4242424242424242",
        exp_month: "12",
        exp_year: "2025",
        cvc: "123"
      }
    }
    
    assert_redirected_to order_path(Order.last)
    
    # Verify order created
    order = Order.last
    assert_equal 2, order.order_items.count
    assert order.paid?
  end

  test "admin content moderation workflow" do
    admin = users(:admin)
    reporter = users(:reporter)
    author = users(:author)
    
    # Regular user creates potentially problematic post
    post = Post.create!(
      title: "Controversial Topic",
      body: "This might be inappropriate content...",
      author: author,
      published: true
    )
    
    # Another user reports the post
    sign_in reporter
    post post_reports_path, params: {
      report: {
        post_id: post.id,
        reason: "inappropriate_content",
        details: "Contains offensive language"
      }
    }
    assert_response :created
    
    # Admin reviews reported posts
    sign_in admin
    get admin_reports_path
    assert_response :success
    assert_select '.report-item', count: 1
    assert_select '.report-details', text: /Contains offensive language/
    
    # Admin takes action - hide post
    patch admin_post_path(post), params: {
      post: { status: 'hidden' }
    }
    assert_redirected_to admin_posts_path
    
    # Verify post hidden from public view
    sign_out
    get post_path(post)
    assert_response :not_found
    
    # Verify author can still see it with notice
    sign_in author
    get post_path(post)
    assert_response :success
    assert_select '.moderation-notice', text: /under review/
    
    # Admin can restore post after review
    sign_in admin
    patch admin_post_path(post), params: {
      post: { status: 'published' }
    }
    
    # Verify post visible again
    sign_out
    get post_path(post)
    assert_response :success
  end

  private

  def sign_up_user(email, password)
    post users_path, params: {
      user: {
        name: "Test User",
        email: email,
        password: password,
        password_confirmation: password
      }
    }
  end

  def sign_in(user)
    post session_path, params: {
      session: { email: user.email, password: 'password' }
    }
  end

  def sign_out
    delete session_path
  end
end
```

## Background Job Testing

### Job Performance Testing
```ruby
class WelcomeEmailJobTest < ActiveJob::TestCase
  test "should enqueue welcome email job" do
    user = users(:john)
    
    assert_enqueued_with(job: WelcomeEmailJob, args: [user]) do
      WelcomeEmailJob.perform_later(user)
    end
  end

  test "should perform job successfully" do
    user = users(:john)
    
    assert_emails 1 do
      WelcomeEmailJob.perform_now(user)
    end
    
    email = ActionMailer::Base.deliveries.last
    assert_equal [user.email], email.to
    assert_equal "Welcome to our platform!", email.subject
  end

  test "should handle job failure gracefully" do
    user = users(:john)
    
    # Mock external service failure
    UserMailer.stub :welcome, -> { raise "Service unavailable" } do
      assert_raises(StandardError) do
        WelcomeEmailJob.perform_now(user)
      end
    end
  end

  test "should retry failed jobs with exponential backoff" do
    user = users(:john)
    
    WelcomeEmailJob.stub :perform, -> { raise "Temporary failure" } do
      job = WelcomeEmailJob.new
      
      # First retry after 3 seconds
      assert_enqueued_at 3.seconds.from_now do
        job.retry_job(wait: 3.seconds)
      end
    end
  end
end

class DataProcessingJobTest < ActiveJob::TestCase
  test "should process large datasets in batches" do
    # Create test data
    users = (1..1000).map do |i|
      User.create!(
        name: "User #{i}",
        email: "user#{i}@test.com",
        password: "password"
      )
    end
    
    # Mock the batch processing
    processed_count = 0
    DataProcessingJob.stub :process_user_batch, ->(batch) { processed_count += batch.size } do
      DataProcessingJob.perform_now
    end
    
    assert_equal 1000, processed_count
  end

  test "should handle partial batch failures" do
    users = users(:john, :jane, :admin)
    
    # Simulate one user causing processing failure
    User.stub :find, ->(id) { id == users(:jane).id ? raise("Processing error") : User.find(id) } do
      result = DataProcessingJob.perform_now(users.pluck(:id))
      
      assert_equal 2, result[:success_count]
      assert_equal 1, result[:error_count]
      assert_includes result[:errors], "Processing error"
    end
  end
end
```

## System Testing Patterns

### JavaScript Interaction Testing
```ruby
class JavaScriptInteractionTest < ApplicationSystemTestCase
  test "dynamic form submission", js: true do
    user = users(:john)
    sign_in_as(user)
    
    visit posts_path
    click_on "Quick Post"
    
    # Modal should appear
    assert_selector "#quick-post-modal", visible: true
    
    within "#quick-post-modal" do
      fill_in "Title", with: "Quick Post Title"
      fill_in "Body", with: "This was created via the quick post modal"
      click_button "Publish"
    end
    
    # Wait for AJAX submission
    assert_text "Quick Post Title", wait: 5
    assert_no_selector "#quick-post-modal"
    
    # Verify post was created
    assert Post.exists?(title: "Quick Post Title")
  end

  test "infinite scroll loading", js: true do
    # Create enough posts to trigger pagination
    user = users(:john)
    posts = (1..25).map do |i|
      Post.create!(
        title: "Post #{i}",
        body: "Content for post #{i}",
        author: user,
        published: true
      )
    end
    
    visit posts_path
    
    # Initially shows first 10 posts
    assert_selector '.post-card', count: 10
    
    # Scroll to bottom
    page.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    
    # Wait for more posts to load
    assert_selector '.post-card', count: 20, wait: 5
    
    # Scroll again
    page.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    assert_selector '.post-card', count: 25, wait: 5
  end

  test "real-time notifications", js: true do
    user = users(:john)
    other_user = users(:jane)
    sign_in_as(user)
    
    visit dashboard_path
    
    # Simulate notification from another user in separate thread
    Thread.new do
      sleep 1 # Wait for page to load
      Notification.create!(
        recipient: user,
        sender: other_user,
        message: "#{other_user.name} mentioned you in a comment",
        notification_type: 'mention'
      )
      
      # Broadcast via ActionCable
      ActionCable.server.broadcast(
        "notifications_#{user.id}",
        {
          message: "#{other_user.name} mentioned you in a comment",
          type: 'mention'
        }
      )
    end
    
    # Wait for notification to appear via ActionCable
    assert_text "#{other_user.name} mentioned you", wait: 5
    assert_selector '.notification-badge', text: '1'
  end

  test "drag and drop file upload", js: true do
    user = users(:john)
    sign_in_as(user)
    
    visit new_post_path
    
    # Create a test file
    attach_file "post[featured_image]", Rails.root.join('test', 'fixtures', 'files', 'test_image.jpg')
    
    # Verify preview appears
    assert_selector '.image-preview img[src*="test_image.jpg"]'
    
    fill_in "Title", with: "Post with Image"
    fill_in "Body", with: "This post has a featured image"
    click_button "Create Post"
    
    assert_text "Post was successfully created"
    
    # Verify image was uploaded and attached
    post = Post.last
    assert post.featured_image.attached?
  end

  test "keyboard navigation", js: true do
    visit posts_path
    
    # Tab through navigation
    find('body').send_keys(:tab) # Focus first element
    assert_equal 'Home', page.evaluate_script('document.activeElement.textContent')
    
    find('body').send_keys(:tab)
    assert_equal 'Posts', page.evaluate_script('document.activeElement.textContent')
    
    # Test keyboard shortcuts
    find('body').send_keys([:control, 'k']) # Ctrl+K for search
    assert_selector '#search-modal', visible: true
    
    find('body').send_keys(:escape) # Escape to close
    assert_no_selector '#search-modal'
  end

  private

  def sign_in_as(user)
    visit login_path
    fill_in "Email", with: user.email
    fill_in "Password", with: "password"
    click_button "Sign In"
    assert_text "Successfully signed in"
  end
end
```

## Performance and Benchmark Testing

### Response Time Testing
```ruby
class PerformanceTest < ActionDispatch::IntegrationTest
  test "homepage loads quickly" do
    start_time = Time.current
    
    get root_path
    
    response_time = Time.current - start_time
    assert response_time < 0.5, "Homepage took #{response_time}s, expected < 0.5s"
  end

  test "search results load efficiently" do
    # Create test data
    100.times do |i|
      Post.create!(
        title: "Post #{i} with searchable content",
        body: "This is test content for search functionality",
        published: true,
        author: users(:john)
      )
    end
    
    start_time = Time.current
    get posts_path, params: { search: "searchable" }
    response_time = Time.current - start_time
    
    assert_response :success
    assert response_time < 1.0, "Search took #{response_time}s, expected < 1s"
    
    # Verify reasonable number of queries
    assert_operator ActiveRecord::Base.connection.query_cache.size, :<, 5
  end
end

class DatabasePerformanceTest < ActiveSupport::TestCase
  test "bulk user creation performance" do
    result = Benchmark.measure do
      User.transaction do
        1000.times do |i|
          User.create!(
            name: "User #{i}",
            email: "user#{i}@test.com",
            password: "password123"
          )
        end
      end
    end
    
    assert result.real < 2.0, "Bulk creation took #{result.real}s, expected < 2s"
  end

  test "complex query performance" do
    # Setup: Create users with posts and comments
    users = Array.new(50) do |i|
      User.create!(name: "User #{i}", email: "user#{i}@test.com", password: "pass")
    end
    
    users.each do |user|
      5.times do |j|
        post = user.posts.create!(title: "Post #{j}", body: "Content", published: true)
        10.times { |k| post.comments.create!(body: "Comment #{k}", author: users.sample) }
      end
    end
    
    # Test the complex query
    result = Benchmark.measure do
      User.joins(posts: :comments)
          .where(posts: { published: true })
          .where(comments: { created_at: 1.week.ago.. })
          .group('users.id')
          .having('COUNT(comments.id) > ?', 5)
          .limit(20)
          .to_a
    end
    
    assert result.real < 0.1, "Complex query took #{result.real}s, expected < 0.1s"
  end
end
```

This comprehensive guide covers all the major testing patterns you'll need for Rails applications using Minitest. Each pattern includes realistic examples and focuses on testing behavior rather than implementation details.