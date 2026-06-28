const userList = document.getElementById("user-list");
const message = document.getElementById("message");

// Show success/error message
function showMessage(text, type) {
    message.style.display = "block";
    message.className = type;
    message.textContent = text;

    setTimeout(() => {
        message.style.display = "none";
        message.className = "";
        message.textContent = "";
    }, 3000);
}

// Load all users
async function loadUsers() {
    try {
        const response = await fetch("/users");

        if (!response.ok) {
            throw new Error("Failed to load users.");
        }

        const users = await response.json();

        userList.innerHTML = "";

        users.forEach(user => {

            const card = document.createElement("div");
            card.className = "user-card";

            card.innerHTML = `
                <div>
                    <div class="user-name">${user.name}</div>

                    <div class="status ${user.available ? "available" : "unavailable"}">
                        ${user.available ? "🟢 Available" : "🔴 Unavailable"}
                    </div>
                </div>

                <input
                    type="checkbox"
                    class="switch"
                    ${user.available ? "checked" : ""}
                >
            `;

            const toggle = card.querySelector(".switch");
            const status = card.querySelector(".status");

            toggle.addEventListener("change", async () => {

                const available = toggle.checked;

                try {

                    const response = await fetch(`/users/${user.id}`, {
                        method: "PUT",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            available: available
                        })
                    });

                    const result = await response.json();

                    if (!response.ok) {
                        throw new Error(result.message);
                    }

                    status.textContent = result.available
                        ? "🟢 Available"
                        : "🔴 Unavailable";

                    status.className = result.available
                        ? "status available"
                        : "status unavailable";

                    showMessage(
                        "Availability updated successfully.",
                        "success"
                    );

                } catch (error) {

                    // Restore previous toggle state
                    toggle.checked = !available;

                    showMessage(
                        error.message || "Failed to update availability.",
                        "error"
                    );
                }

            });

            userList.appendChild(card);
        });

    } catch (error) {
        showMessage(error.message, "error");
    }
}

// Initial load
loadUsers();
