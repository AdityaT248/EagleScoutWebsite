document.addEventListener("DOMContentLoaded", function() {
    const availabilityForm = document.getElementById("availability-form");
    const commentForm = document.getElementById("comment-form");
    const commentsSection = document.getElementById("comments-section");

    if (availabilityForm) {
        availabilityForm.addEventListener("submit", async function(event) {
            event.preventDefault();
            const date = document.getElementById("availability-date").value;
            const available = document.querySelector('input[name="availability"]:checked').value === "true";

            const response = await fetch(`/set_availability/${date}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ available })
            });

            const result = await response.json();
            alert(result.message);
        });
    }

    if (commentForm) {
        commentForm.addEventListener("submit", async function(event) {
            event.preventDefault();
            const comment = document.getElementById("comment-text").value;

            const response = await fetch("/comment/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({ comment })
            });

            const result = await response.json();
            alert(result.message);
            loadComments();
        });
    }

    async function loadComments() {
        const response = await fetch("/comments/");
        const result = await response.json();
        commentsSection.innerHTML = "";
        result.comments.forEach(comment => {
            const commentElement = document.createElement("p");
            commentElement.textContent = comment;
            commentsSection.appendChild(commentElement);
        });
    }

    loadComments();
});