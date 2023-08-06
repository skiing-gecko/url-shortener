async function copy_to_clipboard(button_id) {
  let text_to_copy;

  if (button_id === 'copyShort') {
    text_to_copy = document.getElementById('shortUrlText');
  } else if (button_id === 'copyLong') {
    text_to_copy = document.getElementById('longUrlText');
  }
  text_to_copy.select();

  try {
    await navigator.clipboard.writeText(text_to_copy.value);
  } catch (error) {
    console.error('Error when copying: ', error);
  }
}