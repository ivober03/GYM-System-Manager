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
        document.getElementById('editPlanPrice').value = plan.price;
        document.getElementById('editDays').value = plan.days;
        document.getElementById('editPlanDescription').value = plan.description;

        // Get form reference
        var form = document.getElementById('editPlanForm');

        // Update the 'action' attribute of the form
        form.action = '/edit_plan/' + planId;

        // Open edit plan modal
        var editPlanModal = new bootstrap.Modal(document.getElementById('editPlanModal'));
        editPlanModal.show();

        var closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(function(closeButton) {
          closeButton.addEventListener('click', function() {
            editPlanModal.hide();
          });
        });

      } else {
        alert('Error al obtener los datos del plan');
      }

    };
    xhr.send();
  });
});

// Get all member buttons
var editMemberBtns = document.querySelectorAll('.edit-member-btn');

// Handle click event for each button
editMemberBtns.forEach(function(editMemberBtn) {
  editMemberBtn.addEventListener('click', function() {
    var memberId = this.getAttribute('data-member-id');

    // Make an AJAX request to get the data
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get_member/' + memberId);
    xhr.onload = function() {
      if (xhr.status === 200) {
        var member = JSON.parse(xhr.responseText);

        // Complete modal with the data
        document.getElementById('editMemberName').value = member.name;
        document.getElementById('editMemberPlan').value = member.plan_id;


        // Get form reference
        var form = document.getElementById('editPlanForm');

        // Update the 'action' attribute of the form
        form.action = '/edit_plan/' + planId;

        // Open edit plan modal
        var editPlanModal = new bootstrap.Modal(document.getElementById('editPlanModal'));
        editPlanModal.show();

        var closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(function(closeButton) {
          closeButton.addEventListener('click', function() {
            editPlanModal.hide();
          });
        });

      } else {
        alert('Error al obtener los datos del plan');
      }

    };
    xhr.send();
  });
});

  var currentDate = moment().format('ddd MMM DD YYYY'); // Get formated current date
  console.log(currentDate);
  document.getElementById('datepicker').setAttribute('placeholder', currentDate);
  document.getElementById('datepickerBreak').setAttribute('placeholder', currentDate);
  document.getElementById('datepickerBreak2').setAttribute('placeholder', currentDate);

})();
