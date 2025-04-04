// document.addEventListener("DOMContentLoaded", function () {
//     const form = document.querySelector("#history-form");
//     const resultContainer = document.querySelector("#history-results");
  
//     form.addEventListener("submit", async function (event) {
//       event.preventDefault();
//       const patientUID = document.querySelector("#patient_uid").value.trim();
  
//       if (!patientUID) {
//         alert("Please enter a valid Patient UID.");
//         return;
//       }
  
//       resultContainer.innerHTML = `<div class="text-sm text-gray-400 animate-pulse">Loading history...</div>`;
  
//       try {
//         const response = await fetch(`/api/view-history/${patientUID}`);
//         if (!response.ok) throw new Error("No history found for this UID.");
  
//         const data = await response.json();
//         displayHistory(data);
//       } catch (error) {
//         resultContainer.innerHTML = `<p class="text-red-500">${error.message}</p>`;
//       }
//     });
  
//     function displayHistory(data) {
//       if (!data.records || data.records.length === 0) {
//         resultContainer.innerHTML = "<p>No history found for this patient.</p>";
//         return;
//       }
  
//       let html = `
//         <div class="mt-6 space-y-4">
//           <div class="text-sm text-muted mb-4">
//             <p><span class="font-semibold">Name:</span> ${data.patient_name}</p>
//             <p><span class="font-semibold">UID:</span> ${data.patient_uid}</p>
//           </div>`;
  
//       data.records.forEach((record) => {
//         html += `
//           <div class="bg-muted rounded-xl p-4">
//             <h3 class="font-semibold mb-2">🗓️ ${record.scan_date}</h3>
//             <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">`;
  
//         record.segmented_images.forEach((image) => {
//           html += `
//             <div class="bg-background border border-border p-3 rounded-xl shadow">
//               <img src="/static/${image}" alt="Segmented Scan" class="rounded-xl mb-2"/>
//               <p class="text-xs mb-1">${record.name}, ${record.age}, ${record.gender}</p>
//               <a href="/static/${image}" download class="text-blue-400 hover:underline text-sm">Download</a>
//             </div>`;
//         });
  
//         html += `</div></div>`;
//       });
  
//       html += `</div>`;
//       resultContainer.innerHTML = html;
//     }
//   });
  


document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("#history-form");
    const resultContainer = document.querySelector("#history-results");
  
    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      const patientUID = document.querySelector("#patient_uid").value.trim();
  
      if (!patientUID) {
        alert("Please enter a valid Patient UID.");
        return;
      }
  
      resultContainer.innerHTML = <div class="text-sm text-gray-400 animate-pulse">Loading history...</div>;
  
      try {
        const response = await fetch(/api/view-history/${patientUID});
        if (!response.ok) throw new Error("No history found for this UID.");
  
        const data = await response.json();
        displayHistory(data);
      } catch (error) {
        resultContainer.innerHTML = <p class="text-red-500">${error.message}</p>;
      }
    });
  
    function displayHistory(data) {
      if (!data.records || data.records.length === 0) {
        resultContainer.innerHTML = "<p>No history found for this patient.</p>";
        return;
      }
  
      let html = `
        <div class="mt-6 space-y-4">
          <div class="text-sm text-muted mb-4">
            <p><span class="font-semibold">Name:</span> ${data.patient_name}</p>
            <p><span class="font-semibold">UID:</span> ${data.patient_uid}</p>
          </div>`;
  
      data.records.forEach((record) => {
        html += `
          <div class="bg-muted rounded-xl p-4">
            <h3 class="font-semibold mb-2">🗓 ${record.scan_date}</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">`;
  
        record.segmented_images.forEach((image) => {
          html += `
            <div class="bg-background border border-border p-3 rounded-xl shadow">
              <img src="/static/${image}" alt="Segmented Scan" class="rounded-xl mb-2"/>
              <p class="text-xs mb-1">${record.name}, ${record.age}, ${record.gender}</p>
              <a href="/static/${image}" download class="text-blue-400 hover:underline text-sm">Download</a>
            </div>`;
        });
  
        html += </div></div>;
      });
  
      html += </div>;
      resultContainer.innerHTML = html;
    }
  });