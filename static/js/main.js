(function() {
  "use strict";

    // code to handle user registration
    document.addEventListener('DOMContentLoaded', function() {
      const form = document.querySelector('form');
      const nameField = document.getElementById('name')
      const nameError = document.getElementById('nameError');
      const userField = document.getElementById('username');
      const userError = document.getElementById('usernameError');
      const emailField = document.getElementById('email');
      const passwordField = document.getElementById('password');
      const emailError = document.getElementById('emailError');
      const passwordError = document.getElementById('passwordError');
      const submitBtn = document.getElementById('submitBtn');
      let emailExistTimeout;

      form.addEventListener('submit', function(event) {
        if (!validateForm()) {
          event.preventDefault(); // prevent submitting the form
        }
      });

      emailField.addEventListener('input', function() {
        clearTimeout(emailExistTimeout);
        const email = emailField.value.trim();

        if (email === '') {
          emailField.classList.remove('is-invalid');
          emailError.textContent = '';
          submitBtn.disabled = false; // enable submit button
        } else {
          emailExistTimeout = setTimeout(function() {
            axios.post('/check_email', { email })
              .then(function(response) {
                if (response.data.exists) {
                  emailField.classList.add('is-invalid');
                  emailError.textContent = 'Email already exists!';
                  submitBtn.disabled = true; // disable submit button
                } else {
                  emailField.classList.remove('is-invalid');
                  emailError.textContent = '';
                  submitBtn.disabled = false; // enable submit button
                }
              })
              .catch(function(error) {
                console.error(error);
              });
          }, 250);
        }
      });

      function ValidateEmail(email) {
        // regular expression to validate emails
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
      }

      function validateForm() {
        let isValid = true;

        if (nameField.value.trim() === '') {
          nameField.classList.add('is-invalid');
          nameError.textContent = 'Please enter a valid name!';
          isValid = false;
        } else {
          nameField.classList.remove('is-invalid');
          nameError.textContent = '';
        }

        if (userField.value.trim() === '') {
          userField.classList.add('is-invalid');
          userError.textContent = 'Please enter a valid username!';
          isValid = false;
        } else {
          userField.classList.remove('is-invalid');
          userError.textContent = '';
        }

        if (emailField.value.trim() === '') {
          emailField.classList.add('is-invalid');
          emailError.textContent = 'Please enter a valid Email address!';
          isValid = false;
        } else if (!ValidateEmail(emailField.value)) {
          emailField.classList.add('is-invalid');
          emailError.textContent = 'Please enter a valid Email address!';
          isValid = false;
        } else if (emailField.classList.contains('is-invalid')) {
          isValid = false;
        } else {
          emailField.classList.remove('is-invalid');
          emailError.textContent = '';
        }

        if (passwordField.value.trim() === '') {
          passwordField.classList.add('is-invalid');
          passwordError.textContent = 'Please enter your password!';
          isValid = false;
        } else {
          passwordField.classList.remove('is-invalid');
          passwordError.textContent = '';
        }

        return isValid;
      }
    });


  document.addEventListener('DOMContentLoaded', function() {
    const passwordField = document.getElementById('password');
    const confirmationField = document.getElementById('confirmation');
    const confirmationError = document.getElementById('confirmationError');
    const submitBtn = document.getElementById('submitBtn');

    function validatePasswords() {
      if (passwordField.value !== confirmationField.value) {
        confirmationField.classList.add('is-invalid');
        confirmationError.textContent = 'Passwords must match!';
        submitBtn.disabled = true; // disable submit button
      } else {
        confirmationField.classList.remove('is-invalid');
        confirmationError.textContent = '';
        submitBtn.disabled = false; // enable submit button
      }
    }

    passwordField.addEventListener('input', validatePasswords);
    confirmationField.addEventListener('input', validatePasswords);
  });

  const select = (el, all = false) => {
    el = el.trim();
    if (all) {
      return [...document.querySelectorAll(el)];
    } else {
      return document.querySelector(el);
    }
  };

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    if (all) {
      select(el, all).forEach(e => e.addEventListener(type, listener));
    } else {
      select(el, all).addEventListener(type, listener);
    }
  };

  /**
   * Easy on scroll event listener
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener);
  };

  /**
   * Sidebar toggle
   */
  if (select('.toggle-sidebar-btn')) {
    on('click', '.toggle-sidebar-btn', function(e) {
      select('body').classList.toggle('toggle-sidebar');
    });
  }


  function updateHabitTimes() {
    // Get all <p> elements that display the elapsed time
    var habitTimeElements = document.querySelectorAll('[id^="habit-time-"]');

    // Iterate over each item and update the elapsed time for the corresponding habit
    habitTimeElements.forEach(function(element) {
      // Get the habit ID from the <p> element ID
      var habitId = element.id.split('-')[2];

      // Get the start date of the corresponding habit
      var startDateString = document.getElementById('habitStartDate-' + habitId).value;
      var startDate = new Date(startDateString);

      // Get current date
      var currentDate = new Date();

      // Calculate the difference in milliseconds between the current date and the start date
      var timeDiff = currentDate - startDate;

      // Calculate the days, hours, minutes and seconds elapsed
      var days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
      var hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      var minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
      var seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

      // Update the content of the <p> element with the elapsed time
      element.textContent =  days + " days " + hours + " hours " + minutes + " minutes " + seconds + " seconds";
    });
  }

  // Update the elapsed time every second
  setInterval(updateHabitTimes, 1000);

  // Get all buttons to show progress good habit
  var progressModalBtns = document.querySelectorAll('.display-progress-modal');

  // Handle the click event on each button
  progressModalBtns.forEach(function(progressModalBtn) {
    progressModalBtn.addEventListener('click', function() {
      var habitId = this.getAttribute('data-habit-id');

      // Make an AJAX request to get the data
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/get_progress_data/' + habitId);
      xhr.onload = function() {
        if (xhr.status === 200) {
          var data = JSON.parse(xhr.responseText);
          var habit = data.habit_data;
          var record = data.record_data;

          // Complete modal with the data
          document.getElementById('habitProgressModalLabel').textContent = habit.name;
          document.getElementById('currentStreak').textContent = record.current_streak + ' day/s';
          document.getElementById('completedDays').textContent = habit.completed_count + ' day/s';
          document.getElementById('failedDays').textContent = habit.failed_count + ' day/s';

          // Generate the URL with the name of the habit
          var habitName = habit.name
          var viewRecordsUrl = '/records?query=' + encodeURIComponent(habitName);

          // Assign the URL to the "View Records" button
          var viewRecordsBtn = document.getElementById('viewRecordsBtn');
          viewRecordsBtn.setAttribute("href", viewRecordsUrl)

          // Get the progress modal
          var progressModal = document.getElementById('habitProgressModal');

          // Open the progress modal
          var modalInstance = new bootstrap.Modal(progressModal);
          modalInstance.show();

          // Get all buttons to close the modal
          var closeButtons = progressModal.querySelectorAll('[data-bs-dismiss="modal"]');

          // Handle the click event for each button
          closeButtons.forEach(function(closeButton) {
            closeButton.addEventListener('click', function() {
              // Close modal
              modalInstance.hide();
            });
          });
        } else {
          alert('Este hábito no tiene ningún registro. Una vez que lo completes o falles, los datos aparecerán aquí.');
        }
      };
      xhr.send();
    });
  });


  // Get all buttons to show progress bad habit
  var badProgressModalBtns = document.querySelectorAll('.display-progress-modal-bad');

  // Handle the click event on each button
  badProgressModalBtns.forEach(function(badProgressModalBtn) {
    badProgressModalBtn.addEventListener('click', function() {
      var habitId = this.getAttribute('data-habit-id');

      // Make an AJAX request to get the data
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/get_progress_data/' + habitId);
      xhr.onload = function() {
        if (xhr.status === 200) {
          var data = JSON.parse(xhr.responseText);
          var habit = data.habit_data;
          var record = data.record_data;

          // Get habit start date
          var startDate = new Date(habit.start_date);

          // Get current date
          var currentDate = new Date();

          // Calculate the difference in milliseconds between the current date and the start date
          var timeDiff = currentDate - startDate;

          // Calculate the days, hours, minutes and seconds elapsed
          var days = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
          var hours = Math.floor((timeDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
          var minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
          var seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

          // Complete modal with the data
          document.getElementById('badHabitProgressModalLabel').textContent = habit.name;
          document.getElementById('badCurrentStreak').textContent = days + " days " + hours + " hours " + minutes + " minutes " + seconds + " seconds";
          document.getElementById('badFailedDays').textContent = habit.failed_count + ' day/s';

          // Generate the URL with the name of the habit
          var habitName = habit.name
          var viewRecordsUrl = '/records?query=' + encodeURIComponent(habitName);

          // Assign the URL to the "View Records" button
          var viewRecordsBtn = document.getElementById('viewRecordsBtnBad');
          viewRecordsBtn.setAttribute("href", viewRecordsUrl)

          // Open the progress modal
          var badProgressModal = new bootstrap.Modal(document.getElementById('badHabitProgressModal'));
          badProgressModal.show();

          var closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"]');
          closeButtons.forEach(function(closeButton) {
            closeButton.addEventListener('click', function() {
              // Close modal
              badProgressModal.hide();
            });
          });

        } else {
          alert('Este hábito no tiene ningún registro. Una vez que lo completes o falles, los datos aparecerán aquí.');
        }
      };
      xhr.send();
    });
  });

  // Get all plan edit buttons
  var editPlanBtns = document.querySelectorAll('.edit-plan-btn');

  // Handle click event for each button
  editPlanBtns.forEach(function(editPlanBtn) {
    editPlanBtn.addEventListener('click', function() {
      var planId = this.getAttribute('data-plan-id');

      // Make an AJAX request to get the data
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/get_plan/' + planId);
      xhr.onload = function() {
        if (xhr.status === 200) {
          var plan = JSON.parse(xhr.responseText);

          // Complete modal with the data
          document.getElementById('editPlanName').value = plan.name;
          document.getElementById('editPlanPrice').value = plan.value;
          document.getElementById('editDays').value = plan.duration;
          document.getElementById('editPlanDescription').value = plan.period;
          
          


          // Get form reference
          var form = document.getElementById('editPlanForm');

          // Update the 'action' attribute of the form
          form.action = '/edit_plan/' + planId;

          // Open edit plan modal
          var editPlanModal = new bootstrap.Modal(document.getElementById('editPlanModal'));
          editGoodplanModal.show();

          var closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"]');
          closeButtons.forEach(function(closeButton) {
            closeButton.addEventListener('click', function() {
              editPlanModal.hide();
            });
          });

        } else {
          alert('Error al obtener los datos del hábito');
        }

      };
      xhr.send();
    });
  });

  // Initialize all Pikaday calendars
  var picker = new Pikaday({
    field: document.getElementById('datepicker'),
    format: 'YYYY-MM-DD',
    minDate: new Date(),
    defaultDate: new Date()
  });

  var pickerEdit = new Pikaday({
    field: document.getElementById('datepickerEdit'),
    format: 'YYYY-MM-DD',
    minDate: new Date(),
    defaultDate: new Date()
  });

  var pickerBreak = new Pikaday({
    field: document.getElementById('datepickerBreak'),
    format: 'YYYY-MM-DD',
    minDate: new Date(),
    defaultDate: new Date()
  });

  var pickerBreak2 = new Pikaday({
    field: document.getElementById('datepickerBreak2'),
    format: 'YYYY-MM-DD',
    minDate: new Date(),
    defaultDate: new Date()
  });

  var currentDate = moment().format('ddd MMM DD YYYY'); // Get formated current date
  console.log(currentDate);
  document.getElementById('datepicker').setAttribute('placeholder', currentDate);
  document.getElementById('datepickerBreak').setAttribute('placeholder', currentDate);
  document.getElementById('datepickerBreak2').setAttribute('placeholder', currentDate);

  document.addEventListener("DOMContentLoaded", function() {
    // Get references to the "Remove" and "Limit" buttons
    var quitButton = document.querySelector("[data-habit-type='quit']");
    var limitButton = document.querySelector("[data-habit-type='limit']");

    // Get references to the "quitSection" and "limitSection" sections
    var quitSection = document.getElementById("quitSection");
    var limitSection = document.getElementById("limitSection");

    // Show "quitSection" and hide "limitSection" by default
    quitSection.classList.add("d-block");
    limitSection.classList.add("d-none");
    document.getElementById('habitTypeInput').value = 'quit';
    console.log("Valor de habitTypeInput:", document.getElementById("habitTypeInput").value);

    // Set button styles
    quitButton.classList.add("btn-light");
    quitButton.classList.add("active");
    limitButton.classList.add("btn-light");

    // Function to handle the "Quit" button click event
    quitButton.addEventListener("click", function() {
      // Show "quitSection" and hide "limitSection" when pressing the "Quit" button
      quitSection.classList.add("d-block");
      quitSection.classList.remove("d-none");
      limitSection.classList.add("d-none");
      limitSection.classList.remove("d-flex");

      // Assign 'quit' value to habitTypeInput
      document.getElementById('habitTypeInput').value = 'quit';
      console.log("Valor de habitTypeInput:", document.getElementById("habitTypeInput").value);
    });

    // Function to handle the "Limit" button click event
    limitButton.addEventListener("click", function() {
      // Show "limitSection" and hide "quitSection" when pressing the "Limit" button
      limitSection.classList.add("d-flex");
      limitSection.classList.remove("d-none");
      quitSection.classList.add("d-none");
      quitSection.classList.remove("d-block");

      // Assign 'limit' value to habitTypeInput


      document.getElementById('habitTypeInput').value = 'limit';
      console.log("Valor de habitTypeInput:", document.getElementById("habitTypeInput").value);
    });
  });

  // Initialize Flatpickr in the time input field
  flatpickr("#habitShowAt", {
    enableTime: true,
    noCalendar: true,
    dateFormat: "H:i",
    time_24hr: true
  });

  // Initialize Flatpickr in the time input field
  flatpickr("#editHabitShowAt", {
    enableTime: true,
    noCalendar: true,
    dateFormat: "H:i",
    time_24hr: true
  });

})();
