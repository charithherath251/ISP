// (function () {
//     let behaviorData = {
//       mouseMoves: 0,
//       keypresses: 0,
//       scrolls: 0,
//       clicks: 0,
//       sessionStart: Date.now(),
//       timing: []
//     };
  
//     document.addEventListener("mousemove", () => behaviorData.mouseMoves++);
//     document.addEventListener("keydown", () => behaviorData.keypresses++);
//     document.addEventListener("scroll", () => behaviorData.scrolls++);
//     document.addEventListener("click", () => behaviorData.clicks++);
  
//     // Send data every 30 seconds
//     setInterval(() => {
//       behaviorData.timing.push(Date.now() - behaviorData.sessionStart);
  
//       fetch("http://127.0.0.1:8000/validate-session", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify(behaviorData)
//       })
//       .then(res => res.json())
//       .then(result => {
//         if (!result.success) {
//           alert("⚠️ Abnormal behavior detected during session.");
          
//           // End simulated session
//             localStorage.removeItem("sessionActive");
//           window.location.href = "index.html";

//         }
//         // Reset counters
//         behaviorData = {
//           mouseMoves: 0,
//           keypresses: 0,
//           scrolls: 0,
//           clicks: 0,
//           sessionStart: Date.now(),
//           timing: []
//         };
//       });
//     }, 30000); // 30 sec
  
//   })();
  
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

  //Keypress
  // document.addEventListener('keydown', () => {
  //     userActivity.keypresses++;
  //     const currentTime = Date.now();
  //     if (lastKeyTime !== null) {
  //         userActivity.keystrokeTimings.push(currentTime - lastKeyTime);
  //     }
  //     lastKeyTime = currentTime;
  // });
  // const currentTime = Date.now();
  // if (userActivity.lastKeyTime !== null) {
  //     userActivity.keystrokeTimings.push(currentTime - userActivity.lastKeyTime);
  // }
  // userActivity.lastKeyTime = currentTime;
  
  //Scrolls
  window.addEventListener('scroll', () => {
      userActivity.scrolls++;
      userActivity.scrollEvents.push({ timestamp: Date.now(), scrollY: window.scrollY });
  });

  document.addEventListener('click', () => userActivity.clicks++);

  // Send data every 30 seconds
      setInterval(() => {
        userActivity.timing.push(Date.now() - userActivity.startTime);
    
        fetch("http://127.0.0.1:8000/validate-session", {
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
      }, 10000); // 30 sec
    
    })();