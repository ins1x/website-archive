/*!
 * Script for Online-checker https://github.com/ins1x/checker
 */

const inputElement = document.getElementById('input-Go');

// Dropdown menu select
document.querySelectorAll('#dropdown-search .dropdown-item').forEach(item => {
  item.addEventListener('click', function(selDropdown) {
    selDropdown.preventDefault();
    const selectedText = this.innerText;
    document.getElementById('button-dropdown').innerText = selectedText;
  });
});

function GoSearch(query) {
  if (inputElement.value.trim() === '') {
    alert('Damn, no input value. Try again!');
    document.getElementById("card-text-secondary").innerText = 'Damn, no input value. Try again!';
  } else {
    const dropdownText = document.getElementById('button-dropdown').innerText.trim();
    switch (dropdownText) {
      case "Whois":
        window.open("https://who.is/whois/" + query, "_blank");
        break
      case "Ping":
        window.open("https://ping.pe/" + query, "_blank");
        break
      case "MAC":
        window.open("https://maclookup.app/search/result?mac=" + query, "_blank");
        break
      case "Trace":
        window.open("https://tools.bunny.net/traceroute?query=" + query, "_blank");
        break
      case "DNS":
        window.open("https://dnschecker.org/all-dns-records-of-domain.php?query=" + query, "_blank");
        break
      case "Spam-base":
        window.open("https://mxtoolbox.com/SuperTool.aspx?action=blacklist%3a" + query, "_blank");
        break
      case "Check-host":
        window.open("https://check-host.net/check-http?host=" + query, "_blank");
        break
      default:
        // console.log(`OK: ${dropdownText}`);
        document.getElementById("card-text-secondary").innerText = 'Something get wrong. Try again!';
    }
  }
}

// Search on press Go button
document.getElementById('button-Go').addEventListener('click', () => {
  const textValue = inputElement.value;
  GoSearch(textValue);
});

// Search on pressed 'Enter' key
inputElement.addEventListener('keydown', function(event) {
  if (event.key === 'Enter') {
    event.preventDefault(); 
    const inputValue = event.target.value;
    GoSearch(inputValue); 
  }
});

// TODO: Load from json
// fetch('https://ipinfo.io/json') 
// .then(response => { 
//   if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`); 
//   return response.json(); // Parses the JSON string into an object 
// }) 
// .then(data => { 
//   console.log(data); // Work with your data here 
// }) 
// .catch(error => { 
//   console.error('Fetch error:', error); 
// }); 
