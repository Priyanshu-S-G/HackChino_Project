document.addEventListener('DOMContentLoaded', function() {
    const historyForm = document.getElementById('historySearchForm');
    const historyResults = document.getElementById('historyResults');

    historyForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const patientUID = document.getElementById('patientUID').value;
        
        // Show loading state
        historyResults.innerHTML = '<p style="color: white; text-align: center;">Loading...</p>';
        historyResults.classList.remove('hidden');

        // Simulate API call with setTimeout
        setTimeout(() => {
            // Mock data - replace with actual API call
            const mockData = {
                patientName: "John Doe",
                scans: [
                    {
                        date: "2024-01-15",
                        scanType: "MRI Brain",
                        result: "Tumor detected",
                        doctor: "Dr. Smith"
                    },
                    {
                        date: "2023-12-20",
                        scanType: "MRI Brain",
                        result: "Initial scan",
                        doctor: "Dr. Johnson"
                    }
                ]
            };

            displayResults(mockData);
        }, 1000);
    });

    function displayResults(data) {
        let html = `
            <h2 style="color: white; margin-bottom: 1rem;">Patient: ${data.patientName}</h2>
        `;

        data.scans.forEach(scan => {
            html += `
                <div class="scan-record">
                    <h3>Scan Date: ${scan.date}</h3>
                    <div class="scan-details">
                        <p><strong>Scan Type:</strong> ${scan.scanType}</p>
                        <p><strong>Result:</strong> ${scan.result}</p>
                        <p><strong>Doctor:</strong> ${scan.doctor}</p>
                    </div>
                </div>
            `;
        });

        historyResults.innerHTML = html;
    }
});