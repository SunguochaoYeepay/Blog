<template>
  <div class="main-layout">
    <header class="header">
      <nav>
        <router-link to="/" class="logo">My Blog</router-link>
        <div class="nav-links">
          <router-link to="/">Home</router-link>
          <router-link to="/blog">Blog</router-link>
          <router-link to="/about">About</router-link>
          <router-link to="/contact">Contact</router-link>
        </div>
      </nav>
    </header>

    <main class="main-content">
      <slot></slot>
    </main>

    <footer class="footer">
      <p>&copy; 2024 My Blog. All rights reserved.</p>
    </footer>
  </div>
</template>

<style scoped lang="scss">
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background-color: var(--background-primary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem 2rem;

  nav {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .logo {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
    text-decoration: none;
  }

  .nav-links {
    display: flex;
    gap: 2rem;

    a {
      color: var(--text-primary);
      text-decoration: none;
      transition: color 0.3s ease;

      &:hover {
        color: var(--primary-color);
      }

      &.router-link-active {
        color: var(--primary-color);
        font-weight: 500;
      }
    }
  }
}

.main-content {
  flex: 1;
  width: 100%;
  margin: 0 auto;
}

.footer {
  background-color: var(--background-primary);
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .header {
    padding: 1rem;

    nav {
      flex-direction: column;
      gap: 1rem;
    }

    .nav-links {
      gap: 1rem;
    }
  }
}
</style>