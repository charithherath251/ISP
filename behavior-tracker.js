(function () {
    let userActivity = {
        mouseMoves: 0,
        keypresses: 0,
        scrolls: 0,
        clicks: 0,
        mouseMovements: [],
        scrollEvents: [],
        keystrokeTimings: [],
        timing: [],
        startTime: Date.now(),
        lastMouseX: null,
        lastMouseY: null,
        lastKeyTime: null
    };

    // MouseMovement
    document.addEventListener('mousemove', (event) => {
        userActivity.mouseMoves++;

        if (userActivity.lastMouseX !== null && userActivity.lastMouseY !== null) {
            const dx = Math.abs(userActivity.lastMouseX - event.clientX);
            const dy = Math.abs(userActivity.lastMouseY - event.clientY);
            userActivity.mouseMovements.push({ x: dx, y: dy, timestamp: Date.now() });
        }

        userActivity.lastMouseX = event.clientX;
        userActivity.lastMouseY = event.clientY;
    });

 
    document.addEventListener('keydown', () => {
        userActivity.keypresses++; // Count total keypresses
    
        const currentTime = Date.now(); // Time of current keypress
    
        if (userActivity.lastKeyTime !== null) {
            const interval = currentTime - userActivity.lastKeyTime;
            userActivity.keystrokeTimings.push(interval); // Time between keypresses
        }
    
        userActivity.lastKeyTime = currentTime; // Update for next key
    });
    
    
    //Scrolls
    window.addEventListener('scroll', () => {
        userActivity.scrolls++;
        userActivity.scrollEvents.push({ timestamp: Date.now(), scrollY: window.scrollY });
    });

    document.addEventListener('click', () => userActivity.clicks++);

    document.addEventListener('DOMContentLoaded', () => {
        const form = document.getElementById('loginForm');
        if (!form) return;

        form.addEventListener('submit', function (e) {
            e.preventDefault();
            userActivity.timing.push(Date.now() - userActivity.startTime);
            console.log(JSON.stringify(userActivity));
            // console.log("Payload being sent:", JSON.stringify(userActivity, null, 2));

            fetch('http://localhost:8000/validate-user', {
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
