// Filter System
class FilterSystem {
  constructor() {
    this.filters = {
      search: '',
      minPrice: 0,
      maxPrice: 1000,
      category: 'all',
      availability: 'all',
      sortBy: 'featured'
    };
    
    this.init();
  }
  
  init() {
    // Initialize filter elements
    this.searchInput = document.querySelector('#search-input');
    this.minPriceInput = document.querySelector('#min-price');
    this.maxPriceInput = document.querySelector('#max-price');
    this.categorySelect = document.querySelector('#category-filter');
    this.availabilitySelect = document.querySelector('#availability-filter');
    this.sortSelect = document.querySelector('#sort-filter');
    this.activeFiltersContainer = document.querySelector('.active-filters');
    this.productsGrid = document.querySelector('.products-grid');
    
    if (!this.productsGrid) {
      console.warn('Products grid not found');
      return;
    }
    
    // Ensure images are loaded properly
    this.preloadImages();
    
    // Add event listeners
    this.addEventListeners();
    
    // Initial render
    this.renderActiveFilters();
    this.applyFilters();
  }
  
  preloadImages() {
    const productImages = document.querySelectorAll('.product-image img');
    
    productImages.forEach(img => {
      // Add loading state to product card
      const card = img.closest('.product-card');
      card.classList.add('loading');
      
      // Create loading spinner
      const spinner = document.createElement('div');
      spinner.className = 'loading-spinner';
      img.parentNode.appendChild(spinner);
      
      // Handle image load
      img.onload = () => {
        card.classList.remove('loading');
        if (spinner.parentNode) {
          spinner.parentNode.removeChild(spinner);
        }
      };
      
      // Handle image error
      img.onerror = () => {
        // Replace with placeholder image
        img.src = 'https://via.placeholder.com/500x350?text=Product+Image';
        card.classList.remove('loading');
        if (spinner.parentNode) {
          spinner.parentNode.removeChild(spinner);
        }
      };
      
      // Force load if image is cached
      if (img.complete) {
        img.onload();
      }
    });
  }
  
  addEventListeners() {
    // Search input
    this.searchInput?.addEventListener('input', debounce((e) => {
      this.filters.search = e.target.value.toLowerCase();
      this.applyFilters();
      this.renderActiveFilters();
    }, 300));
    
    // Price inputs
    this.minPriceInput?.addEventListener('change', (e) => {
      const value = parseFloat(e.target.value);
      this.filters.minPrice = isNaN(value) ? 0 : value;
      this.applyFilters();
      this.renderActiveFilters();
    });
    
    this.maxPriceInput?.addEventListener('change', (e) => {
      const value = parseFloat(e.target.value);
      this.filters.maxPrice = isNaN(value) ? 1000 : value;
      this.applyFilters();
      this.renderActiveFilters();
    });
    
    // Price range slider
    const priceRangeSlider = document.querySelector('#price-range');
    if (priceRangeSlider) {
      priceRangeSlider.addEventListener('input', (e) => {
        this.maxPriceInput.value = e.target.value;
        this.filters.maxPrice = parseFloat(e.target.value);
        this.applyFilters();
        this.renderActiveFilters();
      });
    }
    
    // Category filter
    this.categorySelect?.addEventListener('change', (e) => {
      this.filters.category = e.target.value;
      this.applyFilters();
      this.renderActiveFilters();
    });
    
    // Availability filter
    this.availabilitySelect?.addEventListener('change', (e) => {
      this.filters.availability = e.target.value;
      this.applyFilters();
      this.renderActiveFilters();
    });
    
    // Sort filter
    this.sortSelect?.addEventListener('change', (e) => {
      this.filters.sortBy = e.target.value;
      this.applyFilters();
      this.renderActiveFilters();
    });
    
    // Add product form submission
    const addProductForm = document.querySelector('#add-product-form');
    if (addProductForm) {
      addProductForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.addNewProduct(new FormData(addProductForm));
      });
    }
  }
  
  addNewProduct(formData) {
    // Create new product card
    const productCard = document.createElement('article');
    productCard.className = 'product-card animate-on-scroll';
    productCard.dataset.category = formData.get('category');
    productCard.dataset.availability = 'in-stock';
    productCard.dataset.rating = '5.0';
    
    // Get image URL (from file input or use placeholder)
    let imageUrl = 'https://via.placeholder.com/500x350?text=New+Product';
    const imageFile = formData.get('product-image');
    
    if (imageFile && imageFile.name) {
      // In a real app, you would upload the file to a server
      // For demo purposes, we'll use a placeholder
      imageUrl = URL.createObjectURL(imageFile);
    }
    
    // Create product card HTML
    productCard.innerHTML = `
      <div class="product-image">
        <img src="${imageUrl}" alt="${formData.get('product-name')}" loading="lazy">
      </div>
      <div class="product-info">
        <h3 class="product-title">${formData.get('product-name')}</h3>
        <div class="product-price" data-price="${formData.get('product-price')}">$${formData.get('product-price')}.00</div>
        <div class="product-rating" aria-label="5 out of 5 stars, 0 reviews">
          <div class="rating-stars">★★★★★</div>
          <span class="rating-count">(0)</span>
        </div>
        <p class="product-description">${formData.get('product-description')}</p>
        <a href="#" class="btn btn-primary">Rent Now</a>
      </div>
    `;
    
    // Add to products grid
    this.productsGrid.appendChild(productCard);
    
    // Apply smooth entrance animation
    setTimeout(() => {
      productCard.classList.add('animated', 'fade-up');
    }, 100);
    
    // Preload the image
    const img = productCard.querySelector('img');
    const card = productCard;
    card.classList.add('loading');
    
    // Create loading spinner
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    img.parentNode.appendChild(spinner);
    
    // Handle image load
    img.onload = () => {
      card.classList.remove('loading');
      if (spinner.parentNode) {
        spinner.parentNode.removeChild(spinner);
      }
    };
    
    // Handle image error
    img.onerror = () => {
      img.src = 'https://via.placeholder.com/500x350?text=Product+Image';
      card.classList.remove('loading');
      if (spinner.parentNode) {
        spinner.parentNode.removeChild(spinner);
      }
    };
    
    // Reset form
    addProductForm.reset();
    
    // Show success message
    const successMessage = document.createElement('div');
    successMessage.className = 'alert alert-success';
    successMessage.textContent = 'Product added successfully!';
    addProductForm.prepend(successMessage);
    
    setTimeout(() => {
      successMessage.remove();
    }, 3000);
    
    // Apply filters to include the new product
    this.applyFilters();
  }
  
  renderActiveFilters() {
    if (!this.activeFiltersContainer) return;
    
    this.activeFiltersContainer.innerHTML = '';
    
    Object.entries(this.filters).forEach(([key, value]) => {
      if (value && value !== 'all' && value !== '') {
        const tag = document.createElement('span');
        tag.className = 'filter-tag';
        
        let displayValue = value;
        if (key === 'minPrice') displayValue = `Min $${value}`;
        if (key === 'maxPrice') displayValue = `Max $${value}`;
        if (key === 'sortBy') displayValue = value.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        tag.innerHTML = `
          ${key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}: ${displayValue}
          <button onclick="filterSystem.removeFilter('${key}')">×</button>
        `;
        this.activeFiltersContainer.appendChild(tag);
      }
    });
  }
  
  removeFilter(key) {
    if (key === 'minPrice') {
      this.filters.minPrice = 0;
      if (this.minPriceInput) this.minPriceInput.value = 0;
    } else if (key === 'maxPrice') {
      this.filters.maxPrice = 1000;
      if (this.maxPriceInput) this.maxPriceInput.value = 1000;
      if (document.querySelector('#price-range')) {
        document.querySelector('#price-range').value = 1000;
      }
    } else if (key === 'search') {
      this.filters.search = '';
      if (this.searchInput) this.searchInput.value = '';
    } else {
      this.filters[key] = 'all';
      const input = document.querySelector(`#${key}-filter`);
      if (input) input.value = 'all';
    }
    
    this.applyFilters();
    this.renderActiveFilters();
  }
  
  applyFilters() {
    if (!this.productsGrid) return;
    
    const products = Array.from(this.productsGrid.children);
    let visibleCount = 0;
    
    products.forEach(product => {
      let visible = true;
      
      // Apply search filter
      if (this.filters.search) {
        const searchableContent = [
          product.querySelector('.product-title')?.textContent || '',
          product.querySelector('.product-description')?.textContent || '',
          product.dataset.category || ''
        ].join(' ').toLowerCase();
        
        visible = searchableContent.includes(this.filters.search);
      }
      
      // Apply price filter
      if (visible) {
        const priceElement = product.querySelector('.product-price');
        const price = parseFloat(priceElement?.dataset.price || priceElement?.textContent.replace(/[^0-9.]/g, ''));
        if (!isNaN(price)) {
          visible = price >= this.filters.minPrice && price <= this.filters.maxPrice;
        }
      }
      
      // Apply category filter
      if (visible && this.filters.category !== 'all') {
        visible = product.dataset.category === this.filters.category;
      }
      
      // Apply availability filter
      if (visible && this.filters.availability !== 'all') {
        visible = product.dataset.availability === this.filters.availability;
      }
      
      // Update visibility with smooth transition
      if (visible) {
        visibleCount++;
        if (product.style.display === 'none') {
          product.style.opacity = '0';
          product.style.display = '';
          setTimeout(() => {
            product.style.opacity = '1';
          }, 50);
        }
      } else {
        product.style.opacity = '0';
        setTimeout(() => {
          product.style.display = 'none';
        }, 300);
      }
    });
    
    // Apply sorting
    this.sortProducts();
    
    // Show "no results" message if needed
    this.updateNoResultsMessage(visibleCount === 0);
  }
  
  sortProducts() {
    if (!this.productsGrid) return;
    
    const products = Array.from(this.productsGrid.children);
    
    products.sort((a, b) => {
      const getPriceValue = (element) => {
        const priceElement = element.querySelector('.product-price');
        return parseFloat(priceElement?.dataset.price || priceElement?.textContent.replace(/[^0-9.]/g, '')) || 0;
      };
      
      switch (this.filters.sortBy) {
        case 'price-low':
          return getPriceValue(a) - getPriceValue(b);
        case 'price-high':
          return getPriceValue(b) - getPriceValue(a);
        case 'name':
          return (a.querySelector('.product-title')?.textContent || '').localeCompare(
            b.querySelector('.product-title')?.textContent || ''
          );
        case 'rating':
          const getRating = (element) => parseFloat(element.dataset.rating || 0);
          return getRating(b) - getRating(a);
        default:
          return 0;
      }
    });
    
    // Reorder DOM elements with smooth transitions
    products.forEach((product, index) => {
      product.style.transition = 'transform 0.5s ease, opacity 0.3s ease';
      product.style.zIndex = 1000 - index;
      this.productsGrid.appendChild(product);
    });
  }
  
  updateNoResultsMessage(show) {
    let messageElement = document.querySelector('.no-results-message');
    
    if (show) {
      if (!messageElement) {
        messageElement = document.createElement('div');
        messageElement.className = 'no-results-message';
        messageElement.innerHTML = `
          <p>No products match your filters</p>
          <button class="btn btn-outline" onclick="filterSystem.resetFilters()">Reset Filters</button>
        `;
        this.productsGrid.parentNode.insertBefore(messageElement, this.productsGrid.nextSibling);
        
        // Fade in animation
        messageElement.style.opacity = '0';
        setTimeout(() => {
          messageElement.style.opacity = '1';
        }, 10);
      }
    } else if (messageElement) {
      // Fade out animation
      messageElement.style.opacity = '0';
      setTimeout(() => {
        messageElement.remove();
      }, 300);
    }
  }
  
  resetFilters() {
    this.filters = {
      search: '',
      minPrice: 0,
      maxPrice: 1000,
      category: 'all',
      availability: 'all',
      sortBy: 'featured'
    };
    
    // Reset all inputs
    if (this.searchInput) this.searchInput.value = '';
    if (this.minPriceInput) this.minPriceInput.value = 0;
    if (this.maxPriceInput) this.maxPriceInput.value = 1000;
    if (this.categorySelect) this.categorySelect.value = 'all';
    if (this.availabilitySelect) this.availabilitySelect.value = 'all';
    if (this.sortSelect) this.sortSelect.value = 'featured';
    
    const priceRangeSlider = document.querySelector('#price-range');
    if (priceRangeSlider) priceRangeSlider.value = 1000;
    
    this.applyFilters();
    this.renderActiveFilters();
  }
}

// AI Chatbot
class AIChatbot {
  constructor() {
    this.isOpen = false;
    this.messageHistory = [];
    // Wait for DOM to be fully loaded before initializing
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.init());
    } else {
      this.init();
    }
  }
  
  init() {
    console.log('Initializing chatbot...');
    
    // Get DOM elements
    this.chatbotContainer = document.getElementById('chatbot-container');
    this.chatbotTrigger = document.getElementById('chatbot-trigger');
    this.chatbotClose = document.getElementById('chatbot-close');
    this.chatbotMessages = document.getElementById('chatbot-messages');
    this.chatbotInput = document.getElementById('chatbot-input');
    this.chatbotSendButton = document.getElementById('chatbot-send');
    
    // Check if elements exist
    if (!this.chatbotContainer || !this.chatbotTrigger) {
      console.error('Chatbot elements not found in the DOM');
      return;
    }
    
    console.log('Chatbot elements found, adding event listeners');
    
    this.addEventListeners();
    this.addWelcomeMessage();
  }
  
  addEventListeners() {
    // Toggle chatbot
    if (this.chatbotTrigger) {
      console.log('Adding click event to chatbot trigger');
      this.chatbotTrigger.addEventListener('click', (e) => {
        console.log('Chatbot trigger clicked');
        e.preventDefault();
        e.stopPropagation();
        this.toggleChatbot();
      });
    }
    
    if (this.chatbotClose) {
      this.chatbotClose.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.toggleChatbot(false);
      });
    }
    
    // Send message on button click
    if (this.chatbotSendButton) {
      this.chatbotSendButton.addEventListener('click', () => {
        this.sendMessage();
      });
    }
    
    // Send message on Enter key
    if (this.chatbotInput) {
      this.chatbotInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          this.sendMessage();
        }
      });
    }
    
    // Close chatbot when clicking outside
    document.addEventListener('click', (e) => {
      if (this.isOpen && 
          this.chatbotContainer && 
          this.chatbotTrigger && 
          !this.chatbotContainer.contains(e.target) && 
          !this.chatbotTrigger.contains(e.target)) {
        this.toggleChatbot(false);
      }
    });
  }
  
  addWelcomeMessage() {
    if (!this.chatbotMessages) return;
    
    // Check if welcome message already exists
    if (this.chatbotMessages.children.length === 0) {
      const welcomeMessage = "Hello! I'm your Cutlery Rental assistant. How can I help you today? You can ask me about our products, pricing, availability, or rental process.";
      this.addMessage(welcomeMessage, 'bot');
      
      // Add to message history
      this.messageHistory.push({
        role: 'assistant',
        content: welcomeMessage
      });
    }
  }
  
  async sendMessage() {
    if (!this.chatbotInput || !this.chatbotMessages) return;
    
    const message = this.chatbotInput.value.trim();
    if (!message) return;
    
    // Add user message
    this.addMessage(message, 'user');
    
    // Add to message history
    this.messageHistory.push({
      role: 'user',
      content: message
    });
    
    // Clear input
    this.chatbotInput.value = '';
    
    // Disable input while waiting for response
    this.setInputState(false);
    
    // Show typing indicator
    this.addTypingIndicator();
    
    // Get AI response
    try {
      const response = await this.getAIResponse(message);
      this.removeTypingIndicator();
      this.addMessage(response, 'bot');
      
      // Add to message history
      this.messageHistory.push({
        role: 'assistant',
        content: response
      });
      
      // Limit message history to last 10 messages to prevent excessive context
      if (this.messageHistory.length > 10) {
        this.messageHistory = this.messageHistory.slice(-10);
      }
    } catch (error) {
      console.error('Error getting AI response:', error);
      this.removeTypingIndicator();
      this.addMessage('Sorry, I encountered an error. Please try again later.', 'bot');
    } finally {
      // Re-enable input
      this.setInputState(true);
    }
  }
  
  setInputState(enabled) {
    if (this.chatbotInput && this.chatbotSendButton) {
      this.chatbotInput.disabled = !enabled;
      this.chatbotSendButton.disabled = !enabled;
      
      if (!enabled) {
        this.chatbotSendButton.classList.add('disabled');
      } else {
        this.chatbotSendButton.classList.remove('disabled');
      }
    }
  }
  
  addMessage(text, sender) {
    if (!this.chatbotMessages) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = `chat-avatar ${sender}`;
    avatar.textContent = sender === 'user' ? 'U' : 'A';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;
    
    messageElement.appendChild(avatar);
    messageElement.appendChild(content);
    
    this.chatbotMessages.appendChild(messageElement);
    
    // Scroll to bottom
    this.chatbotMessages.scrollTop = this.chatbotMessages.scrollHeight;
  }
  
  addTypingIndicator() {
    if (!this.chatbotMessages) return;
    
    const typingElement = document.createElement('div');
    typingElement.className = 'chat-message bot typing-indicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'chat-avatar bot';
    avatar.textContent = 'A';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = '<span>.</span><span>.</span><span>.</span>';
    
    typingElement.appendChild(avatar);
    typingElement.appendChild(content);
    
    this.chatbotMessages.appendChild(typingElement);
    this.chatbotMessages.scrollTop = this.chatbotMessages.scrollHeight;
  }
  
  removeTypingIndicator() {
    if (!this.chatbotMessages) return;
    
    const typingIndicator = this.chatbotMessages.querySelector('.typing-indicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }
  
  async getAIResponse(message) {
    try {
      // Show typing indicator for at least 1 second for better UX
      const typingDelay = new Promise(resolve => setTimeout(resolve, 1000));
      
      // Make API request to our chatbot endpoint
      const response = await fetch('/api/chatbot', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: message,
          history: this.messageHistory // Send message history for context
        })
      });
      
      // Wait for both the typing delay and API response
      await typingDelay;
      
      if (!response.ok) {
        throw new Error('Failed to get response from chatbot');
      }
      
      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Chatbot error:', error);
      return "I'm sorry, I'm having trouble connecting right now. Please try again later or contact us directly at (123) 456-7890.";
    }
  }
  
  toggleChatbot(open = !this.isOpen) {
    console.log('Toggling chatbot, current state:', this.isOpen, 'new state:', open);
    
    if (!this.chatbotContainer) {
      console.error('Chatbot container not found');
      return;
    }
    
    this.isOpen = open;
    
    if (open) {
      this.chatbotContainer.classList.add('active');
      if (this.chatbotInput) {
        this.chatbotInput.focus();
      }
    } else {
      this.chatbotContainer.classList.remove('active');
    }
  }
}

// Utility function for debouncing
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Header scroll effect
function handleHeaderScroll() {
  const header = document.querySelector('header');
  if (!header) return;
  
  if (window.scrollY > 50) {
    header.classList.add('header-scrolled');
  } else {
    header.classList.remove('header-scrolled');
  }
}

// Dark mode toggle function
function toggleDarkMode() {
  const html = document.documentElement;
  const isDarkMode = html.getAttribute('data-theme') === 'dark';
  
  html.setAttribute('data-theme', isDarkMode ? 'light' : 'dark');
  localStorage.setItem('theme', isDarkMode ? 'light' : 'dark');
  
  // Update toggle button text/icon if needed
  const darkModeToggle = document.getElementById('dark-mode-toggle');
  if (darkModeToggle) {
    darkModeToggle.innerHTML = isDarkMode ? 
      '<i class="fas fa-moon"></i>' : 
      '<i class="fas fa-sun"></i>';
  }
}

// Initialize theme from localStorage
(function() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Update toggle button text/icon if needed
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle && savedTheme === 'dark') {
      darkModeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
  }
})();

// Smooth scroll for anchor links
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      const targetElement = document.querySelector(targetId);
      
      if (targetElement) {
        const headerOffset = 80;
        const elementPosition = targetElement.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
        
        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
}

// Initialize mobile menu
function initMobileMenu() {
  const menuToggle = document.querySelector('.menu-toggle');
  const navMenu = document.querySelector('.nav-menu');
  
  if (!menuToggle || !navMenu) return;
  
  menuToggle.addEventListener('click', function() {
    menuToggle.classList.toggle('active');
    navMenu.classList.toggle('active');
    document.body.classList.toggle('menu-open');
  });
  
  // Close menu when clicking on a link
  const navLinks = navMenu.querySelectorAll('a');
  navLinks.forEach(link => {
    link.addEventListener('click', function() {
      menuToggle.classList.remove('active');
      navMenu.classList.remove('active');
      document.body.classList.remove('menu-open');
    });
  });
}

// Newsletter Form Handler
class NewsletterForm {
  constructor() {
    this.form = document.querySelector('.newsletter-form');
    if (this.form) {
      this.init();
    }
  }
  
  init() {
    this.emailInput = this.form.querySelector('input[type="email"]');
    this.submitButton = this.form.querySelector('button[type="submit"]');
    
    this.addEventListeners();
  }
  
  addEventListeners() {
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleSubmit();
    });
  }
  
  handleSubmit() {
    const email = this.emailInput.value.trim();
    
    if (!email) {
      this.showMessage('Please enter your email address', 'error');
      return;
    }
    
    if (!this.validateEmail(email)) {
      this.showMessage('Please enter a valid email address', 'error');
      return;
    }
    
    // Here you would typically send the email to your server
    // For now, we'll just simulate a successful subscription
    this.showMessage('Thank you for subscribing!', 'success');
    this.emailInput.value = '';
  }
  
  validateEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
  }
  
  showMessage(message, type) {
    // Remove any existing message
    const existingMessage = this.form.querySelector('.newsletter-message');
    if (existingMessage) {
      existingMessage.remove();
    }
    
    // Create new message
    const messageElement = document.createElement('div');
    messageElement.className = `newsletter-message ${type}`;
    messageElement.textContent = message;
    
    // Add message after the form
    this.form.appendChild(messageElement);
    
    // Remove message after 3 seconds
    setTimeout(() => {
      messageElement.remove();
    }, 3000);
  }
}

// Initialize all components when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Initialize existing components
  const filterSystem = new FilterSystem();
  const chatbot = new AIChatbot();
  const uiEnhancer = new UIEnhancer();
  
  // Initialize header scroll effect
  window.addEventListener('scroll', handleHeaderScroll);
  handleHeaderScroll(); // Call once to set initial state
  
  // Initialize smooth scroll
  initSmoothScroll();
  
  // Initialize mobile menu
  initMobileMenu();
  
  // Initialize newsletter form
  const newsletterForm = new NewsletterForm();
});

// UI Enhancements
class UIEnhancer {
  constructor() {
    this.init();
  }
  
  init() {
    this.addScrollAnimations();
    this.addHoverEffects();
    this.initDarkModeToggle();
    this.initMobileMenu();
  }
  
  addScrollAnimations() {
    // Animate elements when they come into view
    const animateOnScroll = () => {
      const elements = document.querySelectorAll('.animate-on-scroll:not(.animated)');
      
      elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;
        
        if (elementTop < window.innerHeight - elementVisible) {
          element.classList.add('animated');
          
          // Add specific animation class based on data attribute
          const animation = element.dataset.animation || 'fade-in';
          element.classList.add(animation);
        }
      });
    };
    
    // Add animate-on-scroll class to elements
    const addAnimationClasses = () => {
      // Product cards
      document.querySelectorAll('.product-card').forEach((card, index) => {
        card.classList.add('animate-on-scroll');
        card.dataset.animation = 'fade-up';
        card.style.animationDelay = `${index * 0.1}s`;
      });
      
      // Section headings
      document.querySelectorAll('h2, h3').forEach(heading => {
        if (!heading.closest('.hero')) {
          heading.classList.add('animate-on-scroll');
          heading.dataset.animation = 'fade-in';
        }
      });
      
      // Filter section
      const filterSection = document.querySelector('.search-filter');
      if (filterSection) {
        filterSection.classList.add('animate-on-scroll');
        filterSection.dataset.animation = 'fade-in';
      }
    };
    
    // Initialize
    addAnimationClasses();
    window.addEventListener('scroll', debounce(animateOnScroll, 10));
    animateOnScroll(); // Initial check
  }
  
  addHoverEffects() {
    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
      button.addEventListener('mousedown', function(e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const ripple = document.createElement('span');
        ripple.classList.add('ripple-effect');
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        
        this.appendChild(ripple);
        
        setTimeout(() => {
          ripple.remove();
        }, 600);
      });
    });
    
    // Add hover effect to product cards
    document.querySelectorAll('.product-card').forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-8px)';
      });
      
      card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
      });
    });
  }
  
  initDarkModeToggle() {
    const darkModeToggle = document.querySelector('#dark-mode-toggle');
    
    if (darkModeToggle) {
      // Check for saved theme preference or use system preference
      const savedTheme = localStorage.getItem('theme');
      const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      
      if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        darkModeToggle.checked = true;
      }
      
      // Toggle dark mode
      darkModeToggle.addEventListener('change', function() {
        if (this.checked) {
          document.documentElement.setAttribute('data-theme', 'dark');
          localStorage.setItem('theme', 'dark');
        } else {
          document.documentElement.setAttribute('data-theme', 'light');
          localStorage.setItem('theme', 'light');
        }
      });
    }
  }
  
  initMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (menuToggle && navMenu) {
      menuToggle.addEventListener('click', function() {
        navMenu.classList.toggle('active');
        this.classList.toggle('active');
      });
      
      // Close menu when clicking outside
      document.addEventListener('click', function(e) {
        if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
          navMenu.classList.remove('active');
          menuToggle.classList.remove('active');
        }
      });
    }
  }
} 