set_initial_theme();

document.addEventListener('DOMContentLoaded', () => {
  const colorButton = document.getElementById('color-button');
  colorButton.addEventListener('click', () => swap_theme(), false);
  colorButton.checked = localStorage.getItem('theme') !== 'light';

  const logoText = document.getElementById('logo-text');
  if (localStorage.getItem('theme') === 'light') {
    logoText.setAttribute('fill', '#303030');
  } else {
    logoText.setAttribute('fill', '#FFF');
  }
});

function set_initial_theme() {
  if (localStorage.getItem('theme')) {
    document.documentElement.setAttribute('data-bs-theme', localStorage.getItem('theme'));
  }
}

function swap_theme() {
  if (localStorage.getItem('theme')) {
    const logoText = document.getElementById('logo-text');
    if (localStorage.getItem('theme') === "light") {
      localStorage.setItem('theme', 'dark');
      document.documentElement.setAttribute('data-bs-theme', 'dark');
      logoText.setAttribute('fill', '#FFF');
    } else {
      localStorage.setItem('theme', 'light');
      document.documentElement.setAttribute('data-bs-theme', 'light');
      logoText.setAttribute('fill', '#303030');
    }
  }
}