# Script to generate the complete index.html with all new features

# Read the first part (up to the JavaScript closing)
PART_END = '''        // Show alert
        function showAlert(message, type) {
            const container = document.getElementById('alert-container');
            const alert = document.createElement('div');
            alert.className = `alert alert-${type}`;
            alert.innerHTML = `
                <span>${message}</span>
            `;
            
            container.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }
    </script>
</body>
</html>'''

# Read the temporary file we created
with open('C:/Users/Administrator/Documents/Github/Digestarr/app/templates/index_new.html', 'r', encoding='utf-8') as f:
    js_continuation = f.read()

# Read the original to get the first part
with open('C:/Users/Administrator/Documents/Github/Digestarr/app/templates/index.html', 'r', encoding='utf-8') as f:
    original = f.read()

# Find where the loadStats function ends and replace everything after
search_str = '''        // Load stats
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');'''

if search_str in original:
    before = original[:original.index(search_str)]
    complete = before + js_continuation
    
    with open('C:/Users/Administrator/Documents/Github/Digestarr/app/templates/index_BACKUP.html', 'w', encoding='utf-8') as f:
        f.write(original)
    
    with open('C:/Users/Administrator/Documents/Github/Digestarr/app/templates/index.html', 'w', encoding='utf-8') as f:
        f.write(complete)
    
    print("✅ Successfully updated index.html")
    print("✅ Original backed up to index_BACKUP.html")
else:
    print("❌ Could not find search string")
