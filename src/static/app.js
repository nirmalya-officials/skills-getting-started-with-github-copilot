document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message and dropdown
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Participants:</strong>
            <ul class="participants-list" id="participants-${encodeURIComponent(name)}">
            </ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);
        
        // Populate participants list with delete buttons
        const participantsList = document.getElementById(`participants-${encodeURIComponent(name)}`);
        if (details.participants.length > 0) {
          details.participants.forEach(participant => {
            const li = document.createElement("li");
            li.className = "participant-item";
            li.innerHTML = `
              <span>${participant}</span>
              <button class="delete-btn" title="Unregister the participant" data-activity="${name}" data-email="${participant}">
                🗑️
              </button>
            `;
            participantsList.appendChild(li);
          });
        } else {
          const li = document.createElement("li");
          li.innerHTML = "<em>No participants yet</em>";
          participantsList.appendChild(li);
        }

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
      
      // Add event listeners to delete buttons
      document.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", handleDeleteParticipant);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }
  
  // Handle participant deletion
  async function handleDeleteParticipant(event) {
    event.preventDefault();
    const btn = event.target.closest(".delete-btn");
    const activity = btn.getAttribute("data-activity");
    const email = btn.getAttribute("data-email");
    
    if (!confirm(`Remove ${email} from ${activity}?`)) {
      return;
    }
    
    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/participants/${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );
      
      const result = await response.json();
      
      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");
        
        // Refresh activities list
        fetchActivities();
        
        // Hide message after 5 seconds
        setTimeout(() => {
          messageDiv.classList.add("hidden");
        }, 5000);
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      messageDiv.textContent = "Failed to remove participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error removing participant:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Refresh activities list
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
