async function copy_to_clipboard(button) {

  const text_to_copy = button.parentNode.parentNode.children[1];
  text_to_copy.select();

  try {
    await navigator.clipboard.writeText(text_to_copy.value.trim());
  } catch (error) {
    console.error('Error when copying: ', error);
  }
}