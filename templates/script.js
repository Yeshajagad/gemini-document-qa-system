const form = document.getElementById('queryForm');
const submitBtn = document.getElementById('submitBtn');
const originalBtnText = submitBtn.innerHTML;

form.addEventListener('submit', function () {
    submitBtn.innerHTML = '⏳ Processing...';
    submitBtn.disabled = true;
});

window.addEventListener('load', function () {
    submitBtn.innerHTML = originalBtnText;
    submitBtn.disabled = false;
});
