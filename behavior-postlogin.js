(function () {
    let behaviorData = {
      mouseMoves: 0,
      keypresses: 0,
      scrolls: 0,
      clicks: 0,
      sessionStart: Date.now(),
      timing: []
    };
  
    document.addEventListener("mousemove", () => behaviorData.mouseMoves++);
    document.addEventListener("keydown", () => behaviorData.keypresses++);
    document.addEventListener("scroll", () => behaviorData.scrolls++);
    document.addEventListener("click", () => behaviorData.clicks++);
  
    // Send data every 30 seconds
    setInterval(() => {
      behaviorData.timing.push(Date.now() - behaviorData.sessionStart);
  
      fetch("http://127.0.0.1:8000/validate-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(behaviorData)
      })
      .then(res => res.json())
      .then(result => {
        if (!result.success) {
          alert("⚠️ Abnormal behavior detected during session.");
          // Optional: Logout user, lock session, etc.
          window.location.href = "index.html";

        }
        // Reset counters
        behaviorData = {
          mouseMoves: 0,
          keypresses: 0,
          scrolls: 0,
          clicks: 0,
          sessionStart: Date.now(),
          timing: []
        };
      });
    }, 30000); // 30 sec
  
  })();
  