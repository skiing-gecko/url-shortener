window.addEventListener('DOMContentLoaded', () => {
  const deleteButtons = document.getElementsByClassName('delete-btn');
  for (const button of deleteButtons) {
    button.onclick = function confirm_delete() {
      return confirm('Are you sure?');
    }
  }
})