// Image preview for registration
const imageInput = document.getElementById('image');
const previewContainer = document.getElementById('preview');

if (imageInput) {
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewContainer.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            };
            reader.readAsDataURL(file);
        }
    });
}

// Registration form submission
const registrationForm = document.getElementById('registrationForm');
if (registrationForm) {
    registrationForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const messageDiv = document.getElementById('message');
        
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            messageDiv.className = 'message ' + (result.success ? 'success' : 'error');
            messageDiv.textContent = result.message;
            messageDiv.style.display = 'block';
            
            if (result.success) {
                registrationForm.reset();
                previewContainer.innerHTML = '';
            }
        } catch (error) {
            messageDiv.className = 'message error';
            messageDiv.textContent = 'Error: ' + error.message;
            messageDiv.style.display = 'block';
        }
    });
}

// Attendance form submission
const attendanceForm = document.getElementById('attendanceForm');
if (attendanceForm) {
    attendanceForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const processingDiv = document.getElementById('processing');
        const resultsDiv = document.getElementById('results');
        
        processingDiv.style.display = 'block';
        resultsDiv.style.display = 'none';
        
        try {
            const response = await fetch('/api/process-video', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            processingDiv.style.display = 'none';
            
            if (result.success) {
                displayAttendanceResults(result);
            } else {
                alert('Error processing video: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            processingDiv.style.display = 'none';
            alert('Error: ' + error.message);
        }
    });
}

function displayAttendanceResults(data) {
    const resultsDiv = document.getElementById('results');
    const sessionIdSpan = document.getElementById('sessionId');
    const totalPresentSpan = document.getElementById('totalPresent');
    const tableBody = document.querySelector('#attendanceTable tbody');
    
    sessionIdSpan.textContent = data.session_id;
    totalPresentSpan.textContent = data.total_present;
    
    // Clear previous results
    tableBody.innerHTML = '';
    
    // Populate table
    data.attendance_list.forEach(record => {
        const row = tableBody.insertRow();
        row.innerHTML = `
            <td>${record.roll_number}</td>
            <td>${record.full_name}</td>
            <td>${new Date(record.marked_at).toLocaleString()}</td>
            <td>${(record.confidence * 100).toFixed(1)}%</td>
        `;
    });
    
    resultsDiv.style.display = 'block';
}