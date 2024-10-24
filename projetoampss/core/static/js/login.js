document.addEventListener('DOMContentLoaded', () => {
    const pwShowHide = document.querySelectorAll(".showHidePw"),
          pwFields = document.querySelectorAll("input[type='password']");

    pwShowHide.forEach(eyeIcon => {
        eyeIcon.addEventListener("click", () => {
            pwFields.forEach(pwField => {
                if (pwField.type === "password") {
                    pwField.type = "text";
                    eyeIcon.classList.replace("uil-eye-slash", "uil-eye");
                } else {
                    pwField.type = "password";
                    eyeIcon.classList.replace("uil-eye", "uil-eye-slash");
                }
            });
        });
    });
});
