# Rails 8 Features Reference

Comprehensive guide to Rails 8 features, patterns, and migration strategies.

## The Solid Trifecta: Database-Backed Infrastructure

Rails 8 introduces three database-backed components that eliminate external dependencies like Redis and Memcached.

### Solid Queue: Job Processing

**Replaces**: Sidekiq, Resque, Delayed Job, and Redis for job queues.

**Installation**:
```ruby
# Gemfile (included by default in Rails 8)
gem 'solid_queue'

# Generate migration
rails generate solid_queue:install

# Run migration
rails db:migrate
```

**Configuration**:
```ruby
# config/environments/production.rb
config.active_job.queue_adapter = :solid_queue

# config/queue.yml
production:
  dispatchers:
    - polling_interval: 1
      batch_size: 500
  workers:
    - queues: "default,background,reports"
      threads: 5
    - queues: "low_priority"  
      threads: 2
      processes: 1
```

**Basic Usage**:
```ruby
class UserNotificationJob < ApplicationJob
  queue_as :notifications
  
  def perform(user_id, message)
    user = User.find(user_id)
    UserMailer.notification(user, message).deliver_now
  end
end

# Enqueue job
UserNotificationJob.perform_later(user.id, "Welcome!")

# Scheduled jobs  
UserNotificationJob.set(wait: 1.hour).perform_later(user.id, "Reminder")
```

**Advanced Features**:
```ruby
# Recurring jobs
class DailySummaryJob < ApplicationJob
  include Solid::Queue::RecurringTask
  
  recurring_schedule "0 9 * * *"  # Every day at 9 AM
  
  def perform
    # Generate daily summary
  end
end

# Job priorities
class UrgentJob < ApplicationJob  
  queue_as :urgent, priority: 10  # Higher number = higher priority
end

# Bulk enqueue
UserNotificationJob.perform_all_later([
  [user1.id, "Message 1"],
  [user2.id, "Message 2"],  
  [user3.id, "Message 3"]
])
```

**Performance Tuning**:
```ruby
# config/queue.yml - High throughput setup
production:
  dispatchers:
    - polling_interval: 0.1  # Fast polling
      batch_size: 1000       # Large batches
  workers:
    - queues: "*"
      threads: 10            # More threads per worker
      processes: 4           # Multiple worker processes
```

### Solid Cache: Fragment Caching

**Replaces**: Redis, Memcached for Rails caching.

**Installation & Configuration**:
```ruby
# config/environments/production.rb
config.cache_store = :solid_cache_store

# config/cache.yml
production:
  store_options:
    max_age: 2.weeks
    max_entries: 1_000_000
    cluster:
      shards: 4  # Distribute across multiple cache tables
```

**Usage Patterns**:
```ruby
# Basic caching
Rails.cache.fetch("user_stats_#{user.id}", expires_in: 1.hour) do
  user.calculate_expensive_stats
end

# Fragment caching in views
<% cache ["user_profile", user, user.updated_at] do %>
  <%= render "user_profile", user: user %>
<% end %>

# Collection caching
<% cache @posts do %>
  <% @posts.each do |post| %>
    <% cache post do %>
      <%= render post %>
    <% end %>
  <% end %>
<% end %>
```

**Advanced Caching Patterns**:
```ruby
# Conditional caching
Rails.cache.fetch("heavy_computation", skip: Rails.env.development?) do
  perform_heavy_computation
end

# Cache with custom expiry
class UserStatsCache
  def self.fetch(user_id)
    Rails.cache.fetch(
      "user_stats/#{user_id}",
      expires_in: user_cache_duration(user_id),
      race_condition_ttl: 30.seconds
    ) do
      User.find(user_id).calculate_stats
    end
  end
  
  private
  
  def self.user_cache_duration(user_id)
    # Premium users get longer cache
    User.find(user_id).premium? ? 1.hour : 15.minutes
  end
end
```

### Solid Cable: WebSocket Pubsub

**Replaces**: Redis for ActionCable message routing.

**Configuration**:
```ruby
# config/cable.yml
production:
  adapter: solid_cable
  
  # Optional: message retention
  message_retention: 1.day
  
  # Optional: polling interval
  polling_interval: 0.1
```

**Channel Examples**:
```ruby
class ChatChannel < ApplicationCable::Channel
  def subscribed
    stream_from "chat_#{params[:room_id]}"
  end
  
  def receive(data)
    # Broadcast to all subscribers
    ActionCable.server.broadcast(
      "chat_#{params[:room_id]}", 
      data.merge(user: current_user.name)
    )
  end
  
  def unsubscribed
    # Cleanup when disconnected
  end
end

# Broadcasting from controllers/models
class MessagesController < ApplicationController
  def create
    @message = current_user.messages.build(message_params)
    
    if @message.save
      ActionCable.server.broadcast(
        "chat_#{@message.room_id}",
        message: @message.content,
        user: @message.user.name,
        timestamp: @message.created_at
      )
    end
  end
end
```

**Client-side Integration**:
```javascript
// app/javascript/channels/chat_channel.js
import consumer from "channels/consumer"

const chatChannel = consumer.subscriptions.create(
  { channel: "ChatChannel", room_id: roomId },
  {
    connected() {
      console.log("Connected to chat room")
    },

    disconnected() {
      console.log("Disconnected from chat room")
    },

    received(data) {
      // Handle incoming messages
      appendMessage(data.message, data.user)
    },

    send(message) {
      this.perform('receive', { message: message })
    }
  }
)
```

## Authentication Generator

Rails 8 includes a built-in authentication system generator.

**Generation**:
```bash
# Generate complete authentication system
rails generate authentication

# Or specify user model name
rails generate authentication User
```

**Generated Components**:
```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_secure_password
  
  validates :email, presence: true, uniqueness: { case_sensitive: false }
  validates :password, length: { minimum: 8 }, confirmation: true
  
  before_save :downcase_email
  
  generates_token_for :email_confirmation, expires_in: 1.hour
  generates_token_for :password_reset, expires_in: 20.minutes
  
  private
  
  def downcase_email
    self.email = email&.downcase
  end
end

# app/controllers/sessions_controller.rb
class SessionsController < ApplicationController
  def new
  end
  
  def create
    user = User.find_by(email: params[:email]&.downcase)
    
    if user&.authenticate(params[:password])
      login(user)
      redirect_to root_path, notice: "Signed in successfully"
    else
      flash.now[:alert] = "Invalid email or password"
      render :new, status: :unprocessable_entity
    end
  end
  
  def destroy
    logout
    redirect_to root_path, notice: "Signed out successfully"  
  end
end
```

**Generated Helpers**:
```ruby
# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  before_action :authenticate
  
  private
  
  def authenticate
    redirect_to new_session_path unless authenticated?
  end
  
  def authenticated?
    !!current_user
  end
  
  def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end
  
  def login(user)
    session[:user_id] = user.id
  end
  
  def logout
    session[:user_id] = nil
  end
end
```

**Password Reset Flow**:
```ruby
# app/controllers/password_resets_controller.rb  
class PasswordResetsController < ApplicationController
  def new
  end
  
  def create
    if user = User.find_by(email: params[:email]&.downcase)
      UserMailer.password_reset(user).deliver_later
    end
    
    # Always show success to prevent email enumeration
    redirect_to new_session_path, notice: "Password reset instructions sent"
  end
  
  def edit
    @user = User.find_by_token_for(:password_reset, params[:token])
    redirect_to new_password_reset_path unless @user
  end
  
  def update
    @user = User.find_by_token_for(:password_reset, params[:token])
    
    if @user&.update(password_params)
      login(@user)
      redirect_to root_path, notice: "Password reset successfully"
    else
      render :edit, status: :unprocessable_entity
    end
  end
end
```

## Parameter Handling: params.expect()

**Replaces**: `params.require().permit()` with a more intuitive API.

**Old Pattern**:
```ruby
def user_params
  params.require(:user).permit(:name, :email, :age, address: [:street, :city])
end
```

**New Pattern**:
```ruby
def user_params
  params.expect(user: [:name, :email, :age, address: [:street, :city]])
end

# Equivalent to above
def user_params  
  params.expect(user: { name: true, email: true, age: true, address: [:street, :city] })
end
```

**Advanced Examples**:
```ruby
# Multiple top-level keys
def post_params
  params.expect(post: [:title, :content], meta: [:tags, :category])
end

# Nested arrays
def order_params
  params.expect(order: [
    :total, 
    :customer_id,
    items: [:product_id, :quantity, :price]
  ])
end

# Optional parameters with defaults
def search_params
  params.expect(
    q: true,
    page: true,
    filters: [:category, :price_range, :availability]
  ).with_defaults(page: 1, filters: {})
end

# Conditional expectations
def user_params
  expected = [:name, :email]
  expected << :admin if current_user.admin?
  
  params.expect(user: expected)
end
```

**Type Coercion**:
```ruby
# params.expect automatically handles type conversion
params.expect(
  page: Integer,      # Converts to integer
  published: Boolean, # Converts to true/false
  tags: Array        # Ensures array format
)
```

## Propshaft: New Asset Pipeline

**Replaces**: Sprockets as the default asset pipeline.

**Key Differences**:
- No asset compilation - serves source files directly in development
- Simpler manifest system
- Better HTTP/2 support
- Faster development builds

**Configuration**:
```ruby
# config/application.rb
module MyApp
  class Application < Rails::Application
    config.assets.pipeline = :propshaft  # Default in Rails 8
  end
end

# config/environments/production.rb
config.assets.compile = false
config.assets.precompile += %w( admin.js admin.css )
```

**Asset Organization**:
```
app/assets/
  stylesheets/
    application.css      # Main stylesheet
    components/         # Component-specific styles
      nav.css
      forms.css
  javascripts/
    application.js      # Main JavaScript
    controllers/        # Stimulus controllers
      hello_controller.js
    libs/              # Third-party libraries
      chart.js
```

**Import Maps Integration**:
```ruby
# config/importmap.rb
pin "application"
pin "turbo-rails"
pin "stimulus"
pin "stimulus-loading", to: "stimulus-loading.js"

# Pin third-party libraries
pin "chart.js", to: "libs/chart.js"
```

```javascript
// app/javascript/application.js
import "turbo-rails"
import "stimulus"
import { Chart } from "chart.js"
```

## Kamal 2 + Thruster Deployment

**Kamal 2**: Zero-downtime deployment tool built into Rails 8.

**Setup**:
```bash
# Initialize Kamal configuration
rails generate kamal:install

# Deploy
kamal deploy

# Check status
kamal app status
```

**Configuration**:
```yaml
# config/deploy.yml
service: myapp
image: myapp

servers:
  web:
    hosts:
      - 192.168.1.100
      - 192.168.1.101
    labels:
      traefik.http.routers.myapp.rule: Host(`example.com`)

registry:
  server: registry.digitalocean.com/myregistry
  username: myusername

env:
  clear:
    DB_HOST: mydb.example.com
  secret:
    - RAILS_MASTER_KEY
```

**Thruster**: Application proxy included with Rails 8.

**Features**:
- X-Sendfile acceleration for large file downloads
- Asset caching and compression
- Request buffering
- HTTP/2 support

**Configuration**:
```ruby
# config/environments/production.rb
config.force_ssl = true
config.assume_ssl = true

# Thruster handles these automatically:
# - Asset compression
# - Cache headers
# - X-Sendfile acceleration
```

## Security Improvements

### Regexp Timeout Protection

**Automatic DoS Protection**:
```ruby
# Rails 8 default: 1 second timeout
Regexp.timeout = 1.0

# Protects against catastrophic backtracking
user_input = params[:search]
pattern = /^(a+)+b$/

begin
  user_input.match?(pattern)
rescue Regexp::TimeoutError
  # Handle timeout gracefully
  render json: { error: "Search pattern too complex" }, status: 400
end
```

### Enhanced CSRF Protection

```ruby
# app/controllers/application_controller.rb
protect_from_forgery with: :exception

# API endpoints can skip CSRF
class Api::V1::BaseController < ApplicationController
  skip_before_action :verify_authenticity_token
  before_action :authenticate_api_user
end
```

## Performance Optimizations

### Database Schema Loading

Rails 8 optimizes fresh database setup by loading schema before running migrations:

```bash
# On fresh database, Rails 8 now:
# 1. Loads db/schema.rb  
# 2. Runs only new migrations

# Faster than running all migrations from scratch
```

### Improved Asset Handling

```ruby
# Propshaft enables better caching
# Static assets served with optimal headers
# Development mode serves source files directly
```

## Migration Guide from Rails 7

### Upgrading Existing Applications

**1. Update Gemfile**:
```ruby
gem 'rails', '~> 8.0'

# Add Solid gems if wanted
gem 'solid_queue'
gem 'solid_cache'  
gem 'solid_cable'
```

**2. Replace Redis Dependencies** (Optional):
```ruby
# Remove from Gemfile
# gem 'sidekiq'
# gem 'redis'

# Update configuration
# config/environments/production.rb
config.active_job.queue_adapter = :solid_queue
config.cache_store = :solid_cache_store
config.action_cable.adapter = :solid_cable
```

**3. Update Parameter Handling**:
```ruby
# Replace gradually
def old_params
  params.require(:user).permit(:name, :email)
end

def new_params  
  params.expect(user: [:name, :email])
end
```

**4. Asset Pipeline Migration**:
```ruby
# config/application.rb
config.assets.pipeline = :propshaft

# Update asset organization as needed
# Test all asset loading in production environment
```

### Gradual Adoption Strategy

1. **Start with params.expect()** - Easy wins, no infrastructure changes
2. **Add Solid Queue** - Replace job processing gradually  
3. **Migrate to Solid Cache** - Replace caching layer
4. **Switch to Solid Cable** - Replace ActionCable adapter
5. **Adopt Propshaft** - Asset pipeline migration last

Rails 8 represents a maturation of Rails' philosophy: simplicity, convention over configuration, and integrated solutions over external dependencies. The Solid suite and other improvements reduce operational complexity while maintaining Rails' developer-friendly approach.