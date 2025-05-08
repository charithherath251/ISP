(function () {
    let userActivity = {
        mouseMoves: 0,
        keypresses: 0,
        scrolls: 0,
        clicks: 0,
        timing: [],
        startTime: Date.now()
    };

    document.addEventListener('mousemove', () => userActivity.mouseMoves++);
    document.addEventListener('keydown', () => userActivity.keypresses++);
    document.addEventListener('scroll', () => userActivity.scrolls++);
    document.addEventListener('click', () => userActivity.clicks++);

    document.addEventListener('DOMContentLoaded', () => {
        const form = document.getElementById('loginForm');
        if (!form) return;

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            userActivity.timing.push(Date.now() - userActivity.startTime);

            fetch('http://127.0.0.1:8000/validate-user', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userActivity)
            })
                .then(res => res.json())
                .then(data => {
                    if (!data.success) {
                        alert("Bot detected! Login blocked.\n" + data.reasons.join(", "));
                        window.location.href = "/ISP/index.html";
                    } else {
                        alert("User verified. Login allowed.");
                        form.submit(); // Simulate real login
                    }
                })
                .catch(err => {
                    console.error("Error:", err);
                    alert("Validation failed. Please try again.");
                });
        });
    });
})();
