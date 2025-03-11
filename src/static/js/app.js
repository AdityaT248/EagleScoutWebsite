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
    this.init();
  }
  
  init() {
    this.chatbotContainer = document.querySelector('.chatbot-container');
    this.chatbotTrigger = document.querySelector('.chatbot-trigger');
    this.chatbotClose = document.querySelector('.chatbot-close');
    this.chatbotMessages = document.querySelector('.chatbot-messages');
    this.chatbotInput = document.querySelector('.chatbot-input input');
    this.chatbotSendButton = document.querySelector('.chatbot-input button');
    
    this.addEventListeners();
    this.addWelcomeMessage();
  }
  
  addEventListeners() {
    // Toggle chatbot
    this.chatbotTrigger?.addEventListener('click', () => {
      this.toggleChatbot();
    });
    
    this.chatbotClose?.addEventListener('click', () => {
      this.toggleChatbot(false);
    });
    
    // Send message on button click
    this.chatbotSendButton?.addEventListener('click', () => {
      this.sendMessage();
    });
    
    // Send message on Enter key
    this.chatbotInput?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.sendMessage();
      }
    });
    
    // Close chatbot when clicking outside
    document.addEventListener('click', (e) => {
      if (this.isOpen && 
          !this.chatbotContainer.contains(e.target) && 
          !this.chatbotTrigger.contains(e.target)) {
        this.toggleChatbot(false);
      }
    });
  }
  
  addWelcomeMessage() {
    this.addMessage('Hello! How can I help you with your cutlery rental needs today?', 'bot');
  }
  
  async sendMessage() {
    const message = this.chatbotInput.value.trim();
    if (!message) return;
    
    // Add user message
    this.addMessage(message, 'user');
    
    // Clear input
    this.chatbotInput.value = '';
    
    // Show typing indicator
    this.addTypingIndicator();
    
    // Get AI response
    try {
      const response = await this.getAIResponse(message);
      this.removeTypingIndicator();
      this.addMessage(response, 'bot');
    } catch (error) {
      this.removeTypingIndicator();
      this.addMessage('Sorry, I encountered an error. Please try again later.', 'bot');
    }
  }
  
  addMessage(text, sender) {
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
    const typingIndicator = this.chatbotMessages.querySelector('.typing-indicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }
  
  async getAIResponse(message) {
    // Simulate AI response with delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Simple responses based on keywords
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
      return 'Hello! How can I help you with your cutlery rental needs today?';
    } else if (lowerMessage.includes('price') || lowerMessage.includes('cost')) {
      return 'Our prices range from $20 for basic items to $95 for premium sets. You can see all prices on our product listings.';
    } else if (lowerMessage.includes('delivery') || lowerMessage.includes('shipping')) {
      return 'We offer free delivery for orders over $50. Standard delivery takes 1-2 business days.';
    } else if (lowerMessage.includes('return')) {
      return 'Returns are accepted within 7 days of delivery. Please ensure items are in their original condition.';
    } else if (lowerMessage.includes('availability')) {
      return 'Most of our items are in stock and ready to ship. Items marked as "limited" have low stock, while "out of stock" items can be pre-ordered.';
    } else {
      return 'Thank you for your message. If you have any specific questions about our cutlery rental service, please let me know!';
    }
  }
  
  toggleChatbot(open = !this.isOpen) {
    this.isOpen = open;
    
    if (open) {
      this.chatbotContainer.classList.add('active');
      this.chatbotInput.focus();
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

// Header Scroll Effect
function handleHeaderScroll() {
  const header = document.querySelector('header');
  const scrolled = window.scrollY > 20;
  header?.classList.toggle('scrolled', scrolled);
}

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

// Initialize components
document.addEventListener('DOMContentLoaded', () => {
  // Initialize filter system
  window.filterSystem = new FilterSystem();
  
  // Initialize chatbot
  const chatbot = new AIChatbot();
  
  // Initialize header scroll effect
  window.addEventListener('scroll', debounce(handleHeaderScroll, 10));
  handleHeaderScroll();
  
  // Initialize smooth scroll
  initSmoothScroll();
  
  // Add animation classes to elements
  document.querySelectorAll('.product-card').forEach((card, index) => {
    card.classList.add('animate-on-scroll');
    card.dataset.animation = 'fade-up';
    card.style.animationDelay = `${index * 0.1}s`;
  });
  
  // Initialize animations
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
  
  window.addEventListener('scroll', debounce(animateOnScroll, 10));
  animateOnScroll(); // Initial check
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

// Initialize UI enhancements
const uiEnhancer = new UIEnhancer();

/**
 * Product Form Handler
 * Manages the product form functionality including image preview and form submission
 */
class ProductFormHandler {
  constructor() {
    this.form = document.querySelector('.product-form');
    this.imageInput = document.querySelector('#product-image');
    this.imagePreview = document.querySelector('#image-preview');
    this.resetButton = document.querySelector('#reset-form');
    
    this.init();
  }
  
  init() {
    if (!this.form) return;
    
    // Set up event listeners
    this.imageInput?.addEventListener('change', this.handleImagePreview.bind(this));
    this.form.addEventListener('submit', this.handleSubmit.bind(this));
    this.resetButton?.addEventListener('click', this.resetForm.bind(this));
    
    // Initialize form validation
    this.setupFormValidation();
  }
  
  handleImagePreview(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Check if file is an image
    if (!file.type.match('image.*')) {
      this.showAlert('Please select an image file (JPEG, PNG, GIF, etc.)', 'error');
      return;
    }
    
    // Check file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      this.showAlert('Image size should be less than 5MB', 'error');
      return;
    }
    
    const reader = new FileReader();
    
    reader.onload = (e) => {
      if (this.imagePreview) {
        this.imagePreview.src = e.target.result;
        this.imagePreview.style.display = 'block';
        
        // Add animation
        this.imagePreview.style.opacity = '0';
        setTimeout(() => {
          this.imagePreview.style.opacity = '1';
        }, 50);
      }
    };
    
    reader.readAsDataURL(file);
  }
  
  handleSubmit(event) {
    event.preventDefault();
    
    // Validate form
    if (!this.validateForm()) {
      return;
    }
    
    // Get form data
    const formData = new FormData(this.form);
    
    // Show loading state
    this.setLoadingState(true);
    
    // Simulate form submission (replace with actual API call)
    setTimeout(() => {
      // Success response simulation
      this.setLoadingState(false);
      this.showAlert('Product added successfully!', 'success');
      this.resetForm();
      
      // In a real application, you would send the formData to your backend:
      /*
      fetch('/api/products', {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        this.setLoadingState(false);
        if (data.success) {
          this.showAlert('Product added successfully!', 'success');
          this.resetForm();
        } else {
          this.showAlert(data.message || 'Failed to add product', 'error');
        }
      })
      .catch(error => {
        this.setLoadingState(false);
        this.showAlert('An error occurred. Please try again.', 'error');
        console.error('Error:', error);
      });
      */
    }, 1500);
  }
  
  validateForm() {
    let isValid = true;
    const requiredFields = this.form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
      if (!field.value.trim()) {
        isValid = false;
        field.classList.add('error');
        
        // Add error message
        const errorMessage = document.createElement('div');
        errorMessage.className = 'error-message';
        errorMessage.textContent = `${field.getAttribute('placeholder') || 'This field'} is required`;
        
        // Remove existing error message if any
        const existingError = field.parentNode.querySelector('.error-message');
        if (existingError) {
          field.parentNode.removeChild(existingError);
        }
        
        field.parentNode.appendChild(errorMessage);
      } else {
        field.classList.remove('error');
        const existingError = field.parentNode.querySelector('.error-message');
        if (existingError) {
          field.parentNode.removeChild(existingError);
        }
      }
    });
    
    // Validate price (must be a positive number)
    const priceField = this.form.querySelector('#product-price');
    if (priceField && priceField.value) {
      const price = parseFloat(priceField.value);
      if (isNaN(price) || price <= 0) {
        isValid = false;
        priceField.classList.add('error');
        
        // Add error message
        const errorMessage = document.createElement('div');
        errorMessage.className = 'error-message';
        errorMessage.textContent = 'Price must be a positive number';
        
        // Remove existing error message if any
        const existingError = priceField.parentNode.querySelector('.error-message');
        if (existingError) {
          priceField.parentNode.removeChild(existingError);
        }
        
        priceField.parentNode.appendChild(errorMessage);
      }
    }
    
    if (!isValid) {
      this.showAlert('Please fill in all required fields correctly', 'error');
    }
    
    return isValid;
  }
  
  resetForm() {
    this.form.reset();
    if (this.imagePreview) {
      this.imagePreview.src = '';
      this.imagePreview.style.display = 'none';
    }
    
    // Remove all error messages
    const errorMessages = this.form.querySelectorAll('.error-message');
    errorMessages.forEach(message => message.remove());
    
    // Remove error classes
    const errorFields = this.form.querySelectorAll('.error');
    errorFields.forEach(field => field.classList.remove('error'));
  }
  
  setLoadingState(isLoading) {
    const submitButton = this.form.querySelector('button[type="submit"]');
    
    if (isLoading) {
      submitButton.disabled = true;
      submitButton.innerHTML = '<span class="loading-spinner-small"></span> Adding...';
      this.form.classList.add('loading');
    } else {
      submitButton.disabled = false;
      submitButton.innerHTML = 'Add Product';
      this.form.classList.remove('loading');
    }
  }
  
  showAlert(message, type = 'success') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type}`;
    alertElement.textContent = message;
    
    // Insert alert before the form
    this.form.parentNode.insertBefore(alertElement, this.form);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      alertElement.style.opacity = '0';
      setTimeout(() => {
        alertElement.remove();
      }, 300);
    }, 5000);
  }
  
  setupFormValidation() {
    const inputs = this.form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
      input.addEventListener('input', () => {
        input.classList.remove('error');
        const errorMessage = input.parentNode.querySelector('.error-message');
        if (errorMessage) {
          errorMessage.remove();
        }
      });
    });
  }
}

// Initialize all components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize existing components
  const darkModeToggle = document.getElementById('dark-mode-toggle');
  if (darkModeToggle) {
    darkModeToggle.addEventListener('click', toggleDarkMode);
  }
  
  // Initialize header scroll effect
  window.addEventListener('scroll', handleHeaderScroll);
  
  // Initialize filter system if elements exist
  if (document.querySelector('.search-filter')) {
    new FilterSystem();
  }
  
  // Initialize chatbot if elements exist
  if (document.querySelector('.chatbot-container')) {
    new AIChatbot();
  }
  
  // Initialize product form if it exists
  if (document.querySelector('.product-form')) {
    new ProductFormHandler();
  }
  
  // Call header scroll handler once to set initial state
  handleHeaderScroll();
});

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