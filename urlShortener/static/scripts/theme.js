set_initial_theme();

document.addEventListener('DOMContentLoaded', () => {
  const logoText = document.getElementById('logo-text');
  const colorToggle = document.getElementById('color-toggle');

  colorToggle.addEventListener('click', () => swap_theme_other(colorToggle, logoText), false);

  if (localStorage.getItem('theme') === 'light') {
    logoText.setAttribute('fill', '#303030');
    colorToggle.children[0].setAttribute('class', 'bi bi-moon-stars-fill');
  } else {
    logoText.setAttribute('fill', '#FFF');
    colorToggle.children[0].setAttribute('class', 'bi bi-sun-fill');
  }
});

function set_initial_theme() {
  if (localStorage.getItem('theme')) {
    document.documentElement.setAttribute('data-bs-theme', localStorage.getItem('theme'));
  }
}

function swap_theme_other(button, logo) {
  if (localStorage.getItem('theme')) {
    if (localStorage.getItem('theme') === "light") {
      localStorage.setItem('theme', 'dark');
      document.documentElement.setAttribute('data-bs-theme', 'dark');
      logo.setAttribute('fill', '#FFF');
      button.children[0].setAttribute('class', 'bi bi-sun-fill');
    } else {
      localStorage.setItem('theme', 'light');
      document.documentElement.setAttribute('data-bs-theme', 'light');
      logo.setAttribute('fill', '#303030');
      button.children[0].setAttribute('class', 'bi bi-moon-stars-fill');
    }
  }
}