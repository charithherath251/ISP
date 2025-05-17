  
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

  
  //Scrolls
  window.addEventListener('scroll', () => {
      userActivity.scrolls++;
      userActivity.scrollEvents.push({ timestamp: Date.now(), scrollY: window.scrollY });
  });

    //mouseClicks
  document.addEventListener('click', () => userActivity.clicks++);

  // Send data every 30 seconds
      setInterval(() => {
        userActivity.timing.push(Date.now() - userActivity.startTime);
    
        fetch("http://localhost:8000/validate-session", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(userActivity)
        })
        .then(res => res.json())
        .then(result => {
          if (!result.success) {
            alert("⚠️ Abnormal behavior detected during session.");
            
            // End simulated session
              localStorage.removeItem("sessionActive");
            window.location.href = "index.html";
  
          }
          // Reset counters
          userActivity = {
            mouseMoves: 0,
            keypresses: 0,
            scrolls: 0,
            clicks: 0,
            mouseMovements: [],
            scrollEvents: [],
            keystrokeTimings: [],
            startTime: Date.now(),
            timing: []
          };
        });
      }, 30000); // 30 sec
    
    })();