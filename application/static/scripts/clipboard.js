  console.log('Clipboard script loaded');
  // Function to handle toggling display of elements
  function toggleDisplay(event) {
    event.preventDefault();

    // Get the target id from data-target attribute
    const targetId = event.target.getAttribute('data-target');

    // Show the selected element, hide it if it's already visible
    const targetElement = document.getElementById(targetId);
    if (!targetElement) {
        return
    }
    // Get the computed style of the element
    const isVisible = window.getComputedStyle(targetElement).display !== 'none';

    // Hide all doc-elements
    const elements = document.querySelectorAll('.doc-element-collapse');
    elements.forEach(element => {
      element.style.display = 'none';
    });

    //get anchor siblings of event element
    const siblings = event.target.parentElement.children;
    for (let i = 0; i < siblings.length; i++) {
      if (siblings[i].tagName === 'A') {
        siblings[i].style.backgroundColor = 'lightblue';
      }
    }
    


    // Toggle visibility based on current state
    if (isVisible) {
    targetElement.style.display = 'none';
    } else {
    targetElement.style.display = 'block';
    event.target.scrollIntoView({behavior: 'smooth', block: 'start'});
    event.target.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
    }
}

  // Add event listeners to all toggle links
  const links = document.querySelectorAll('.toggle-link');
  links.forEach(link => {
    link.addEventListener('click', toggleDisplay);
  });