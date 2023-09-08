window.addEventListener('DOMContentLoaded', () => {
  const copyButtons = document.getElementsByClassName('copy-button');

  for (const button of copyButtons) {
    const formURL = button.parentNode.children[1];
    button.addEventListener('click', () => copy_to_clipboard(formURL))
  }
});

async function copy_to_clipboard(text_to_copy) {
  text_to_copy.select();

  try {
    await navigator.clipboard.writeText(text_to_copy.value.trim());
  } catch (error) {
    console.error('Error when copying: ', error);
  }
}