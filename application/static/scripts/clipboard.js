  console.log('Clipboard script loaded');
  // Function to handle toggling display of elements
  function toggleDisplay(event) {
    console.log('Toggling display');
    event.preventDefault();

    // Get the target id from data-target attribute
    const targetId = event.target.getAttribute('data-target');

    // Hide all doc-elements
    const elements = document.querySelectorAll('.doc-element-collapse');
    elements.forEach(element => {
      element.style.display = 'none';
    });

    // Show the selected element
    const targetElement = document.getElementById(targetId);
    if (targetElement) {
      targetElement.style.display = 'block';
    }
  }

  // Add event listeners to all toggle links
  const links = document.querySelectorAll('.toggle-link');
  links.forEach(link => {
    link.addEventListener('click', toggleDisplay);
  });

  // Optionally: Show index by default when the page loads
  document.getElementById('index0').style.display = 'block';